Introduction
============

``collective.MockMailHost`` enables integration testing of email functionality
from Plone_. Simply add this egg to your [test] runner section, and install
this product through your ``Layer`` or ``TestCase``.

Note
  THIS IS FOR TESTING PURPOSE ONLY, do not use this product on your
  running Plone site. It replaces the standard MailHost with a Mock
  MailHost that you can poke at to check email content and recipients.

Has been tested with Plone 4 but should also work with earlier versions.


Integration
-----------

Example how to integrate ``collective.MockMailHost`` to your testing setup
based on `plone.app.testing`_. Add the package to your extras_requires section
in your package's ``setup.py`` file, so buildout will automatically download
the package for you.::

    setup(name='my.package',
          ...
          extras_require={
            'test': [
                'plone.app.testing',
                'collective.MockMailHost',
            ]
          },
          ...
          )

Your test layer setup could look like this example below::

    from plone.app.testing import helpers, layers
    from plone.testing import z2


    class MyLayer(helpers.PloneSandboxLayer):
        defaultBases = (layers.PLONE_FIXTURE, )

        def setUpZope(self, app, configurationContext):
            # Load zcml
            import collective.MockMailHost
            self.loadZCML(package=collective.MockMailHost)

            # Install product and call its initialize() function
            z2.installProduct(app, 'collective.MockMailHost')

            # Note: you can skip this if my.product is not a Zope 2-style
            # product, i.e. it is not in the Products.* namespace and it
            # does not have a <five:registerPackage /> directive in its
            # configure.zcml.

        def tearDownZope(self, app):
            # Uninstall product
            z2.uninstallProduct(app, 'collective.MockMailHost')

            # Note: Again, you can skip this if my.product is not a Zope 2-
            # style product

        def setUpPloneSite(self, portal):
            helpers.quickInstallProduct(portal, 'collective.MockMailHost')

            helpers.applyProfile(portal, 'collective.MockMailHost:default')

    MY_FIXTURE = MyLayer()

.. _Plone: http://plone.org
.. _`plone.app.testing`: http://pypi.python.org/pypi/plone.app.testing
