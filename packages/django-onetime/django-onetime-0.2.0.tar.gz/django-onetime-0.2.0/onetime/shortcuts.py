from __future__ import absolute_import

from .models import OneTimeCallback


def call_later(callback, *args, **kwargs):
    otc = OneTimeCallback.objects.create(callback=callback, context=(args, kwargs))
    return otc.id


def call_view_later(callback, *args, **kwargs):
    otc = OneTimeCallback.objects.create(callback=callback, context=(args, kwargs), is_view=True)
    return otc.id
