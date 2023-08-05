Changelog
=========

2.1 (2016-01-21)
----------------

- Changed `various` import step to be ZCML configured.
  [davidjb]


2.0 (2015-05-20)
----------------

- **Backwards incompatibility**: because of the migration of portlet to
  ``collective.shibboleth``, you need to remove the existing
  ``collective.aaf`` portlet before upgrading.
  [davidjb]
- Refactor into ``collective.shibboleth`` and depend on that package.  This
  package now adds just the AAF specific settings into Plone, extending
  ``collective.shibboleth``.
  [davidjb]


1.5 (unreleased)
----------------

- Nothing changed yet.


1.4 (2015-04-28)
----------------

- Make portlet header friendlier.
  [davidjb]


1.3 (2014-02-26)
----------------

- Configure AutoUserMakerPASPlugin to auto-update user properties on login.
  [davidjb]

1.2 (2014-02-19)
----------------

- Made the embedded WAYF JavaScript URL depend on the portlet's
  configured URL rather than being hardcoded.
  [davidjb]


1.1 (2014-01-30)
----------------

- Noted that latest collective.pluggablelogin released. Package now
  depends on this latest version or later.
  [davidjb]


1.0 (2014-01-29)
----------------

- If logging in again from a logged_out view, then strip the view from
  the ``came_from`` query string parameter. 
  [davidjb]
- Notify users of their temporary passwords being generated on first login.
  [davidjb]
- Monkey patch the password generation function AutoUserMakerPASPlugin
  to allow stronger passwords.
  [davidjb]
- Ensure users logging in get the Shibboleth Authenticated role via
  AuthZ mapping.
  [davidjb]
- Add Shibboleth Authenticated role.
  [davidjb]
- Package created using templer
  [davidjb]
