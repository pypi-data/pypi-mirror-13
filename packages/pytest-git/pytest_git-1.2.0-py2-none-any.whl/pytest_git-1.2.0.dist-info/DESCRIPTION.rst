Pytest GIT Fixture
==================

Creates an empty Git repository for testing that cleans up after itself
on teardown.

Installation
------------

Install using your favourite package installer:

.. code:: bash

        pip install pytest-git
        # or
        easy_install pytest-git

Enable the fixture explicitly in your tests or conftest.py (not required
when using setuptools entry points):

.. code:: python

        pytest_plugins = ['pytest_git']

Usage
-----

This plugin is a thin wrapper around the excellent GitPython library
(see http://gitpython.readthedocs.org/en/stable/). Here's a noddy test
case that shows it working:

.. code:: python

    def test_git_repo(git_repo):
        # The fixture derives from `workspace` in `pytest-shutil`, so they contain 
        # a handle to the path.py path object (see https://pythonhosted.org/path.py)
        path = git_repo.workspace
        file = path / 'hello.txt'
        file.write_text('hello world!')

        # We can run commands relative to the working directory
        git_repo.run('git add hello.txt')

        # It's better to use the GitPython api directly - the 'api' attribute is 
        # a handle to the repository object.
        git_repo.api.index.commit("Initial commit")

        # The fixture has a URI property you can use in downstream systems
        assert git_repo.uri.startswith('file://')


Changelog
---------

1.2.0 (2016-2-19)
~~~~~~~~~~~~~~~~~

-  New plugin: git repository fixture

1.1.1 (2016-2-16)
~~~~~~~~~~~~~~~~~

-  pytest-profiling improvement: escape illegal characters in .prof
   files (Thanks to Aarni Koskela for the PR)

1.1.0 (2016-2-15)
~~~~~~~~~~~~~~~~~

-  New plugin: devpi server fixture
-  pytest-profiling improvement: overly-long .prof files are saved as
   the short hash of the test name (Thanks to Vladimir Lagunov for PR)
-  Changed default behavior of workspace.run() to not use a subshell for
   security reasons
-  Corrected virtualenv.run() method to handle arguments the same as the
   parent method workspace.run()
-  Removed deprecated '--distribute' from virtualenv args

1.0.1 (2015-12-23)
~~~~~~~~~~~~~~~~~~

-  Packaging bugfix

1.0.0 (2015-12-21)
~~~~~~~~~~~~~~~~~~

-  Initial public release



