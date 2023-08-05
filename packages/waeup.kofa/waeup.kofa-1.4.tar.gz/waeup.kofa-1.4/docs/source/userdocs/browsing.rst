.. _browsing_kofa:


Browsing Kofa
*************

The reader may ask: How do officers, applicants and students browse
the portal? Where are the step-by-step operating instructions on how
to use Kofa? We are always tempted to answer: The menu navigation
should be self-explanatory and it's quite easy to follow the menu
prompts or flash messages which appear above page titles in a green,
yellow or red box. This answer seems a bit over the top. We must
indeed describe some browser pages and what their clickable actions
are doing with the data. The reason is, that a lot of Kofa's
functionality is embedded in view and utility methods and not only
provided by the functionality of content components. In the
following, functionality of pages is described in subchapters called
'Browser Pages'.


.. _page_layout:

Page Layout
===========

Kofa makes use of two different `Bootstrap`_ layouts. Anonymous
users, students and applicants do see a single-column theme with
only a static top navigation bar. Students can navigate to the
various display form pages of their record by pulling down the 'My
Data' tab in the navigation bar.

.. _navigation_bar:

The navigation bar for an anonymous user:

.. image:: images/navbar_anon.png

The navigation bar for a student with drop-down menue:

.. image:: images/navbar_student.png

The navigation bar for an officer with lots of permissions:

.. image:: images/navbar_officer.png

Officers see a double-column theme after logging in. The left column
contains a box (side box) which provides links to the user's
preferences (My Preferences) and roles (My Roles). It also contains
links to the various sections of Kofa, depending on the permissions
the officer has obtained. Possible sections are: 'Portal
Configuration', 'Officers', 'Data Center', 'Reports' and 'Access
Codes'. The side box expands, when the officer accesses a student
record. The box gives direct access to the pages of the student.

.. image:: images/multicolumn.png


.. _views_pages:

Views, Pages and Form Pages
===========================

Views are dealing with request and response objects. Usually a view
renders (produces) HTML or PDF code to be displayed in a web browser
or a pdf reader respectively. Very often a view only redirects to
another view or page and does not render code by itself.
Views, which render pdf code, are called pdf slips in Kofa.

Kofa pages are 'layout-aware' browser views, which means they know
about the global page layout and render content inside it.

In Kofa most pages are form pages which means they are layout-aware
views on data. These pages are either used to submit data (simple form
page), or to display, edit or add persistant data. The latter three
are called display, edit or add form pages respectively. Kofa is
using the `Zope Formlib`_ package to auto-generate these forms.

.. note::

  Briefly, Zope Formlib is wedded to `Zope Schema`_, it provides
  display and input widgets (= views) for the fields defined in the
  Zope Schema package. Auto-generation is done with `grok.AutoFields`
  which takes the fields, declared in an
  :ref:`interface<kofa_interfaces>`, and renders display or input
  widgets, according to the schema declaration, for display or edit
  forms respectively.

Whereas display and add form pages are usually shared by officers
and students, edit form pages are not. Applicants and students are
not allowed to edit all of their data all the time. Edit access is
restricted by workflow states or other conditions. Officers' access
is much less restricted, and we therefore speak of 'managing'
instead of 'editing' data. In most cases, Kofa uses two different
form pages which require different permissions: An `EditFormPage`
requires the
:py:class:`HandleApplication<waeup.kofa.applicants.permissions.HandleApplication>`
/
:py:class:`HandleStudent<waeup.kofa.students.permissions.HandleStudent>`
permission and a `ManageFormPage` requires the
:py:class:`ManageApplication<waeup.kofa.applicants.permissions.ManageApplication>`
/
:py:class:`ManageStudent<waeup.kofa.students.permissions.ManageStudent>`
permission.


.. _page_locking:

Page Locking
============

As mentiond above, the right to use a form depends on the
permissions the user gained. But this is not sufficient. Applicants
and students always have the permission to handle their data
although they are not allowed to edit the data all the time.
Access to forms has to be further restricted. This is always done in
the `update` method of a page. If an applicant or student doesn't
meet the additional conditions defined in this method, s/he is
immediately thrown out and redirected to another page. In most cases,
the allowance to modify data depends on the workflow state of an
applicant or student.


.. _action_buttons:

Action Buttons
==============

There are two kinds of action buttons which appear on pages:

**Link Buttons** appear on top of the page above the page
title and are decorated with an icon. These
:py:class:`action
buttons<waeup.kofa.browser.viewlets.ActionButton>` have a
link target which means they usually refer to another Kofa
page and are sending GET requests to open the page. Example:

.. image:: images/link_button.png
   :scale: 50 %

**Form Buttons** are submit buttons which appear below a form.
They are HTML form actions which submit data by sending a
POST request back to the form page. A form page method is
called and processes the data or simply redirects to
another Kofa page. Example:

.. image:: images/form_buttons.png
   :scale: 50 %



.. _bootstrap: http://getbootstrap.com/

.. _zope schema: http://docs.zope.org/zope.schema

.. _zope formlib: http://bluebream.zope.org/doc/1.0/manual/schema.html#auto-generated-forms-using-the-forms-package