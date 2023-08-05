# -*- coding: utf-8 -*-
"""Test settings applied by ps.plone.basepolicy."""

# python imports
import unittest2 as unittest

# zope imports
from plone import api

# local imports
from ps.plone.basepolicy.testing import (
    PS_PLONE_BASEPOLICY_INTEGRATION_TESTING,
)


class TestSettings(unittest.TestCase):
    """Settings Test Case for ps.plone.basepolicy."""
    layer = PS_PLONE_BASEPOLICY_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        self.p_properties = api.portal.get_tool(name='portal_properties')
        self.portal_workflow = api.portal.get_tool(name='portal_workflow')

    def test_mailhost_host(self):
        """Validate the SMTP server settings."""
        mailhost = api.portal.get_tool(name='MailHost')
        self.assertEqual('localhost', mailhost.smtp_host)

    def test_email_from_address(self):
        """Validate the site from address."""
        self.assertEqual('', self.portal.getProperty('email_from_address'))

    def test_email_from_name(self):
        """Validate the site from name."""
        self.assertEqual(
            'Website Administrator',
            self.portal.getProperty('email_from_name'),
        )

    def test_about_view_anonymous_allowed(self):
        """Validate that only members see about information."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertFalse(getattr(sp, 'allowAnonymousViewAbout'))

    def test_dc_metadata_exposed(self):
        """Validate that the Dublin Core metadata is exposed."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertTrue(getattr(sp, 'exposeDCMetaTags'))

    def test_no_email_as_login(self):
        """Validate that email is not used as login."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertFalse(getattr(sp, 'use_email_as_login'))

    def test_external_sites_new_window(self):
        """Validate that external sites open in a new window."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertTrue(getattr(sp, 'external_links_open_new_window'))

    def test_nonfolderish_sections_disabled(self):
        """Validate that tabs are not generated for non-folderish items."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertTrue(getattr(sp, 'disable_nonfolderish_sections'))

    def test_sitemap_enabled(self):
        """Validate that the the sitemap.xml.gz is exposed."""
        sp = self.p_properties.get('site_properties')
        self.assertTrue(sp)
        self.assertTrue(getattr(sp, 'enable_sitemap'))

    def test_sendto_disabled(self):
        """Validate that nobody can use the sendto_form."""
        roles = self.portal.rolesOfPermission('Allow sendto')
        roles = [r['name'] for r in roles if r['selected']]
        self.assertEqual(roles, [])

    def test_quickupload_settings(self):
        """Validate the collective.quickupload settings."""
        sp = self.p_properties.get('quickupload_properties')
        self.assertTrue(sp)
        self.assertTrue(getattr(sp, 'show_upload_action'))

    def test_tinymce_settings(self):
        """Validate the custom TinyMCE editor settings."""
        utility = api.portal.get_tool(name='portal_tinymce')
        self.assertTrue(utility.link_using_uids)
        self.assertTrue(utility.toolbar_visualchars)
        self.assertTrue(utility.toolbar_media)
        self.assertTrue(utility.toolbar_removeformat)
        self.assertTrue(utility.toolbar_pasteword)
        self.assertTrue(utility.toolbar_pastetext)
        self.assertTrue(utility.toolbar_visualaid)
        self.assertTrue(utility.toolbar_cleanup)
