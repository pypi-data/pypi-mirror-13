This library for RobotFramework
==================================================

Introduction
------------

MobileLibrary is an appium testing library for `RobotFramework <http://code.google.com/p/robotframework/>`_.

It uses `Appium <http://appium.io/>`_ (version 1.x) to communicate with Android and iOS application 
similar to how `Selenium WebDriver <http://seleniumhq.org/projects/webdriver/>`_ talks
to web browser.

It support Python 2.x only.


Installation
------------

Using ``pip``
'''''''''''''

The recommended installation method is using
`pip <http://pip-installer.org>`__::

    pip install mobilelibrary



Usage
-----

To write tests with Robot Framework and AppiumLibrary, 
AppiumLibrary must be imported into your RF test suite.
See `Robot Framework User Guide <https://code.google.com/p/robotframework/wiki/UserGuide>`_ 
for more information.

As it uses Appium make sure your Appium server is up and running.
For how to use Appium please refer to `Appium Documentation <http://appium.io/getting-started.html>`_
