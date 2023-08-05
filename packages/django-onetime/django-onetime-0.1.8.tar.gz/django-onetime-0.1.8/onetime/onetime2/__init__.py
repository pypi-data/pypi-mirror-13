from __future__ import absolute_import


def call_later(callback, *args, **kwargs):
    otc = models.OneTimeCallback.objects.create(callback=callback, context=(args, kwargs))
    return otc.id


def call_view_later(callback, *args, **kwargs):
    otc = models.OneTimeCallback.objects.create(callback=callback, context=(args, kwargs), is_view=True)
    return otc.id

from . import models
from . import fields
from . import middleware
