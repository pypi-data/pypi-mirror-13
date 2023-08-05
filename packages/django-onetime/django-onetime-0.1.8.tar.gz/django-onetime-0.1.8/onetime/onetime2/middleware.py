from __future__ import absolute_import

from django.conf import settings

from .models import OneTimeCallback


class CallbackMiddleware(object):
    def process_request(self, request):
        request_param = getattr(settings, 'ONETIME_REQUEST_PARAMETER', 'onetime_id')
        onetime_id = request.REQUEST.get(request_param, None)
        if onetime_id is None:
            return
        try:
            entry = OneTimeCallback.objects.get(id=onetime_id)
        except OneTimeCallback.DoesNotExist:
            return

        args, kwargs = entry.context
        if entry.is_view:
            retval = entry.callback(request, *args, **kwargs)
        else:
            retval = entry.callback(*args, **kwargs)
        entry.delete()
        return retval
