# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from uuid import uuid4


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Status'
        db.create_table(u'updater_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('site_token', self.gf('django.db.models.fields.CharField')(default=uuid4, max_length=36)),
        ))
        db.send_create_signal(u'updater', ['Status'])

        # Adding model 'Notification'
        db.create_table(u'updater_notification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('security_issue', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'updater', ['Notification'])


    def backwards(self, orm):
        # Deleting model 'Status'
        db.delete_table(u'updater_status')

        # Deleting model 'Notification'
        db.delete_table(u'updater_notification')


    models = {
        u'updater.notification': {
            'Meta': {'object_name': 'Notification'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'security_issue': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'updater.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_token': ('django.db.models.fields.CharField', [], {'default': "uuid4", 'max_length': '36'})
        }
    }

    complete_apps = ['updater']