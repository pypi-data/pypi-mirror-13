# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import redturtle.jquerybrowser


class RedturtleJquerybrowserLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=redturtle.jquerybrowser)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redturtle.jquerybrowser:default')


REDTURTLE_JQUERYBROWSER_FIXTURE = RedturtleJquerybrowserLayer()


REDTURTLE_JQUERYBROWSER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REDTURTLE_JQUERYBROWSER_FIXTURE,),
    name='RedturtleJquerybrowserLayer:IntegrationTesting'
)


REDTURTLE_JQUERYBROWSER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REDTURTLE_JQUERYBROWSER_FIXTURE,),
    name='RedturtleJquerybrowserLayer:FunctionalTesting'
)


REDTURTLE_JQUERYBROWSER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        REDTURTLE_JQUERYBROWSER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='RedturtleJquerybrowserLayer:AcceptanceTesting'
)
