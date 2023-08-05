# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OneTimeCallback'
        db.create_table('onetime_onetimecallback', (
            ('id', self.gf('onetime.fields.UUIDField')(max_length=64, primary_key=True)),
            ('callback', self.gf('onetime.fields.CallableField')()),
            ('context', self.gf('onetime.fields.PythonLiteralField')()),
        ))
        db.send_create_signal('onetime', ['OneTimeCallback'])

    def backwards(self, orm):
        # Deleting model 'OneTimeCallback'
        db.delete_table('onetime_onetimecallback')

    models = {
        'onetime.onetimecallback': {
            'Meta': {'object_name': 'OneTimeCallback'},
            'callback': ('onetime.fields.CallableField', [], {}),
            'context': ('onetime.fields.PythonLiteralField', [], {}),
            'id': ('onetime.fields.UUIDField', [], {'max_length': '64', 'primary_key': 'True'})
        }
    }

    complete_apps = ['onetime']