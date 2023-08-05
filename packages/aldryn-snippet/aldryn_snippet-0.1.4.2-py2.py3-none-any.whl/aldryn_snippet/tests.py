# -*- coding: utf-8 -*-
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import TestCase

from cms import api
from cms.models import CMSPlugin
from cms.test_utils.testcases import BaseCMSTestCase, URL_CMS_PLUGIN_ADD, URL_CMS_PLUGIN_EDIT
from cms.utils import get_cms_setting

from djangocms_snippet.cms_plugins import SnippetPlugin as OldSnippetPlugin
from djangocms_snippet.models import Snippet as OldSnippet

from .cms_plugins import Snippet
from .management.commands import migrate_from_djangocms_snippet


class Randomness(object):
    used = []

    def get(self, amount=1, length=20):
        """
        Returns a N(amount) random strings with length ``length`` which have not been used in this class before
        """
        rands = []
        for i in xrange(amount):
            rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
            if rand in self.used:
                rand = self.get(length)  # pragma: no cover
            self.used.append(rand)
            rands.append(rand)
        return rands[0] if amount == 1 else rands


class SnippetTestCase(TestCase, BaseCMSTestCase):
    su_username = 'user'
    su_password = 'pass'

    def setUp(self):
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.page = api.create_page('page', self.template, self.language, published=True)
        self.placeholder = self.page.placeholders.all()[0]
        self.superuser = self.create_superuser()
        self.random = Randomness()

    def tearDown(self):
        CMSPlugin.objects.all().delete()

    def create_superuser(self):
        return User.objects.create_superuser(self.su_username, 'email@example.com', self.su_password)

    def test_add_snippet_plugin_api(self):
        content, name = self.random.get(amount=2)
        plugin = api.add_plugin(self.placeholder, Snippet, self.language)

        plugin.content = content
        plugin.name = name
        plugin.save()

        self.page.publish(self.language)

        response = self.client.get(self.page.get_absolute_url())
        self.assertContains(response, content)

        # Test the unicode method
        self.assertEqual(plugin.__unicode__(), unicode(name))

    def test_add_snippet_plugin_client(self):
        self.client.login(username=self.su_username, password=self.su_password)

        content = self.random.get()
        plugin_data = {
            'plugin_type': 'Snippet',
            'plugin_language': self.language,
            'placeholder_id': self.placeholder.pk,
            'content': content,
        }

        # Add plugin
        self.assertFalse(CMSPlugin.objects.exists())
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CMSPlugin.objects.exists())

        # Edit plugin
        edit_url = '%s%d/' % (URL_CMS_PLUGIN_EDIT, CMSPlugin.objects.all()[0].pk)
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        data = {'content': content}
        response = self.client.post(edit_url, data)
        self.assertEqual(response.status_code, 200)

        # Check plugin content
        self.page.publish(self.language)
        self.client.logout()

        response = self.client.get(self.page.get_absolute_url())
        # self.assertContains(response, content)  # FIXME

    def djangocms_migration(self, keep=False):
        # Add and old SnippetPlugin and publish it
        content = self.random.get()
        old_snippet = OldSnippet(
            html=content,
        )
        old_snippet.save()
        api.add_plugin(self.placeholder, OldSnippetPlugin, self.language, snippet=old_snippet)
        self.page.publish(self.language)
        response = self.client.get(self.page.get_absolute_url())
        self.assertContains(response, content)

        self.assertTrue(OldSnippet.objects.exists())
        self.assertTrue(CMSPlugin.objects.filter(plugin_type='SnippetPlugin').exists())  # old plugin
        self.assertFalse(CMSPlugin.objects.filter(plugin_type='Snippet').exists())  # new plugin

        # Migrate to new snippet plugin
        call_command('migrate_from_djangocms_snippet', keep=keep)

        if keep:
            self.assertTrue(OldSnippet.objects.exists())
        else:
            self.assertFalse(OldSnippet.objects.exists())

        self.assertFalse(CMSPlugin.objects.filter(plugin_type='SnippetPlugin').exists())  # old plugin
        self.assertTrue(CMSPlugin.objects.filter(plugin_type='Snippet').exists())  # new plugin

        new_snippet = CMSPlugin.objects.filter(plugin_type='Snippet')[0].get_plugin_instance()[0]
        content = self.random.get()
        new_snippet.content = content
        new_snippet.save()

        self.page.publish(self.language)
        response = self.client.get(self.page.get_absolute_url())
        self.assertContains(response, content)

    def test_djangocms_snippet_migration(self):
        """
        Test the migration from djangocms_snippet.Snippet to aldryn_snippet.Snippet
        > Delete the old snippet objects
        """
        self.djangocms_migration(keep=False)

    def test_djangocms_snippet_migration_keep(self):
        """
        Test the migration from djangocms_snippet.Snippet to aldryn_snippet.Snippet
        > Keep the old snippet objects
        """
        self.djangocms_migration(keep=True)

    def test_djangocms_snippet_missing(self):
        """
        Test the migration from djangocms_snippet.Snippet to aldryn_snippet.Snippet
        withouth having djangocms-snippet installed
        """

        # monkey patch the command to simulate a not installed djangocms-snippet
        backup = getattr(migrate_from_djangocms_snippet, "OldSnippet")
        setattr(migrate_from_djangocms_snippet, "OldSnippet", None)

        self.assertRaises(ImproperlyConfigured, self.djangocms_migration)

        # restore the monkey patch
        setattr(migrate_from_djangocms_snippet, "OldSnippet", backup)
