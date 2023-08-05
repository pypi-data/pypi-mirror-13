import copy
import os
import random
import threading
import time

import opentracing
import opentracing.standard.context

from . import instrument
from . import reporter as reporter_module

"""
LightStep's implementation of the python OpenTracing API.
http://opentracing.io
See the API definition for comments.
"""

FIELD_NAME_TRACE_ID = 'traceid'
FIELD_NAME_SPAN_ID  = 'spanid'
""" Note that these strings are lowercase because HTTP headers mess with capitalization.
"""

MAX_ID_BITS = 63

def init_for_opentracing(*args, **kwargs):
    """ The one command you need to call to start tracing with LightStep in opentracing.

    :param bool debug: whether spans should be printed to the console
    :param str group_name: name identifying the type of service that is being tracked
    :param str access_token: project's access token
    :param bool secure: whether HTTP connection is secure
    :param str service_host: Service host name
    :param int service_port: Service port number
    :param int max_log_records: Maximum number of log records to buffer
    :param int max_span_records: Maximum number of spans records to buffer

    After the first time this method is called, all arguments except for debug will be ignored.
    """
    # Act on the debug param but also remove it from kwargs so that get_runtime() doesn't complain about unknown args.
    if kwargs.pop('debug', False):
        reporter = reporter_module.LoggingReporter()
    else:
        reporter = reporter_module.NullReporter()
    opentracing.tracer = Tracer(instrument.get_runtime(*args, **kwargs), reporter)

class TraceContext(opentracing.standard.context.TraceContext):

    def __init__(self, trace_id, span_id, trace_attributes=None):
        super(TraceContext, self).__init__(trace_attributes=trace_attributes)
        self.trace_id = trace_id
        self.span_id = span_id
        # TODO(misha): Add a field here to identify the runtime.


class TraceContextSource(opentracing.TraceContextSource):

    def __init__(self, runtime):
        self.random = random.Random(time.time() * (os.getpid() or 1))
        # We don't actually need to store the runtime here, we can
        # just call get_runtime() whenever we want it, but we might
        # want to move away from that implementation down the road, so
        # I'm including it here.
        self.runtime = runtime

    def random_id(self):
        return self.random.getrandbits(MAX_ID_BITS)

    def new_root_trace_context(self):
        trace_id = self.random_id()
        span_id = self.random_id()
        return TraceContext(trace_id=trace_id, span_id=span_id)

    def new_child_trace_context(self, parent_trace_context):
        with parent_trace_context.lock:
            trace_attributes = copy.deepcopy(parent_trace_context.trace_attributes)
        ctx = TraceContext(trace_id=parent_trace_context.trace_id,
                           span_id=self.random_id(),
                           trace_attributes=trace_attributes)
        return ctx, {'parent_span_id': parent_trace_context.span_id}

    def close(self):
        pass

# TODO(misha): Find a binary encoding that works in both python and go and then add the corresponding methods below.

class TraceContextEncoder(opentracing.TraceContextEncoder):
    def trace_context_to_text(self, trace_context):
        return {FIELD_NAME_TRACE_ID: str(trace_context.trace_id),
                FIELD_NAME_SPAN_ID: str(trace_context.span_id)}, trace_context.trace_attributes

class TraceContextDecoder(opentracing.TraceContextEncoder):
    def trace_context_from_text(self, trace_context_id, trace_attributes):
        trace_id = int(trace_context_id[FIELD_NAME_TRACE_ID])
        span_id = int(trace_context_id[FIELD_NAME_SPAN_ID])
        # TODO(misha): Think about whether we should validate trace_attributes
        return TraceContext(trace_id=trace_id, span_id=span_id, trace_attributes=trace_attributes)


class Span(opentracing.Span):
    def __init__(self, trace_context, tracer, lightstep_span, tags=None):
        super(Span, self).__init__(trace_context)
        self.tracer = tracer
        self.update_lock = threading.Lock()
        self.lightstep_span = lightstep_span
        self.set_tag('trace_id', str(trace_context.trace_id))
        if tags:
            for k, v in tags.iteritems():
                self.set_tag(k, v)

    # __enter__ and __exit__ are provided by opentracing.Span

    def start_child(self, operation_name):
        return self.tracer.join_trace(operation_name, self.trace_context)

    def finish(self):
        self.lightstep_span.end()
        self.tracer.report_span(self)

    def set_tag(self, key, value):
        # TODO(misha): Add support for int and bool tag values.
        self.lightstep_span.add_join_id(key, str(value))
        return self

    def info(self, message, *args):
        self.lightstep_span.infof(message, *args)
        return self

    def error(self, message, *args):
        self.lightstep_span.errorf(message, *args)
        return self


class Tracer(opentracing.Tracer):

    def __init__(self, runtime, reporter):
        self.trace_context_source = TraceContextSource(runtime)
        self.encoder = TraceContextEncoder()
        self.decoder = TraceContextDecoder()
        self.reporter = reporter

    def start_trace(self, operation_name, tags=None):
        trace_context = self.trace_context_source.new_root_trace_context()
        return Span(trace_context,
                    self,
                    self.trace_context_source.runtime.span(operation_name),
                    tags=tags)

    def join_trace(self, operation_name, parent_trace_context, tags=None):
        trace_context, span_tags = \
            self.trace_context_source.new_child_trace_context(parent_trace_context)
        span = Span(trace_context,
                    self,
                    self.trace_context_source.runtime.span(operation_name),
                    tags=tags)
        for key, value in span_tags.iteritems():
            span.set_tag(key, value)
        return span

    def report_span(self, span):
        self.reporter.report_span(span)

    def close(self):
        instrument.flush()
        self.trace_context_source.close()
        return self.reporter.close()

    # TraceContextSource methods
    def new_root_trace_context(self):
        return self.trace_context_source.new_root_trace_context()

    def new_child_trace_context(self, parent_trace_context):
        return self.trace_context_source.new_child_trace_context(parent_trace_context)

    #TraceContextEncoder methods
    def trace_context_to_text(self, trace_context):
        return self.encoder.trace_context_to_text(trace_context)

    #TraceContextDecoder methods
    def trace_context_from_text(self, trace_context_id, trace_attributes):
        return self.decoder.trace_context_from_text(trace_context_id, trace_attributes)
