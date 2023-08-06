"""
Usage:
  batch_scoring [--host=<host>] [--user=<user>]
                [--password=<pwd>] [--api_token=<api_token>]
                [--datarobot_key=<datarobot_key>] [--verbose]
                [--n_samples=<n_samples>] [--n_retry=<n_retry>]
                [--n_concurrent=<n_concurrent>]
                [--out=<out>]
                [--api_version=<api_version>]
                [--pred_name=<pred_name>]
                [--create_api_token] [--keep_cols=<keep_cols>]
                [--delimiter=<delimiter>] [--timeout=<timeout>] [--version]
                <project_id> <model_id> <dataset> [--resume|--cancel]
  batch_scoring -h | --help
  batch_scoring --version

Batch score ``dataset`` by submitting prediction requests against ``host``
using model ``model_id``. It will send batches of size ``n_samples``.
Set ``n_samples`` such that the round-trip is roughly 10sec (see verbose output).
Set ``n_concurrent`` to match the number of cores in the prediction API endpoint.

The dataset has to be a single CSV file that can be gzipped (extension '.gz').
The output ``out`` will be a single CSV files but remember that records might be
unordered.

Arguments:
  --host=<host>    The host to test [default: https://beta.datarobot.com/api].
  --api_version=<api_version>    The API version [default: v1]
  --datarobot_key=<datarobot_key>   An additional datarobot_key for dedicated prediction instances.
  --user=<user>  The username to acquire the api-token; if none prompt.
  --password=<pwd>  The password to acquire the api-token; if none prompt.
  --n_samples=<n_samples>  The number of samples per batch [default: 1000].
  --n_retry=<n_retry>  The number of retries if a request failed; -1 means infinite [default: 3].
  --n_concurrent=<n_concurrent>  The number of concurrent requests to submit [default: 4].
  --api_token=<api_token>  The api token for the requests; if none use <pwd> to get token.
  --out=<out>  The file to which the results should be written [default: out.csv].
  --keep_cols=<keep_cols>  A comma separated list of column names to append to the predictions.
  --delimiter=<delimiter>  Delimiter to use. If empty, will try to automatically determine this [default: ,].
  --timeout=<timeout>  The timeout for each post request [default: 30].

Options:
  -h --help
  --version  Show version
  -v --verbose  Verbose output
  -c --create_api_token  If set we will request a new api token.
  -r --resume   Resume a checkpointed run.
  -c --cancel   Cancel a checkpointed run.

Example:

  batch_scoring --host https://beta.datarobot.com/api --user="<username>" --password="<password>" 5545eb20b4912911244d4835 5545eb71b4912911244d4847 ~/Downloads/diabetes_test.csv

"""

from __future__ import print_function

import collections
import copy
import getpass
import glob
import gzip
import json
import logging
import os
import shelve
import sys
import tempfile
import threading
import warnings
from functools import partial
from time import time

import pandas as pd
import requests
import six
from docopt import docopt

from . import __version__

if six.PY2:
    from . import grequests
    input = raw_input
if six.PY3:
    from . import arequests
    from builtins import input


class ShelveError(Exception):
    pass


Batch = collections.namedtuple('Batch', 'id, df, rty_cnt')


class TargetType(object):
    REGRESSION = 'Regression'
    BINARY = 'Binary'


FakeResponse = collections.namedtuple('FakeResponse', 'status_code, text')


VALID_DELIMITERS = {';', ',', '|', '\t', ' ', '!', '  '}


logger = logging.getLogger('main')
root_logger = logging.getLogger()

with tempfile.NamedTemporaryFile(prefix='datarobot_batch_scoring_',
                                 suffix='.log', delete=False) as fd:
    pass
root_logger_filename = fd.name


def configure_logging(level):
    """Configures logging for user and debug logging. """
    # user logger
    fs = '[%(levelname)s] %(message)s'
    hdlr = logging.StreamHandler()
    dfs = None
    fmt = logging.Formatter(fs, dfs)
    hdlr.setFormatter(fmt)
    logger.setLevel(level)
    logger.addHandler(hdlr)

    # root logger
    fs = '%(asctime)-15s [%(levelname)s] %(message)s'
    hdlr = logging.FileHandler(root_logger_filename, 'w+')
    dfs = None
    fmt = logging.Formatter(fs, dfs)
    hdlr.setFormatter(fmt)
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(hdlr)


def error(msg, exit=True):
    if exit:
        msg = ('{}\nIf you need assistance please send the log \n'
               'file {} to support@datarobot.com .').format(
                   msg, root_logger_filename)
    logger.error(msg)
    if sys.exc_info()[0]:
        exc_info = True
    else:
        exc_info = False
    root_logger.error(msg, exc_info=exc_info)
    if exit:
        sys.exit(1)


def acquire_api_token(base_url, base_headers, user, pwd, create_api_token):
    """Get the api token.

    Either supplied by user or requested from the API with username and pwd.
    Optionally, create a new one.
    """

    auth = (user, pwd)

    request_meth = requests.get
    if create_api_token:
        request_meth = requests.post

    r = request_meth(base_url + 'api_token', auth=auth, headers=base_headers)
    if r.status_code == 401:
        raise ValueError('wrong credentials')
    elif r.status_code != 200:
        raise ValueError('api_token request returned status code {}'
                         .format(r.status_code))
    else:
        logger.info('api-token acquired')

    api_token = r.json()['api_token']

    if api_token is None:
        raise ValueError('no api-token registered; '
                         'please run with --create_api_token flag.')

    logger.debug('api-token: {}'.format(api_token))

    return api_token


def verify_objectid(id_):
    """Verify if id_ is a proper ObjectId. """
    if not len(id_) == 24:
        raise ValueError('id {} not a valid project/model id'.format(id_))


class BatchGenerator(object):
    """Class to chunk a large csv files into a stream
    of batches of size ``--n_samples``.

    Yields
    ------
    batch : Batch
        The next batch
    """

    def __init__(self, dataset, n_samples, n_retry, delimiter):
        self.dataset = dataset
        self.chunksize = n_samples
        self.rty_cnt = n_retry
        self.sep = delimiter

    def __iter__(self):
        compression = None
        if self.dataset.endswith('.gz'):
            logger.debug('using gzip compression')
            compression = 'gzip'
        rows_read = 0
        sep = self.sep

        engine = 'c'
        engine_params = {'error_bad_lines': False,
                         'warn_bad_lines': True}

        if not sep:
            sep = None
            engine = 'python'
            engine_params = {}
            logger.warning('Guessing delimiter will result in slower parsing.')

        # handle unix tabs
        # NOTE: on bash you have to use Ctrl-V + TAB
        if sep == '\\t':
            sep = '\t'

        def _file_handle(fname):
            root_logger.debug('Opening file name {}.'.format(fname))
            return gzip.open(fname) if compression == 'gzip' else open(fname)

        if sep is not None:
            if sep not in VALID_DELIMITERS:
                raise ValueError('Delimiter "{}" is not a valid delimiter.'
                                 .format(sep))

            # if fixed sep check if we have at least one occurrence.
            with _file_handle(self.dataset) as fd:
                header = fd.readline()
                if not header.strip():
                    raise ValueError("Input file '{}' is empty."
                                     .format(self.dataset))
                if len(header.split(sep)) == 1:
                    raise ValueError(
                        ("Delimiter '{}' not found. "
                         "Please check your input file "
                         "or consider the flag `--delimiter=''`.").format(sep))

        # TODO for some reason c parser bombs on python 3.4 wo latin1
        batches = pd.read_csv(self.dataset, encoding='latin-1',
                              sep=sep,
                              iterator=True,
                              chunksize=self.chunksize,
                              compression=compression,
                              engine=engine,
                              **engine_params
                              )
        i = -1
        for i, chunk in enumerate(batches):
            if chunk.shape[0] == 0:
                raise ValueError(
                    "Input file '{}' is empty.".format(self.dataset))
            if i == 0:
                root_logger.debug('input columns: %r', chunk.columns.tolist())
                root_logger.debug('input dtypes: %r', chunk.dtypes)
                root_logger.debug('input head: %r', chunk.head(2))

            # strip white spaces
            chunk.columns = [c.strip() for c in chunk.columns]
            yield Batch(rows_read, chunk, self.rty_cnt)
            rows_read += self.chunksize

        if i == -1:
            raise ValueError("Input file '{}' is empty.".format(self.dataset))


def peek_row(dataset, delimiter):
    """Peeks at the first row in `dataset`. """
    batches = BatchGenerator(dataset, 1, 1, delimiter)
    try:
        row = next(iter(batches))
    except StopIteration:
        raise ValueError('Cannot peek first row from {}'.format(dataset))
    return row.df


class GeneratorBackedQueue(object):
    """A queue that is backed by a generator.

    When the queue is exhausted it repopulates from the generator.
    """

    def __init__(self, gen):
        self.gen = gen
        self.n_consumed = 0
        self.deque = collections.deque()
        self.lock = threading.RLock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            if len(self.deque):
                return self.deque.popleft()
            else:
                out = next(self.gen)
                self.n_consumed += 1
                return out

    def next(self):
        return self.__next__()

    def push(self, batch):
        # we retry a batch - decrement retry counter
        with self.lock:
            batch = batch._replace(rty_cnt=batch.rty_cnt - 1)
            self.deque.append(batch)

    def has_next(self):
        with self.lock:
            try:
                item = self.next()
                self.push(item)
                return True
            except StopIteration:
                return False


def dataframe_from_predictions(result, pred_name):
    """Convert DR prediction api v1 into dataframe.

    Returns
    -------
    pred : DataFrame
         A dataframe that holds one prediction per row;
         as many columns as class labels.
         Class labels are ordered in lexical order (asc).
    """
    predictions = result['predictions']
    if result['task'] == TargetType.BINARY:
        pred = pd.DataFrame([p['class_probabilities'] for p in
                             sorted(predictions, key=lambda p: p['row_id'])])
        sorted_classes = pd.np.unique(pred.columns.tolist())
        pred = pred[sorted_classes]
    elif result['task'] == TargetType.REGRESSION:
        pred = pd.DataFrame({pred_name: [p["prediction"] for p in
                             sorted(predictions, key=lambda p: p['row_id'])]})
    else:
        ValueError('task {} not supported'.format(result['task']))

    return pred


def process_successful_request(result, batch, ctx, pred_name):
    """Process a successful request. """
    pred = dataframe_from_predictions(result, pred_name)
    if pred.shape[0] != batch.df.shape[0]:
        raise ValueError('Shape mismatch {}!={}'.format(
            pred.shape[0], batch.df.shape[0]))
    # offset index by batch.id
    pred.index = batch.df.index + batch.id
    pred.index.name = 'row_id'
    ctx.checkpoint_batch(batch, pred)


class WorkUnitGenerator(object):
    """Generates async requests with completion or retry callbacks.

    It uses a queue backed by a batch generator.
    It will pop items for the queue and if its exhausted it will populate the
    queue from the batch generator.
    If a submitted async request was not successfull it gets enqueued again.
    """

    def __init__(self, batches, endpoint, headers, user, api_token,
                 ctx, pred_name, timeout):
        self.endpoint = endpoint
        self.headers = headers
        self.user = user
        self.api_token = api_token
        self.ctx = ctx
        self.queue = GeneratorBackedQueue(batches)
        self.pred_name = pred_name
        self.timeout = timeout

    def _response_callback(self, r, batch=None, *args, **kw):
        try:
            if r.status_code == 200:
                try:
                    result = r.json()
                    exec_time = result['execution_time']
                    logger.debug(('successful response: exec time {:.0f}msec |'
                                  ' round-trip: {:.0f}msec').format(
                                      exec_time,
                                      r.elapsed.total_seconds() * 1000))

                    process_successful_request(result, batch,
                                               self.ctx, self.pred_name)
                except Exception as e:
                    logger.warn('{} response error: {} -- retry'
                                .format(batch.id, e))
                    self.queue.push(batch)
            else:
                try:
                    logger.warn('batch {} failed with status: {}'
                                .format(batch.id,
                                        json.loads(r.text)['status']))
                except ValueError:
                    logger.warn('batch {} failed with status code: {}'
                                .format(batch.id, r.status_code))

                text = r.text
                root_logger.error('batch {} failed status_code:{} text:{}'
                                  .format(batch.id,
                                          r.status_code,
                                          text))
                self.queue.push(batch)
        except Exception as e:
            logger.fatal('batch {} - dropping due to: {}'
                         .format(batch.id, e), exc_info=True)

    def has_next(self):
        return self.queue.has_next()

    def __iter__(self):
        for batch in self.queue:
            # if we exhaused our retries we drop the batch
            if batch.rty_cnt == 0:
                logger.error('batch {} exceeded retry limit; '
                             'we lost {} records'.format(
                                 batch.id, batch.df.shape[0]))
                continue
            # otherwise we make an async request
            data = batch.df.to_csv(encoding='utf8', index=False)
            logger.debug('batch {} transmitting {} bytes'
                         .format(batch.id, len(data)))
            if six.PY2:
                yield grequests.AsyncRequest(
                    'POST', self.endpoint,
                    headers=self.headers,
                    timeout=self.timeout,
                    data=data,
                    auth=(self.user, self.api_token),
                    callback=partial(self._response_callback,
                                     batch=batch))
            elif six.PY3:
                yield ({'method': 'POST', 'url': self.endpoint,
                        'headers': self.headers, 'data': data,
                        'auth': (self.user, self.api_token),
                        'timeout': self.timeout},
                       partial(self._response_callback,
                               batch=batch))


class RunContext(object):
    """A context for a run backed by a persistant store.

    We use a shelve to store the state of the run including
    a journal of processed batches that have been checkpointed.

    Note: we use globs for the shelve files because different
    versions of Python have different file layouts.
    """
    FILENAME = '.shelve'

    def __init__(self, n_samples, out_file, pid, lid, keep_cols,
                 n_retry, delimiter, dataset, pred_name):
        self.n_samples = n_samples
        self.out_file = out_file
        self.project_id = pid
        self.model_id = lid
        self.keep_cols = keep_cols
        self.n_retry = n_retry
        self.delimiter = delimiter
        self.dataset = dataset
        self.pred_name = pred_name
        self.out_stream = None
        self.lock = threading.Lock()

    def __enter__(self):
        self.db = shelve.open(self.FILENAME, writeback=True)
        self.partitions = []
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()
        if self.out_stream is not None:
            self.out_stream.close()
        if type is None:
            # success - remove shelve
            self.clean()

    def checkpoint_batch(self, batch, pred):
        if self.keep_cols and self.first_write:
            mask = [c in batch.df.columns for c in self.keep_cols]
            if not all(mask):
                error('keep_cols "{}" not in columns {}.'.format(
                    self.keep_cols[mask.index(False)], batch.df.columns))

        if self.keep_cols:
            # stack columns
            ddf = batch.df[self.keep_cols]
            ddf.index = pred.index
            comb = pd.concat((ddf, pred), axis=1)
            assert comb.shape[0] == ddf.shape[0]
        else:
            comb = pred
        with self.lock:
            # if an error happends during/after the append we
            # might end up with inconsistent state
            # TODO write partition files instead of appending
            #  store checksum of each partition and back-check
            comb.to_csv(self.out_stream, mode='aU', header=self.first_write)
            self.out_stream.flush()

            self.db['checkpoints'].append(batch.id)

            if self.first_write:
                self.db['first_write'] = False
            self.first_write = False
            logger.info('batch {} checkpointed'.format(batch.id))
            self.db.sync()

    def batch_generator(self):
        return iter(BatchGenerator(self.dataset, self.n_samples,
                                   self.n_retry, self.delimiter))

    @classmethod
    def exists(cls):
        """Does shelve exist. """
        return any(glob.glob(cls.FILENAME + '*'))

    @classmethod
    def clean(cls):
        """Clean the shelve. """
        for fname in glob.glob(cls.FILENAME + '*'):
            os.remove(fname)


def prompt_yesno(msg):
    cmd = input('{} (yes/no)> '.format(msg)).strip().lower()
    while cmd not in ('yes', 'no'):
        cmd = input('Please type (yes/no)> ').strip().lower()
    return cmd == 'yes'


class NewRunContext(RunContext):
    """RunContext for a new run.

    It creates a shelve file and adds a checkpoint journal.
    """

    def __enter__(self):
        if self.exists():
            logger.info('Removing old run shelve')
            self.clean()
        if os.path.exists(self.out_file):
            logger.warn('File {} exists.'.format(self.out_file))
            rm = prompt_yesno('Do you want to remove {}'.format(self.out_file))
            if rm:
                os.remove(self.out_file)
            else:
                sys.exit(0)

        super(NewRunContext, self).__enter__()

        self.db['n_samples'] = self.n_samples
        self.db['project_id'] = self.project_id
        self.db['model_id'] = self.model_id
        self.db['keep_cols'] = self.keep_cols
        # list of batch ids that have been processed
        self.db['checkpoints'] = []
        # used to check if output file is dirty (ie first write op)
        self.db['first_write'] = True
        self.first_write = True
        self.db.sync()

        self.out_stream = open(self.out_file, 'w+')
        return self

    def __exit__(self, type, value, traceback):
        super(NewRunContext, self).__exit__(type, value, traceback)


class OldRunContext(RunContext):
    """RunContext for a resume run.

    It requires a shelve file and plays back the checkpoint journal.
    Checks if inputs are consistent.

    TODO: add md5sum of dataset otherwise they might
    use a different file for resume.
    """

    def __enter__(self):
        if not self.exists():
            raise ValueError('Cannot resume a project without {}'
                             .format(self.FILENAME))
        super(OldRunContext, self).__enter__()

        if self.db['n_samples'] != self.n_samples:
            raise ShelveError('n_samples mismatch: should be {} but was {}'
                              .format(self.db['n_samples'], self.n_samples))
        if self.db['project_id'] != self.project_id:
            raise ShelveError('project id mismatch: should be {} but was {}'
                              .format(self.db['project_id'], self.project_id))
        if self.db['model_id'] != self.model_id:
            raise ShelveError('model id mismatch: should be {} but was {}'
                              .format(self.db['model_id'], self.model_id))
        if self.db['keep_cols'] != self.keep_cols:
            raise ShelveError('keep_cols mismatch: should be {} but was {}'
                              .format(self.db['keep_cols'], self.keep_cols))

        self.first_write = self.db['first_write']
        self.out_stream = open(self.out_file, 'a')

        logger.info('resuming a shelved run with {} checkpointed batches'
                    .format(len(self.db['checkpoints'])))
        return self

    def __exit__(self, type, value, traceback):
        super(OldRunContext, self).__exit__(type, value, traceback)

    def batch_generator(self):
        """We filter everything that has not been checkpointed yet. """
        logger.info('playing checkpoint log forward.')
        already_processed_batches = set(self.db['checkpoints'])
        return (b for b in BatchGenerator(self.dataset,
                                          self.n_samples,
                                          self.n_retry,
                                          self.delimiter)
                if b.id not in already_processed_batches)


def context_factory(resume, cancel, n_samples, out_file, pid, lid,
                    keep_cols, n_retry,
                    delimiter, dataset, pred_name):
    """Factory method for run contexts.

    Either resume or start a new one.
    """
    if RunContext.exists():
        is_resume = None
        if resume:
            is_resume = True
        elif cancel:
            is_resume = False
        if is_resume is None:
            is_resume = prompt_yesno('Existing run found. Resume')
    else:
        is_resume = False
    if is_resume:
        return OldRunContext(n_samples, out_file, pid, lid, keep_cols, n_retry,
                             delimiter, dataset, pred_name)
    else:
        return NewRunContext(n_samples, out_file, pid, lid, keep_cols, n_retry,
                             delimiter, dataset, pred_name)


def exception_handler(request, *args):
    response = getattr(request, 'response', None)
    exc = args[0] if len(args) else None
    if exc:
        logger.warning('Exception: {} {}'.format(exc, type(exc)))
    else:
        logger.warn('Request failed -- retrying')

    if response is None:
        response = FakeResponse(400, 'No Response')

    if six.PY2:
        callback = request.kwargs['hooks']['response']
    elif six.PY3:
        callback = request[1]

    callback(response)


def requests_imap(requests, stream=False, size=None, exception_handler=None):
    if six.PY2:
        return grequests.imap(requests,
                              stream=stream,
                              size=size,
                              exception_handler=exception_handler)
    elif six.PY3:
        return arequests.imap(requests,
                              size=size,
                              exception_handler=exception_handler)
    else:
        raise ValueError('Unsupported Python Version')


def authorized(user, api_token, n_retry, endpoint, base_headers, row):
    """Check if user is authorized for the given model and that schema is correct.

    This function will make a sync request to the api endpoint with a single
    row just to make sure that the schema is correct and the user
    is authorized.
    """
    while n_retry:
        logger.debug('request authorization')
        try:
            data = row.to_csv(encoding='utf8', index=False)
            r = requests.post(endpoint, headers=base_headers,
                              data=data,
                              auth=(user, api_token))
            root_logger.debug('authorization request response: {}|{}'
                              .format(r.status_code, r.text))
        except requests.exceptions.ConnectionError:
            error('cannot connect to {}'.format(endpoint))
        if r.status_code == 200:
            # all good
            break
        if r.status_code == 400:
            # client error -- maybe schema is wrong
            try:
                msg = r.json()['status']
            except:
                msg = r.text

            error('failed with client error: {}'.format(msg))
        elif r.status_code == 401:
            error('failed to authenticate -- '
                  'please check your username and/or api token.')
        elif r.status_code == 405:
            error('failed to request endpoint -- '
                  'please check your --host argument.')
        else:
            n_retry -= 1
    if n_retry == 0:
        status = r.text
        try:
            status = r.json()['status']
        except:
            pass  # fall back to r.text
        logger.error(('authorization failed -- '
                      'please check project id and model id permissions: {}')
                     .format(status))
        rval = False
    else:
        logger.debug('authorization successfully')
        rval = True

    return rval


def run_batch_predictions_v1(base_url, base_headers, user, pwd,
                             api_token, create_api_token,
                             pid, lid, n_retry, concurrent,
                             resume, cancel, n_samples,
                             out_file, keep_cols, delimiter,
                             dataset, pred_name,
                             timeout):
    if not api_token:
        if not pwd:
            pwd = getpass.getpass('password> ')
        try:
            api_token = acquire_api_token(base_url, base_headers, user, pwd,
                                          create_api_token)
        except Exception as e:
            error('{}'.format(e))

    base_headers['content-type'] = 'text/csv; charset=utf8'
    endpoint = base_url + '/'.join((pid, lid, 'predict'))

    first_row = peek_row(dataset, delimiter)
    root_logger.debug('First row for auth request: %s', first_row)

    # Make a sync request to check authentication and fail early
    if not authorized(user, api_token, n_retry, endpoint,
                      base_headers, first_row):
        sys.exit(1)

    try:
        with context_factory(resume, cancel, n_samples, out_file, pid,
                             lid, keep_cols, n_retry, delimiter,
                             dataset, pred_name) as ctx:
            n_batches_checkpointed_init = len(ctx.db['checkpoints'])
            root_logger.debug('number of batches checkpointed initially: {}'
                              .format(n_batches_checkpointed_init))
            batches = ctx.batch_generator()
            work_unit_gen = WorkUnitGenerator(batches,
                                              endpoint,
                                              headers=base_headers,
                                              user=user,
                                              api_token=api_token,
                                              ctx=ctx,
                                              pred_name=pred_name,
                                              timeout=timeout)
            t0 = time()
            i = 0
            while work_unit_gen.has_next():
                responses = requests_imap(work_unit_gen,
                                          stream=False,
                                          size=concurrent,
                                          exception_handler=exception_handler)
                for r in responses:
                    i += 1
                    logger.info('{} responses sent | time elapsed {}s'
                                .format(i, time() - t0))

                logger.debug('{} items still in the queue'
                             .format(len(work_unit_gen.queue.deque)))

            root_logger.debug('list of checkpointed batches: {}'
                              .format(sorted(ctx.db['checkpoints'])))
            n_batches_checkpointed = (len(ctx.db['checkpoints']) -
                                      n_batches_checkpointed_init)
            root_logger.debug('number of batches checkpointed: {}'
                              .format(n_batches_checkpointed))
            n_batches_not_checkpointed = (work_unit_gen.queue.n_consumed -
                                          n_batches_checkpointed)
            batches_missing = n_batches_not_checkpointed > 0
            if batches_missing:
                logger.fatal(('scoring incomplete, {} batches were dropped | '
                             'time elapsed {}s')
                             .format(n_batches_not_checkpointed, time() - t0))
            else:
                logger.info('scoring complete | time elapsed {}s'
                            .format(time() - t0))
                os.remove(root_logger_filename)

    except ShelveError as e:
        error('{}'.format(e), exit=False)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt')
    except Exception as oe:
        error('{}'.format(oe), exit=False)


# FIXME: broken alpha version
def run_batch_predictions_v2(base_url, base_headers, user, pwd,
                             api_token, create_api_token,
                             pid, lid, concurrent, n_samples,
                             out_file, dataset, timeout):

    from datarobot_sdk.client import Client
    if api_token:
        Client(token=api_token, endpoint=base_url)
    elif pwd:
        Client(username=user, password=pwd, endpoint=base_url)
    else:
        error('Please provide a password or api token')
        sys.exit(1)

    from datarobot_sdk import Model
    model = Model.get(pid, lid)
    try:
        model.predict_batch(dataset, out_file + ".tmp",
                            n_jobs=concurrent, batch_size=n_samples)

        import csv
        # swap order of prediction CSV schema to match api/v1
        with open(out_file + ".tmp", "rb") as input_file:
            with open(out_file, "wb") as output_file:
                rdr = csv.DictReader(input_file)
                wrtr = csv.DictWriter(output_file, ["row_id", "prediction"],
                                      extrasaction='ignore')
                wrtr.writeheader()
                for a in rdr:
                    wrtr.writerow(a)

    except ShelveError as e:
        error('{}'.format(e), exit=False)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt')
    except Exception as oe:
        error('{}'.format(oe), exit=False)


def main():
    warnings.simplefilter('ignore')
    args = docopt(__doc__)

    level = logging.DEBUG if args['--verbose'] else logging.INFO
    configure_logging(level)

    printed_args = copy.copy(args)
    printed_args.pop('--password')
    root_logger.debug(printed_args)
    root_logger.info('platform: {} {}'.format(sys.platform, sys.version))

    if args['--version']:
        print('batch_scoring {}'.format(__version__))
        sys.exit(0)

    # parse args
    host = args['--host']
    pid = args['<project_id>']
    lid = args['<model_id>']
    n_retry = int(args['--n_retry'])
    if args['--keep_cols']:
        keep_cols = [s.strip() for s in args['--keep_cols'].split(',')]
    else:
        keep_cols = None
    concurrent = int(args['--n_concurrent'])
    dataset = args['<dataset>']
    pred_name = args['--pred_name'] if args['--pred_name'] else 'prediction'
    n_samples = int(args['--n_samples'])
    delimiter = args['--delimiter']
    resume = args['--resume']
    cancel = args['--cancel']
    out_file = args['--out']
    datarobot_key = args.get('--datarobot_key', None)
    pwd = args.get('--password', None)
    timeout = int(args['--timeout'])

    if '--user' not in args:
        user = input('user name> ').strip()
    else:
        user = args['--user'].strip()

    if not os.path.exists(args['<dataset>']):
        error('file {} does not exist.'.format(args['<dataset>']))
        sys.exit(1)

    pid = args['<project_id>']
    lid = args['<model_id>']

    try:
        verify_objectid(pid)
        verify_objectid(lid)
    except ValueError as e:
        error('{}'.format(e))
        sys.exit(1)

    api_token = args.get('--api_token', None)
    create_api_token = args.get('--create_api_token', None)
    pwd = args.get('--password', None)

    api_version = args['--api_version']

    base_url = '{}/{}/'.format(host, api_version)
    base_headers = {}
    if datarobot_key:
        base_headers['datarobot-key'] = datarobot_key

    logger.info('connecting to {}'.format(base_url))

    if api_version == 'v1':
        run_batch_predictions_v1(base_url, base_headers, user, pwd,
                                 api_token, create_api_token,
                                 pid, lid, n_retry, concurrent,
                                 resume, cancel, n_samples,
                                 out_file, keep_cols, delimiter,
                                 dataset, pred_name, timeout)
    elif api_version == 'v2':
        run_batch_predictions_v2(base_url, base_headers, user, pwd,
                                 api_token, create_api_token,
                                 pid, lid, concurrent, n_samples,
                                 out_file, dataset, timeout)
    else:
        error('API Version {} is not supported'.format(api_version))
        sys.exit(1)


if __name__ == '__main__':
    main()
