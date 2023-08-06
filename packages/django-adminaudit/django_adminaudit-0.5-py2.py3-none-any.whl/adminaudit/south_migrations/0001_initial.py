# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AuditLog'
        db.create_table(u'adminaudit_auditlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('change', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('representation', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('values', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'adminaudit', ['AuditLog'])


    def backwards(self, orm):
        # Deleting model 'AuditLog'
        db.delete_table(u'adminaudit_auditlog')


    models = {
        u'adminaudit.auditlog': {
            'Meta': {'object_name': 'AuditLog'},
            'change': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'representation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'values': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['adminaudit']