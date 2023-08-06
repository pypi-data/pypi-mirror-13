Web Testing library for Robot Framework
==================================================


Introduction
------------

WebLibrary is a web testing library for `Robot Framework`_
that leverages the `Selenium 2 (WebDriver)`_ libraries from the
Selenium_ project.

It is modeled after (and forked from) the SeleniumLibrary_ library,
but re-implemented to use Selenium 2 and WebDriver technologies.


Installation
------------

Using ``pip``
'''''''''''''

The recommended installation method is using
`pip <http://pip-installer.org>`__::

    pip install weblibrary

The main benefit of using ``pip`` is that it automatically installs all
dependencies needed by the library. Other nice features are easy upgrading
and support for un-installation::

    pip install --upgrade weblibrary
    pip uninstall weblibrary


Usage
-----

To write tests with Robot Framework and WebLibrary,
Selenium2Library must be imported into your Robot test suite.
See `Robot Framework User Guide`_ for more information.

Project Contributors
--------------------
* `Dong Hao <longmazhanfeng@gmail.com>`_
* `Wang Yangdan <wangyangdan@gmail.com>`_
* `Xia Daqiang <joehisaishi1943@gmail.com>`_
