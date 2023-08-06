# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AuditLog.username'
        db.alter_column(u'adminaudit_auditlog', 'username', self.gf('django.db.models.fields.TextField')())

        # Changing field 'AuditLog.representation'
        db.alter_column(u'adminaudit_auditlog', 'representation', self.gf('django.db.models.fields.TextField')())

        # Changing field 'AuditLog.model'
        db.alter_column(u'adminaudit_auditlog', 'model', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'AuditLog.username'
        db.alter_column(u'adminaudit_auditlog', 'username', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'AuditLog.representation'
        db.alter_column(u'adminaudit_auditlog', 'representation', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'AuditLog.model'
        db.alter_column(u'adminaudit_auditlog', 'model', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        u'adminaudit.auditlog': {
            'Meta': {'object_name': 'AuditLog'},
            'change': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.TextField', [], {}),
            'representation': ('django.db.models.fields.TextField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.TextField', [], {}),
            'values': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['adminaudit']