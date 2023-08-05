===============================
Cuteshop
===============================

.. image:: https://badge.fury.io/py/cuteshop.png
    :target: http://badge.fury.io/py/cuteshop

.. image:: https://travis-ci.org/uranusjr/cuteshop.png?branch=master
        :target: https://travis-ci.org/uranusjr/cuteshop

.. image:: https://pypip.in/d/cuteshop/badge.png
        :target: https://pypi.python.org/pypi/cuteshop


Package manager for Qt projects.

* Free software: MIT license
* Documentation: https://cuteshop.readthedocs.org.


What is Cuteshop?
=================

Short Version
-------------

It's like CocoaPods, but for Qt (qmake-based) projects, if you know what that
means.

Long Version
-------------

Cuteshop manages library dependencies for Qt (qmake-based) projects.

You describe your depedencies in a file called ``Shopfile``. Cuteshop analyzes
it, resolves all the library dependencies for you, and generate boilerplate
qmake configurations for you to use.




=======
History
=======

0.3.0 (2016-01-04)
---------------------

* Add option for additional spec sources.
* Add support for OTHER_FILES.
* Minor wording fixes.


0.2.1 (2015-09-20)
---------------------

* Add support for RESOURCES.
* Add QtHandlebarsJS spec.


0.2.0 (2015-07-07)
---------------------

* Add specs for QtSignal and QtYAML.
* Fix implementation for usage on Windows.
* More spec parameters made available.
* More bug fixes.


0.1.0 (2014-12-16)
---------------------

* First release on PyPI.


