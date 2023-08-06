# -*- coding: utf-8 -*-
"""Test Layer for ps.plone.fotorama."""

# zope imports
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from plone.testing import (
    Layer,
    z2,
)
from zope.configuration import xmlconfig


class PsPloneFotoramaLayer(PloneSandboxLayer):
    """Custom Test Layer for ps.plone.fotorama."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import ps.plone.fotorama
        xmlconfig.file(
            'configure.zcml',
            ps.plone.fotorama,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        applyProfile(portal, 'ps.plone.fotorama:default')


PS_PLONE_FOTORAMA_FIXTURE = PsPloneFotoramaLayer()

PS_PLONE_FOTORAMA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PS_PLONE_FOTORAMA_FIXTURE,),
    name='PsPloneFotoramaLayer:IntegrationTesting'
)


PS_PLONE_FOTORAMA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PS_PLONE_FOTORAMA_FIXTURE,),
    name='PsPloneFotoramaLayer:FunctionalTesting'
)


PS_PLONE_FOTORAMA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PS_PLONE_FOTORAMA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PsPloneFotoramaLayer:AcceptanceTesting'
)


ROBOT_TESTING = Layer(name='ps.plone.fotorama:Robot')
