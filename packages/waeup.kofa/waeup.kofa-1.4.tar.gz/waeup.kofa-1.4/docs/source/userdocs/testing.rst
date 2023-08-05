.. _testing:

Testing
*******

Introduction
============

Kofa's Python code is being tested automatically. The developers'
goal is to reach 100% code coverage by Kofa's test runners, which
means that each single line of code is passed at least one time when
running the tests.

Why testing? Testing makes sure that our code works properly under
given sets of conditions and, only comprehensive testing ensures
that changing or customizing the code does not break existing
functionality.

Why *automated* testing? Simply because no developer likes to click
around the user interface to check tons of functionality. In Kofa
more than 1300 tests, with dozens of actions per test, are being
executed each time when the testrunner is started. This job can't be
done manually.

What we test: "Unit" and "Functional" Tests
-------------------------------------------

There are two different ways to test the code of a web application
automatically: *unit tests* and *functional tests*. The goal of unit
testing is to isolate each part of the program and show that the
individual parts are correct. Functional tests of a web application
are more wholistic, they require a running web application in the
background with even a working (temporary) database. Functional
tests are typically linked to a particular use case, they are
interacting with the portal as a user would. That implies that
functional testing has to make use of a test browser. A test browser
does the same job as normal web browser does, except for visualizing
the rendered HTML code.


How we test: "Python" and "Doctest" Tests
-----------------------------------------

There are also two different ways to integrate tests, either
functional or unit, into a Python package: *Doctest tests* (or doctests)
and *Python tests*. Python test modules are a collection of
isolatable Python test cases. A test case combines a collection of
test methods which are being executed by the testrunner one
after the other. Python test modules are automatically identified by
means of their filenames which start with ``test_``. In contrast,
doctests can be wrapped up in simple text files (ending with
``.txt``), or they can be put into docstrings of the application's
source code itself. Common to all doctests is that they are based on
output from the standard Python interpreter shell (indicated by the
interpreter prompt ``>>>``. The doctest runner parses all ``py`` and
``txt`` files in our package, executes the interpreter commands
found and compares the output against an expected value. Example::

  Python's `math` module can compute the square root of 2:

  >>> from math import sqrt
  >>> sqrt(2)
  1.4142135623730951

Why wrapping tests into documentation? An objective of testdriven
software development is also the documentation of the 'Application
Programming Interface' (API) and, to a certain extent, providing a
guideline to users, how to operate the portal. The first is mainly
done in the docstrings of Python modules which present an expressive
documentation of the main use cases of a module and its components.
The latter is primarily done in separate ``txt`` files.

When starting the development of Kofa, we relied on writing a
coherent documentation including doctests in restructured text
format. During the software development process, the focus shifted
from doctesting to pure Python testing with a lot of functional
tests inside. It turned out that Python tests are easier to handle
and more powerful. Drawback is, that these tests cannot easily be
integrated into the Sphinx documentation project (the documentation
which you are reading right now). However, we will list some of
these tests and try to explain what they are good for.


Doctest Tests
=============

Browsing
--------

.. toctree::
   :maxdepth: 2

   testing/pages
   testing/breadcrumbs

Cataloging
----------

.. toctree::
   :maxdepth: 2

   testing/catalog

Data Center
-----------

.. toctree::
   :maxdepth: 2

   testing/datacenter

Security
--------

.. toctree::
   :maxdepth: 2

   testing/permissions

Officers
--------

.. toctree::
   :maxdepth: 2

   testing/userscontainer

University
----------

.. toctree::
   :maxdepth: 2

   testing/app

Academic Section
----------------

.. toctree::
   :maxdepth: 2

   testing/certcourse

Batch Processing
----------------

.. toctree::
   :maxdepth: 2

   testing/batchprocessing
   testing/batchprocessing_browser

Access Codes
------------

.. toctree::
   :maxdepth: 2

   testing/accesscode


Python Tests
============

There are hundreds of Python test cases in Kofa with many test
methods each. Here we present only a few of them. The test methods
are easy to read. In most cases they are functional and certain
methods and properties of a test browser are called. Most important
are `browser.open()` (opens a web page), `browser.getControl()`
(gets a control button), `browser.getLink()` (gets a link) and
`browser.contents` (is the HTML content of the opened page).


.. _test_suspended_officer:

Suspended Officer Account
-------------------------

The first test can be found in
`waeup.kofa.browser.tests.test_browser.SupplementaryBrowserTests`. The test makes sure that suspended officers can't login but see a
proper warning message when trying to login. Furthermore, suspended
officer accounts are clearly marked and a warning message shows up
if a manager accesses a suspended account, see :ref:`Officers
<officers>`.

.. literalinclude:: ../../../src/waeup/kofa/browser/tests/test_browser.py
   :pyobject: test_suspended_officer


.. _test_handle_clearance:

Handling Clearance by Clearance Officer
---------------------------------------

This test can be found in
`waeup.kofa.students.tests.test_browser.OfficerUITests`. The corresponding use
case is partly described :ref:`elsewhere <rejecting_clearance>`.

.. literalinclude:: ../../../src/waeup/kofa/students/tests/test_browser.py
   :pyobject: test_handle_clearance_by_co


.. _test_handle_courses:

Handling Course List Validation by Course Adviser
-------------------------------------------------

This test can be found in
`waeup.kofa.students.tests.test_browser.OfficerUITests`. The corresponding use
case is described :ref:`elsewhere <course_registration>`.

.. literalinclude:: ../../../src/waeup/kofa/students/tests/test_browser.py
   :pyobject: test_handle_courses_by_ca


.. _test_batch_editing_scores:

Batch Editing Scores by Lecturers
---------------------------------

This test can be found in
`waeup.kofa.students.tests.test_browser.OfficerUITests`. The corresponding use
case is described :ref:`elsewhere <batch_editing_scores>`.

.. literalinclude:: ../../../src/waeup/kofa/students/tests/test_browser.py
   :pyobject: test_handle_courses_by_lecturer

.. _test_manage_hostels:

Manage Hostel
-------------

This test can be found in
`waeup.kofa.hostels.tests.HostelsUITests`. The corresponding use
case is described :ref:`elsewhere <hostels_pages>`.

.. literalinclude:: ../../../src/waeup/kofa/hostels/tests.py
   :pyobject: test_add_search_edit_delete_manage_hostels

.. _test_handle_accommodation:

Bed Space Booking
-----------------

This test can be found in
`waeup.kofa.students.tests.test_browser.OfficerUITests`. The corresponding use
case is described :ref:`elsewhere <bed_tickets>`.

.. literalinclude:: ../../../src/waeup/kofa/students/tests/test_browser.py
   :pyobject: test_student_accommodation
