# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OneTimeCallback.is_view'
        db.add_column('onetime_onetimecallback', 'is_view',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'OneTimeCallback.is_view'
        db.delete_column('onetime_onetimecallback', 'is_view')

    models = {
        'onetime.onetimecallback': {
            'Meta': {'object_name': 'OneTimeCallback'},
            'callback': ('onetime.fields.CallableField', [], {}),
            'context': ('onetime.fields.PythonLiteralField', [], {}),
            'id': ('onetime.fields.UUIDField', [], {'max_length': '64', 'primary_key': 'True'}),
            'is_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['onetime']