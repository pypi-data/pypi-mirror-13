# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from redturtle.jquerybrowser.testing import REDTURTLE_JQUERYBROWSER_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that redturtle.jquerybrowser is properly installed."""

    layer = REDTURTLE_JQUERYBROWSER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if redturtle.jquerybrowser is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'redturtle.jquerybrowser'))

    def test_browserlayer(self):
        """Test that IRedturtleJquerybrowserLayer is registered."""
        from redturtle.jquerybrowser.interfaces import (
            IRedturtleJquerybrowserLayer)
        from plone.browserlayer import utils
        self.assertIn(IRedturtleJquerybrowserLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = REDTURTLE_JQUERYBROWSER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['redturtle.jquerybrowser'])

    def test_product_uninstalled(self):
        """Test if redturtle.jquerybrowser is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'redturtle.jquerybrowser'))
