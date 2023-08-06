# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

import json
import os

from cStringIO import StringIO
from random import choice
from string import ascii_letters
from datetime import timedelta

import django

from django.test import TestCase
from django.db.models import Model
from django.conf import settings
from django.core import mail
from django.core.files import File
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.contrib.admin import ModelAdmin, site
from django.contrib.auth.models import User, Permission
from django.utils.timezone import now

from mock import Mock, patch

from adminaudit import audit_install
from adminaudit.models import AuditLog
from adminaudit.management.commands.adminaudit_email_report import (
    Command as EmailCommand)

from example_app.models import Post


class BaseTestCase(TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        User.objects.filter(username='test').delete()
        AuditLog.objects.all().delete()

        self.user = User.objects.create_superuser(
            username='test', password='12345678', email='a@a.com')

        assert self.client.login(username='test', password='12345678')

    def test_access_admin(self):
        response = self.client.get(reverse('admin:index'))
        if django.VERSION < (1, 5):
            self.assertContains(
                response,
                '<a href="/admin/adminaudit/" class="section">')
        else:
            self.assertContains(
                response,
                '<a href="/admin/adminaudit/" class="section" '
                'title="Models in the Adminaudit application">')


class AuditLogTestCase(TestCase):
    def make_log_data(self, **overrides):
        data = {
            'username': 'test',
            'user_id': 1,
            'model': 'model',
            'change': 'change',
            'representation': 'representation',
            'values': 'values',
        }
        data.update(overrides)
        return data

    def assert_log_valid(self, data):
        log = AuditLog(**data)
        # force model validation
        # full_clean raises a ValidationError if object doesn't validate with
        # model.
        log.full_clean()

    def test_long_username(self):
        data = self.make_log_data(username='a'*500)
        self.assert_log_valid(data)

    def test_long_model(self):
        data = self.make_log_data(model='a'*500)
        self.assert_log_valid(data)

    def test_long_representation(self):
        data = self.make_log_data(representation='a'*500)
        self.assert_log_valid(data)


class AuditAdminEmailReportTestCase(TestCase):

    def create_and_log_in_user(self, **kwargs):
        defaults = {
            'username': "".join(choice(ascii_letters) for x in range(5)),
            'is_staff': True,
        }
        defaults.update(kwargs)
        user = User.objects.create(**defaults)
        user.set_password('test')
        user.save()

        # Give access to AuditLog and Post
        for perm in ['change_auditlog', 'add_post', 'change_post',
                     'delete_post']:
            user.user_permissions.add(Permission.objects.get(codename=perm))
        user.save()
        self.client.login(username=user.username, password='test')
        return user

    def test_when_logging_in_to_admin_you_can_see_audit_log_objects(self):
        self.create_and_log_in_user()

        r = self.client.get(reverse('admin:index'))
        self.assertContains(r, 'Audit logs')

        r = self.client.get('/admin/adminaudit/')
        self.assertEqual(200, r.status_code)

    def test_even_superuser_can_not_change_audit_log_object(self):
        user = self.create_and_log_in_user(is_superuser=True)

        auditlog_id = AuditLog.create(user, user, 'create').id
        url = '/admin/adminaudit/auditlog/{0}/'.format(auditlog_id)

        r = self.client.post(url, {
            'values': 'test',
            'representation': 'test',
            'change': 'create',
            'model': 'model',
            'user': user.pk,
        })
        auditlog = AuditLog.objects.get(pk=auditlog_id)

        self.assertNotEqual(auditlog.values, 'test')
        self.assertEqual(404, r.status_code)

    def test_even_superuser_can_not_delete_audit_log_objects(self):
        user = self.create_and_log_in_user(is_superuser=True)

        auditlog_id = AuditLog.create(user, user, 'create').id
        url = '/admin/adminaudit/auditlog/{0}/delete/'.format(auditlog_id)

        r = self.client.post(url, {'post': 'yes'})

        self.assertEqual(AuditLog.objects.filter(pk=auditlog_id).count(), 1)
        self.assertEqual(404, r.status_code)

    def test_js_for_removing_change_link_from_index_page_is_present(self):
        self.create_and_log_in_user(is_superuser=True)

        r = self.client.get(reverse('admin:index'))

        self.assertContains(r, 'a.parentNode.removeChild(a)')


class AdminIntegrationTestCase(BaseTestCase):

    def assertOneLogCreated(self, change):
        logs = AuditLog.objects.filter(username=self.user.username)
        self.assertEqual(1, logs.count())

        log = logs[0]
        self.assertEqual(change, log.change)

    def test_adding_new_object_via_admin_interface_is_saved_by_audit(self):
        r = self.client.post('/admin/auth/user/add/', {
            'username': "test_user",
            'password1': "test",
            'password2': "test",
        })
        # Redirect after object creation
        self.assertEqual(302, r.status_code)
        self.assertOneLogCreated('create')

    def test_changing_object_via_admin_is_saved_by_audit(self):
        r = self.client.get('/admin/auth/user/{0}/'.format(self.user.pk))
        data = r.context['adminform'].form.initial
        data.update({
            'first_name': "First",
            'last_login_0': str(data['last_login'].date()),
            'last_login_1': data['last_login'].strftime("%H:%M:%S"),
            'date_joined_0': str(data['date_joined'].date()),
            'date_joined_1': data['date_joined'].strftime("%H:%M:%S"),
        })
        r = self.client.post(
            '/admin/auth/user/{0}/'.format(self.user.pk), data)
        self.assertEqual(302, r.status_code)
        self.assertOneLogCreated('update')

    def test_deleting_object_via_admin_is_saved_by_audit(self):
        user = User.objects.create_user('newuser', 'new@example.com')
        r = self.client.post('/admin/auth/user/{0}/delete/'.format(user.pk), {
            'post': 'yes',
        })

        self.assertEqual(302, r.status_code)
        self.assertOneLogCreated('delete')

    def test_cascading_deleted_objects_also_receive_audit_log(self):
        user = User.objects.create_user('newuser', 'new@example.com')
        Post.objects.create(author=user, title='foo', body='bar')
        self.client.post('/admin/auth/user/{0}/delete/'.format(user.pk), {
            'post': 'yes',
        })
        # Check that delete cascaded to the related Post object
        self.assertEqual(0, Post.objects.count())
        # Check that an AuditLog object was created for each
        self.assertEqual(2, AuditLog.objects.count())

    def test_nested_cascading_deleted_objects(self):
        user = User.objects.create_user('newuser', 'new@example.com')
        post1 = Post.objects.create(author=user, title='foo', body='bar')
        Post.objects.create(
            author=user, title='bar', body='baz', related=post1)
        self.client.post(
            '/admin/auth/user/{0}/delete/'.format(user.pk),
            data={'post': 'yes'})
        # Check that delete cascaded to the related Post objects
        self.assertEqual(0, Post.objects.count())
        # Check that an AuditLog object was created for each
        self.assertEqual(3, AuditLog.objects.count())


class AuditLogAdminChangeViewTestCase(BaseTestCase):

    def test_display_change_view_for_create_log(self):
        auditlog = AuditLog.create(self.user, self.user, 'create')

        r = self.client.get(
            '/admin/adminaudit/auditlog/{0}/'.format(auditlog.pk))

        self.assertContains(r, 'test')
        self.assertContains(r, 'auth.user')

        self.assertTrue(r.context['new'])
        self.assertFalse(r.context['old'])

    def test_display_change_view_for_update_log(self):
        auditlog = AuditLog.create(self.user, self.user, 'update', self.user)

        r = self.client.get(
            '/admin/adminaudit/auditlog/{0}/'.format(auditlog.pk))

        self.assertTrue(r.context['new'])
        self.assertTrue(r.context['old'])

    def test_display_change_view_for_delete_log(self):
        auditlog = AuditLog.create(self.user, self.user, 'delete')

        r = self.client.get(
            '/admin/adminaudit/auditlog/{0}/'.format(auditlog.pk))

        self.assertFalse(r.context['new'])
        self.assertTrue(r.context['old'])

    def test_display_change_list(self):
        AuditLog.create(self.user, self.user, 'delete')

        r = self.client.get('/admin/adminaudit/auditlog/')

        self.assertNotContains(r, '<select name="action">')


class AdminAuditEmailReportTestCase(TestCase):

    command = 'adminaudit_email_report'

    def setUp(self):
        super(AdminAuditEmailReportTestCase, self).setUp()

        self.user = User.objects.create_user('user1', '1@example.com')
        self.auditlog = AuditLog.create(
            self.user, self.user, 'update', self.user)
        self.auditlog.created_at = self.auditlog.created_at - timedelta(days=1)
        self.auditlog.save()

    def test_report_date_returns_yesterday(self):
        report_date = EmailCommand().report_date()
        date_diff = now().date() - report_date

        self.assertEqual(date_diff.days, 1)

    def test_handle_sends_as_many_emails_as_there_are_settings_entries(self):
        recipients = ['{0}@example.com'.format(c) for c in 'abcdefghijk']
        settings.ADMINAUDIT_EMAILS_RECIPIENTS = recipients

        call_command(self.command, stdout=StringIO())

        self.assertEqual(11, len(mail.outbox))

    def test_no_mails_are_sent_when_there_are_no_recipients(self):
        with self.settings(ADMINAUDIT_EMAILS_RECIPIENTS=[]):
            call_command(self.command, stdout=StringIO())

        self.assertEqual(0, len(mail.outbox))

    def test_no_mails_are_sent_when_there_are_no_changs(self):
        recipients = ['{0}@example.com'.format(c) for c in 'abcdefghijk']
        with self.settings(ADMINAUDIT_EMAILS_RECIPIENTS=recipients):
            AuditLog.objects.all().delete()
            call_command(self.command, stdout=StringIO())

        self.assertEqual(0, len(mail.outbox))

    def test_data_for_user(self):
        user2 = User.objects.create_user('user2', '2@example.com')
        AuditLog.create(user2, self.user, 'update', self.user)

        data = EmailCommand().data_for_user(self.user.pk,
                                            AuditLog.objects.all())

        self.assertEqual(1, data['auditlogs'].count())
        self.assertIn('user1', data['caption'])

    def test_context_data(self):
        context = EmailCommand().context_data()

        self.assertEqual(1, len(context['users']))


class AdminAuditCLIReportTestCase(TestCase):

    command = 'adminaudit_report'

    def create_audit_log(self, user, obj, change, new_object):
        al = AuditLog.create(user, obj, change, new_object)
        al.created_at = al.created_at - timedelta(days=1)
        al.save()

    def test_handle(self):
        user1 = User.objects.create_user('user1', '1@example.com')
        user2 = User.objects.create_user('user2', '2@example.com')
        self.create_audit_log(user1, user1, 'update', user1)
        self.create_audit_log(user2, user2, 'update', user2)

        stdout = StringIO()
        call_command(self.command, stdout=stdout)

        self.assertIn('user1', stdout.getvalue())


class FilesTestCase(BaseTestCase):

    def create_post_with_attachement(self):
        with open('adminaudit/test_data/file_1.dat') as f:
            p = Post.objects.create(author=self.user, title='t', body='b')
            p.attachement.save('file_1.dat', File(f))
            p.save()

        return p

    def test_changing_file_in_the_admin_leaves_alone_old_file(self):
        p = self.create_post_with_attachement()

        with open('adminaudit/test_data/file_2.dat') as f:
            response = self.client.post(
                '/admin/example_app/post/{0}/'.format(p.pk),
                data={
                    'author': self.user.pk,
                    'title': "Post title",
                    'body': "Post body",
                    'attachement': f,
                }
            )

        self.assertRedirects(response, '/admin/example_app/post/')

        logs = AuditLog.objects.all().order_by('-created_at')
        self.assertEqual(logs.count(), 1)

        latest_log = logs[0]
        data = json.loads(latest_log.values)

        self.assertEqual('update', latest_log.change)
        self.assertTrue(os.path.exists(data['old']['fields']['attachement']))

    def test_deleting_object_via_admin_saves_the_file_content(self):
        p = self.create_post_with_attachement()
        attachement_path = p.attachement.name

        self.client.post('/admin/example_app/post/{0}/delete/'.format(p.pk), {
            'post': 'yes',
        })

        logs = AuditLog.objects.all().order_by('-created_at')
        self.assertEqual(logs.count(), 1)

        latest_log = logs[0]
        self.assertEqual('delete', latest_log.change)

        data = json.loads(latest_log.values)
        content = data['files'][attachement_path].decode('base64')
        original_content = open('adminaudit/test_data/file_1.dat').read()
        self.assertEqual(original_content, content)


class AuditInstallTestCase(TestCase):
    def test_audit_install_reentry(self):
        class AModel(Model):
            pass

        class AModelAdmin(ModelAdmin):
            pass

        model = AModel
        model_admin = AModelAdmin(AModel, site)
        mock_items = {model: model_admin}

        with patch.object(site, '_registry', mock_items):
            mock_unregister = Mock(side_effect=site.unregister)
            with patch.object(site, 'unregister', mock_unregister):
                audit_install()
                audit_install()

        mock_unregister.assert_called_once(model)
