.. _security_policy:

Security
********

.. seealso::

   :ref:`Security Doctests <security_txt>`

Kofa has a very efficient security machinery. The machinery does not
perform authorization checks on the content objects themselves stored
in the database, but, restricts the usage of views, i.e. web pages and
forms which are needed to view or edit data. Views are protected by
permissions the user must have to use the view. Instead of assigning
permissions seperately to users, permissions are bundled into sets of
permissions, so-called roles which can be assigned to users through
the web interface.

It is important to note that permissions do not include other
permissions. Only roles 'include' permissions. A 'manage' permission,
for example, does not automatically enable users to open pages which
merely display the data. These pages have their own 'view'
permission. Another example is the ManagePortal permission described
below. The name of the permission may lead to believe that users can
do everything with this permissions. This is not true. It does only
give access to certain pages which are dedicated to portal managers
and must not be accessed by any other user.

.. contents:: Table of Contents
   :local:

Permissions
===========

The whole set of permission and role classes are described in the
:py:mod:`Permissions and Roles Module<waeup.kofa.permissions>`. Here
we describe only a subset of permission classes which are essential
for the security settings configuration.

General Permissions
-------------------

.. autoclass:: waeup.kofa.permissions.Public()
   :noindex:

.. autoclass:: waeup.kofa.permissions.Anonymous()
   :noindex:

.. autoclass:: waeup.kofa.permissions.Authenticated()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ManageUsers()
   :noindex:

.. autoclass:: waeup.kofa.permissions.EditUser()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ManagePortal()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ViewAcademics()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ManageAcademics()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ManagePortalConfiguration()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ManageDataCenter()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ExportData()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ImportData()
   :noindex:

.. autoclass:: waeup.kofa.permissions.TriggerTransition()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ShowStudents()
   :noindex:

.. autoclass:: waeup.kofa.reports.HandleReports()
   :noindex:

.. autoclass:: waeup.kofa.reports.ManageReports()
   :noindex:

Applicants Section Permissions
------------------------------

.. autoclass:: waeup.kofa.applicants.permissions.ViewApplication()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.HandleApplication()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.ManageApplication()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.PayApplicant()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.ViewApplicationStatistics()
   :noindex:

Students Section Permissions
----------------------------

.. autoclass:: waeup.kofa.students.permissions.ViewStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.HandleStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.ViewStudentsContainer()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.ManageStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.PayStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.HandleAccommodation()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.UploadStudentFile()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.ClearStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.LoginAsStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.EditStudyLevel()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.ClearStudent()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.ValidateStudent()
   :noindex:

Global Roles
============

Global or site roles are assigned portal-wide. In contrast to local
roles, users have this role in every context.

Many global roles do only bundle one or two permissions. The objective
behind is to share responsibilities and distribute tasks.

Global roles are being assigned via the user manage form page.

Global General Roles
--------------------

.. autoclass:: waeup.kofa.permissions.AcademicsOfficer()
   :noindex:

.. autoclass:: waeup.kofa.permissions.AcademicsManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.DataCenterManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ImportManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ExportManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.ACManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.UsersManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.WorkflowManager()
   :noindex:

.. autoclass:: waeup.kofa.reports.ReportsOfficer()
   :noindex:

.. autoclass:: waeup.kofa.reports.ReportsManager()
   :noindex:

In contrast to these specialized sets of permissions, there are two
sets which delegate extensive powers on portal managers.

.. autoclass:: waeup.kofa.permissions.PortalManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.CCOfficer()
   :noindex:

Global Applicants Section Roles
-------------------------------

Global Applicants Section Roles are assigned portal-wide (globally)
but do actually only allocate permissions in the applicants section.

.. autoclass:: waeup.kofa.applicants.permissions.ApplicantRole()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.ApplicationsOfficer()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.ApplicationsManager()
   :noindex:

Global Students Section Roles
-----------------------------

Global Students Section Roles are assigned portal-wide (globally) but
do actually only allocate permissions in the students section.

.. autoclass:: waeup.kofa.students.permissions.StudentRole()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentsOfficer()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentsManager()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentsClearanceOfficer()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentsCourseAdviser()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentImpersonator()
   :noindex:

.. _local_roles:

Local Roles and Dynamic Role Assignment
=======================================

In contrast to global roles, which are assigned portal-wide, local
role permissions are gained for a specific context.

Some local roles serve a second purpose. At first glance it appears
strange that some of these 'odd' roles do not give more permissions
than the user already has due to other roles. Their real purpose is to
delegate permissions to the students or applicants section. If a user
has for example the LocalStudentsManager role described below at
department level, s/he automatically gets the StudentsManager role for
those students studying in this department. We call this a **dynamic
role**. In contrast to static global or local roles, dynamic roles are
not stored in the database, they are dynamically assigned.

Local roles are assigned either automatically by the system during
user object setup or manually through the web interface. The
automatically assigned local roles are:

.. autoclass:: waeup.kofa.permissions.Owner()
   :noindex:

.. autoclass:: waeup.kofa.applicants.permissions.ApplicationOwner()
   :noindex:

.. autoclass:: waeup.kofa.students.permissions.StudentRecordOwner()
   :noindex:

All other local roles must be assigned manually via context manage form pages.

.. autoclass:: waeup.kofa.permissions.ApplicationsManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.DepartmentOfficer()
   :noindex:

.. autoclass:: waeup.kofa.permissions.DepartmentManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.Lecturer()
   :noindex:

The following local roles do also delegate permissions to the student
section. In other words, dynamic roles are assigned.

.. autoclass:: waeup.kofa.permissions.ClearanceOfficer()
   :noindex:

.. autoclass:: waeup.kofa.permissions.LocalStudentsManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.LocalWorkflowManager()
   :noindex:

.. autoclass:: waeup.kofa.permissions.UGClearanceOfficer()
   :noindex:

.. autoclass:: waeup.kofa.permissions.PGClearanceOfficer()
   :noindex:

.. autoclass:: waeup.kofa.permissions.CourseAdviser100()
   :noindex:
