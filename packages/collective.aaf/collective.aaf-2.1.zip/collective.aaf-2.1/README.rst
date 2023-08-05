.. contents::

Introduction
============

This package provides an integration layer for Plone for the `Australian
Access Federation <http://aaf.edu.au>`_ (AAF), a Shibboleth-powered
authentication federation.  This package builds upon `collective.shibboleth <https://pypi.python.org/pypi/collective.shibboleth>`_.

Features
========

* Configures the underlying authentication plugin to load user data from
  the relevant AAF attributes.

Most heavy lifting is now carried out by ``collective.shibboleth`` so this
package just depends upon that.

Installation
============

Installation with Plone follows the standard practice of modifying your
Buildout configuration like so, adding this package to your list of eggs::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    eggs +=
        collective.aaf

Once installed, this package will configure the underlying packages in Plone
accordingly.
