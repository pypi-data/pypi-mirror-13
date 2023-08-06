# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

import json

import django

if django.VERSION < (1, 7):
    from django.contrib.admin.util import NestedObjects
else:
    from django.contrib.admin.utils import NestedObjects
from django.core import serializers
from django.db import models, router
from django.db.models.fields.files import FileField
from django.utils.timezone import now


class AuditLog(models.Model):
    """Record of all changes made via Django admin interface."""
    username = models.TextField()
    user_id = models.IntegerField()
    model = models.TextField()
    change = models.CharField(max_length=100)
    representation = models.TextField()
    values = models.TextField()
    created_at = models.DateTimeField(default=now, blank=True)

    @classmethod
    def create(cls, user, obj, change, new_object=None):
        assert change in ['create', 'update', 'delete']

        values = serializers.serialize("json", [obj])
        # json[0] is for removing outside list, this serialization is only for
        # complete separate objects, the list is unnecessary
        json_content = json.loads(values)[0]
        if new_object:
            values_new = serializers.serialize("json", [new_object])
            json_new = json.loads(values_new)[0]
            json_content = {'new': json_new, 'old': json_content}
        if change == 'delete':
            file_fields = [f for f in obj._meta.fields
                           if isinstance(f, FileField)]
            if len(file_fields) > 0:
                json_content['files'] = {}
                for file_field in file_fields:
                    field_name = file_field.name
                    fileobj = getattr(obj, field_name)
                    if fileobj.name:
                        content = fileobj.read().encode('base64')
                        json_content['files'][fileobj.name] = content
        values_pretty = json.dumps(json_content, indent=2, sort_keys=True)
        return cls.objects.create(
            username=user.username,
            user_id=user.id,
            model=str(obj._meta),
            values=values_pretty,
            representation=unicode(obj),
            change=change,
        )


class AdminAuditMixin(object):

    def _flatten(self, lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result

    def _collect_deleted_objects(self, obj):
        result = []
        using = router.db_for_write(obj)
        collector = NestedObjects(using=using)
        collector.collect([obj])
        result = self._flatten(collector.nested())
        return result

    def log_addition(self, request, obj, *args, **kwargs):
        AuditLog.create(request.user, obj, 'create')
        super(AdminAuditMixin, self).log_addition(
            request, obj, *args, **kwargs)

    def log_deletion(self, request, obj, *args, **kwargs):
        for subobj in self._collect_deleted_objects(obj):
            AuditLog.create(request.user, subobj, 'delete')
        super(AdminAuditMixin, self).log_deletion(
            request, obj, *args, **kwargs)

    def save_model(self, request, new_obj, form, change):
        if change:
            # This is so that we'll get the values of the object before the
            # change
            old_obj = new_obj.__class__.objects.get(pk=new_obj.pk)
            AuditLog.create(
                request.user, old_obj, 'update', new_object=new_obj)
        super(AdminAuditMixin, self).save_model(
            request, new_obj, form, change)
