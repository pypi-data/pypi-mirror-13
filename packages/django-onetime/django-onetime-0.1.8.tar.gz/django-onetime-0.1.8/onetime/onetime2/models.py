from __future__ import absolute_import
from django.db import models

from .onetime import fields


class OneTimeCallback(models.Model):
    id = fields.UUIDField(primary_key=True, editable=False)
    callback = fields.CallableField()
    context = fields.PythonLiteralField()
    is_view = models.BooleanField()

    def __unicode__(self):
        return "<OneTimeCallback: %s(%s)" % (self.callback.func_name, ','.join(list(map(str, self.context[0])) + ['%s=%r' % (k, v) for k, v in self.context[1].items()]))
