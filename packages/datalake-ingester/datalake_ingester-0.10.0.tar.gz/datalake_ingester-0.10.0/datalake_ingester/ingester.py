from memoized_property import memoized_property
from datalake_common import DatalakeRecord
from datalake_common.errors import InsufficientConfiguration, \
    UnsupportedTimeRange, NoSuchDatalakeFile
from translator import S3ToDatalakeTranslator
import time
import logging
from storage import DynamoDBStorage
from queue import SQSQueue
from reporter import SNSReporter
from errors import InvalidS3Notification, InvalidS3Event


logger = logging.getLogger('ingester')


# This is a list of exceptions that we may encounter that do not compromise our
# ability to ingest. These we simply wish to log, report, and move on.
SAFE_EXCEPTIONS = [
    InvalidS3Notification,
    InvalidS3Event,
    UnsupportedTimeRange,
    NoSuchDatalakeFile,
]


class IngesterReport(dict):

    def start(self):
        self.start = time.time()
        self['start'] = int(self.start * 1000)
        self.records = {}
        return self

    def add_record(self, r):
        self.records[r['url']] = r

    def end(self):
        self['status'] = 'success'
        self._finalize_report()
        return self

    def error(self, message):
        self['status'] = 'error'
        self['message'] = message
        self._finalize_report()
        return self

    def _finalize_report(self):
        self._set_records()
        self._set_duration()

    def _set_duration(self):
        self['duration'] = time.time() - self.start

    def _set_records(self):
        self['records'] = [self._make_record(r) for r in self.records.values()]

    def _make_record(self, r):
        return {
            'url': r['url'],
            'metadata': r['metadata']
        }


class Ingester(object):

    def __init__(self, storage, queue=None, reporter=None):
        self.storage = storage
        self.queue = queue
        self.reporter = reporter

    @classmethod
    def from_config(cls):
        storage = DynamoDBStorage.from_config()
        queue = SQSQueue.from_config()
        reporter = SNSReporter.from_config()
        return cls(storage, queue=queue, reporter=reporter)

    def ingest(self, url):
        '''ingest the metadata associated with the given url'''
        records = DatalakeRecord.list_from_url(url)
        for r in records:
            self.storage.store(r)

    @memoized_property
    def _translator(self):
        return S3ToDatalakeTranslator()

    def handler(self, msg):
        ir = IngesterReport().start()
        try:
            self._handler(msg, ir)
            ir.end()
        except Exception as e:
            logger.exception(e)
            ir.error(e.message)
            if type(e) not in SAFE_EXCEPTIONS:
                raise
        finally:
            self._report(ir)

    def _handler(self, msg, ir):
        records = self._translator.translate(msg)
        for r in records:
            ir.add_record(r)
            self.storage.store(r)

    def _report(self, r):
        if self.reporter is None:
            return
        self.reporter.report(r)

    def listen(self, timeout=None):
        '''listen to the queue, ingest what you hear, and report'''
        if not self.queue:
            raise InsufficientConfiguration('No queue configured.')

        self.queue.set_handler(self.handler)
        self.queue.drain(timeout=timeout)
