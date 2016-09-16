import time
from contextlib import contextmanager
from functools import wraps
import logging

from .context import slowjam_context


@contextmanager
def span(stat, label=None, logger=logging.getLogger('timer'), prefix=None, extras=None, tag=None):
    start_time = time.time()

    with slowjam_context.event(stat, fmt=label, extras=extras, tag=tag) as ctx:
        yield ctx

    end_time = time.time()
    request_time_ms = (end_time - start_time) * 1000

    slowjam_context.log_time(stat, request_time_ms, prefix)

    if label:
        logger.info("%s took %dms" % (label, request_time_ms))


def annotate(stat, fmt=None, extras=None, tag=None):
    slowjam_context.mark(stat, fmt, extras, tag)


def timer(stat, label=None, logger=logging.getLogger('timer'), prefix=None, extras=None, tag=None, log_args=False):
    def timer_decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            _extras = dict(extras) if extras else {}
            if log_args:
                if args:
                    _extras['args'] = args
                if kwargs:
                    _extras['kwargs'] = kwargs

            with span(stat, label=label, logger=logger, prefix=prefix, extras=_extras, tag=tag):
                return f(*args, **kwargs)

        return wrapped_f
    return timer_decorator
