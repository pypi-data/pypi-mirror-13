========
Overview
========



Pre push hook running linters.

* Free software: BSD license

Installation
============

::

    pip install git-pre-push-hook

Install hook to current Git-repository:

::

    install-git-pre-push-hook

Default pre-push hook:

::

    python -c "import pre_push_hook; sys.exit(pre_push_hook.hook.main())"

Configuration
=============

You can pass configuration parameters to script by setting proper environement variables in ``./.git/hooks/pre-push``

1. Custom Pyflakes configuration file

::

    LINTER_FLAKE_CONFIG="./setup.cfg" python ...

2. Warnings only for changed lines 

::

    CHANGED_LINES_ONLY=1 python ...

Troubleshooting
===============

1. In OSX not prompt question is displayed and after pressing any key EOFError is raised:

Maybe you are not using system Python. E.g. MacPorts have problem with using stdin (
see: http://superuser.com/questions/965133/python2-7-from-macports-stdin-issue).
Try using system Python (``System/Library/Frameworks/Python.framework/Versions/Current/bin/python``)


Development
===========

To run the all tests run::

    tox


Changelog
=========

0.1.0 (2016-01-06)
-----------------------------------------

* First release on PyPI.


