.. _configuration:

Portal Configuration
********************

There are many places in Kofa where portal parameters can be set or
page descriptions can be added. These parameters are attributes of
either dedicated configuration objects or of containers in the
academics, applicants or data center sections. The latter have been
described elsewehere. Here we explain the interfaces of the
configuration section.

Technically speaking, the portal configuration section is a
container of type `ConfigurationContainer` with id ``configuration``
which contains session configuration subobjects::


  Portal Configuration (ConfigurationContainer)
  |
  +--->SessionConfiguration

Much like ``academics``, ``students``, ``applicants``, ``hostels``
and ``documents``, also ``configuration`` is a unique container
which is located in the `IUniversity` instance.

Site Settings
=============

Site parameters are the attributes of the configuration container to
be set via the `ConfigurationContainerManageFormPage`. The page
opens, if an officer with
:py:class:`ManagePortalConfiguration<waeup.kofa.permissions.ManagePortalConfiguration>`
permission clicks the 'Portal Configuration' link in the side box.

The `ConfigurationContainer` class implements exactly one interface:


.. literalinclude:: ../../../src/waeup/kofa/interfaces.py
   :pyobject: IConfigurationContainer

The page furthermore lists containing session configuration objects
and allows to add them.

Session Settings
================

Session parameters are the attributes of session configuration
objects. These parameters may vary between academic sessions.
Particularly student fees, which often vary from one session to the
next, can be configured here, if the portal has been customized
accordingly, see :ref:`customization` below. The session
configuration objects also serve to:

- disable student payments for certain payment categories and
  subgroups of students

  See also `Disable Payment Groups
  <https://kofa-demo.waeup.org/sources#collapseDisablePaymentGroups>`_
  in the base package.

- disable clearance by clearance officers for the selected session

  If clearance is disabled, students can still fill and submit the
  clearance form, but clearance officers can't process the clearance
  requests afterwards. They can neither clear these students nor
  reject their clearance request.

- set the course registration deadline

  If the course registration deadline is set, student can't register
  courses unless they pay the late registration fee.

Session configuration objects implement the following interface:

.. literalinclude:: ../../../src/waeup/kofa/interfaces.py
   :pyobject: ISessionConfiguration
