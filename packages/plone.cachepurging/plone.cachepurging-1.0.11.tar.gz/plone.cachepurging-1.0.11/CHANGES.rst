Changelog
=========

1.0.11 (2016-01-08)
-------------------

Fixes:

- Fixed typo.
  [ale-rt]


1.0.10 (2015-11-28)
-------------------

Fixes:

- Changed i18n_domain to "plone".
  [staeff]


1.0.9 (2015-07-18)
------------------

- Do not iterate on settings.cachingProxies when there are no.
  [gotcha]


1.0.8 (2015-06-09)
------------------

- correctly be able to purge empty path(root of site). Previously, /
  was always appended to url so one potential path of the resource
  in varnish would never get purged--sometimes the most important, the homepage.
  [vangheem]


1.0.7 (2014-09-11)
------------------

- Fix installation issues due to missing commas in setup.py
  [esteele]


1.0.6 (2014-09-08)
------------------

- Add undeclared dependencies
  [gforcada]


1.0.5 (2013-12-07)
------------------

- Replace deprecated test assert statements.
  [timo]


1.0.4 (2012-12-09)
------------------

- Fixed purge paths for virtual hosting scenarios using virtual path components.
  [dokai]


1.0.3 (2011-09-16)
------------------

- Only import ssl module when purging an https url, closes #12190.
  [elro]

1.0.2 (2011-08-31)
------------------

- Cast wait_time to int before calling xrange. This fixes
  "TypeError: integer argument expected, got float" error.
  [vincentfretin]


1.0.1 - 2011-05-21
------------------

- Register a `zope.testing.cleanup.addCleanUp` function to stop all purge
  threads. Also make the default purger available as a module global, so the
  cleanup function can get to it after the ZCA has been torn down.
  [hannosch]

- Register an atexit handler to stop the purge thread on process shutdown.
  [hannosch]

- Change the reconnect strategy for the purge thread to retry fewer times and
  assume a permanent connection failure after one minute and stop the thread.
  This allows the application process to shutdown cleanly without the purge
  thread being stuck forever.
  [hannosch]

- Update socket connection code for the purge thread to use Python 2.6 support
  for passing in a timeout to the create_connection call.
  [hannosch]

- Disable `purge queue is full` warning in debug mode, where it spammed the
  console.
  [hannosch]

- Correct license and update distribution metadata.
  [hannosch]


1.0 - 2011-05-13
----------------

- Release 1.0 Final.
  [esteele]

- Add MANIFEST.in.
  [WouterVH]


1.0b2 - 2011-04-06
------------------

- Fix package requirements to pull in plone.app.testing as part of the [test]
  extra.
  [esteele]


1.0b1 - 2010-12-14
-------------------

- Fix rewriting of paths in a virtual hosting environment, so that the path passed
  to the rewriter is actually used instead of always the current request path.
  [davisagli]


1.0a1 - 2010-04-22
------------------

- Initial release
  [optilude, newbery]
