======================
 NEWS about uci-tests
======================

Overview of changes to uci-tests in reverse chronological order.

0.4.1
=====

* Properly route spurious output from tests to unbreak subunit stream
  parsing.


0.4.0
=====

* Switch to subunit v2.

* Set subunit streams to unbuffered.


0.3.1
=====

* Remove the '-p' alias for --pick. The reason is that it conflicts when the
  option is needed for some external django runner. The rationale is that
  this option is for advanced users and it's better to use the long name as
  the effect is unusual.


0.3.0
=====

* Add runners.add_uci_run_tests_options() to make it easier to add the uci
  options to other argparse-based parsers.

* Add --pick n/m to run 1 out of m tests concurrently without requiring a
  test id list.

* Add filters.pick() to make it easier to run tests concurrently without
  having to pass lists of test ids around.

* Rework concurrent suites adding the 'factor' parameter so that child
  suites better knows their context.

  /!\ Incompatible change: suites that inherited from SubprocessedSuite may
  need to inherit from SubprocessedSuiteWithLoadFile instead and update
  their signature anyway.


0.2.1
=====

* Brown paper bag release for pypi and python2.


0.2.0
=====

* Fix xenial support.

* Fix precise support for python2 (python3 can't be supported there as
  testtools and subunit don't provide python3 versions).
    
* Add SubprocessedSuite to support running concurrent tests in
  subprocesses. Like ForkedSuite, this uses subunit to communicate between
  the controller and the workers. SubprocessedSuite can be used as a base to
  provide the command to produce a subunit stream from a list of tests.

  /!\ Incompatible change: runners.run_suite_forked and
  runners.TestInOtherProcess have been replaced by
  ForkedSuite. runners.split_suite_for() signature has changed.

* Fix test failures on wily triggered by python __name__'ing classes
  defined inside a function in a different way than classes defined at the
  module level (they were previously getting names in the module name space
  rather than 'module.<locals>' which is not a valid python symbol).

* Add a 'prefix' optional argument to fixtures.set_uniq_cwd() and change the
  default to the test method name which help identifying leaks under '/tmp'.


0.1.9
=====

* Delay output from test results for consistency and allowing addError (and
  friends) to be used more freely.

* Fix pypi packaging issue by using python3 to create the sdist (otherwise
  uci-run-tests is not included and pip install fails for the py3 version).
  As of today, pip install should also specify python-subunit==0.0.16 and
  testtools==0.9.34. More recent versions are not supported (yet).


0.1.8
=====

* Fix subunit requirement in setup.py, the proper name is python-subunit.


0.1.7
=====

* Add a '--load' option so a list of test ids can be run (this can be
  combined with included and excluded regexps).

* Display how many tests where skipped by 'reason' in the summary.

* Plug into unittest ctrl-C handling.

* Internal refactoring to allow concurrency runs to be used with arbitrary
  methods to pipe subunit streams between processes.

* Add a TestSuite object implementing setUp() and addCleanUp() with
  semantics similar to unittest.TestCase but applied to suites.


0.1.6
=====

* Add python3 support.


0.1.5
=====

* Fix some octal constants for compatibility with py3 (wip).

* Add support for parametrized tests (ucitests.scenarii).


0.1.4
=====

* Flush all output from the test result or feedback about which test is
  running is wrong.


0.1.3
=====

* Add support for concurrent running by splitting across sub-processes.

* TestPep8 was failing to report some errors.

* Add features.UbuntuPlatform for tests that requires specific Ubuntu Releases.


0.1.2
=====

* Switch from distutils to setuptool since virtualenv does not seem to
  support 'requires' for dependency handling.

* Expose fixtures.build_tree to create arbitrary trees from a textual
  description. Tests that requires building complex trees are easier to
  write with this helper.


0.1.0
=====

* TestPyflakes.excludes expect paths including the module name.


0.0.9
=====

* runners.RunTestsArgParser can be sub-classed.

* import errors give a better traceback revealing where they happen (instead
  of inside ucitests which was a poor UI).

* /!\\ Incompatible change: NameMatcher has been moved from loaders to
  matchers.

* /!\\ Incompatible change: TestPep8 and TestPyflakes have been moved from
  ucitests.tests.test_style to ucitests.styles.

* provide a walker.Walker class that can filter a file system tree and call
  a handler for each file or directory.


0.0.8
=====

* add the tests themselves to the installed packages (so dep8 can use them
  and test_style can be used by other projects).

* disable tests that requires recent versions for testtools, pep8 and
  pyflakes so most of the package can be dep8 tested on precise.


0.0.7
=====

* allow tests to be loaded from importable modules with -m MODULE.

* provide a Loader.packageSysPathFromName convenience method to find where a
  package is imported from.


0.0.6
=====

* add pyflakes support in test_style.


0.0.5
=====

 * add features.py with ExecutableFeature as an example.

 * add a features.requires decorator to skip tests when a feature is not
   available.

 * make assertSuccessfullTest part of assertions.py.


0.0.4
=====

 * revert to python2 to match current needs.


0.0.3
=====

 * add assertions.assertLength to check the length of an iterable and
   display it when the length is wrong.

 * add fixtures.isolate_env to isolate tests from os.environ.


0.0.2
=====

New release to fix packaging issues.


0.0.1
=====

First release.
