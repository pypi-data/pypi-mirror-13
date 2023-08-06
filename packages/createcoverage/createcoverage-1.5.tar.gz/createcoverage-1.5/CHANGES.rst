Changelog of createcoverage
===========================

1.5 (2016-02-02)
----------------

- Fixed ``bin/coverage`` script (it pointed at an old entry point). Note that
  this script is only included because buildout originally didn't install
  scripts of dependencies. It *does* now, with the proper configuration. But
  installing this script ourselves solves every case.


1.4.1 (2015-11-11)
------------------

- Upped the coverage requirement (to 3.7). Coveralls.io's library needs 3.6
  and this makes it a bit easier to make sure there's a new enough release.


1.4 (2015-09-17)
----------------

- Note: no functional changes in this release.

- Moved to github: https://github.com/reinout/createcoverage .

- Noted (in the ``setup.py`` classifiers) that we work just fine with
  python 3!

- Set up travis testing and coveralls.io integration. 100% coverage, of course
  :-)


1.3.2 (2014-12-09)
------------------

- Packaging fix. Nothing changed (functionally) compared to 1.3.


1.3.1 (2014-12-09)
------------------

- Some internal cleanup and a small pypi metadata fix.


1.3 (2014-12-09)
----------------

- Added ``-t/--test-args`` command line option. The string passed to
  that is passed straight on to the test runner. For instance, use
  ``-t "-m somemodule"`` to effectively run ``bin/test -m
  somemodule``. Note the need for quotes (single or double) as you're
  using an option to pass options... Fix by Godefroid Chapelle,
  thanks!


1.2 (2012-06-28)
----------------

- Fixed a problem with opening the coverage ``index.html`` file on OS X when
  using Python 2.7 or newer by using a file URL instead of a path.


1.1 (2011-04-19)
----------------

- Making the path to the coverage index.html file absolute before opening it
  in the webbrowser. This prevents OSX from complaining that it isn't a URL.


1.0 (2010-12-20)
----------------

- Added option ("-d") for specifying an output directory.  Specifying it also
  makes sure the results aren't opened in a webbrowser (as the option is
  intended for offline operation for automatic documentation generation
  purposes).


0.4 (2010-10-05)
----------------

- Falling back to global 'coverage' binary if there isn't one in
  ``bin/coverage``.


0.3 (2010-09-20)
----------------

- Added missing MANIFEST.in file so that the distribution on pypi is complete
  now.


0.2 (2010-09-20)
----------------

- Documentation update: pointing at bitbucket for code, issues, ideas.


0.1 (2010-09-20)
----------------

- First working version.

- Copied some code from the "createzopecoverage" package.

- Initial library skeleton created by nensskel.  [reinout]
