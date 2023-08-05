import logging
import pprint

from concurrent.futures import Future

DEFAULT_LOGGER = logging.getLogger(__name__)


class NullReporter(object):
    """
    Ignores all spans
    """
    def report_span(self, span):
        pass

    def close(self):
        fut = Future()
        fut.set_result(True)
        return fut


class LoggingReporter(NullReporter):
    """
    Logs all spans
    """
    def __init__(self, logger=None):
        self.logger = logger if logger else DEFAULT_LOGGER

    def report_span(self, span):
        logging.warn('Reporting span %s, lightstep_span %s', pprint.pformat(vars(span)), pprint.pformat(vars(span.lightstep_span)))
