try:
    from django.conf import settings
except ImportError:
    class Settings(object):
        SLOWJAM_LOG_THRESHOLD = 200

    settings = Settings()

import json
import logging

from slowjam.context import slowjam_context

logger = logging.getLogger(__name__)


class SlowjamMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if slowjam_context:
            extras = {
                'host': request.META.get('HTTP_HOST'),
                'ip': request.META.get('REAL_IP'),
                'method': request.method,
                'uri': request.get_full_path(),
                'view': request.view_name,
                'view_args': view_args,
                'view_kwargs': view_kwargs,
            }

            slowjam_context.start('request', extras=extras)

    def process_response(self, request, response):
        if slowjam_context:
            profile = slowjam_context.stop()
            if profile:
                exec_time = profile.execution_time
                if exec_time and exec_time > getattr(settings, 'SLOWJAM_LOG_THRESHOLD', 200):
                    if settings.DEBUG:
                        # Here you might want to blacklist certain kinds of views from showing up
                        if profile:
                            print ''
                            print unicode(profile)
                            print ''
                    else:
                        d = profile.to_dict()
                        serialized_profile = json.dumps(d, separators=(',', ':'))
                        logger.info('slowjam', extra={'slowjam': serialized_profile})

        return response
