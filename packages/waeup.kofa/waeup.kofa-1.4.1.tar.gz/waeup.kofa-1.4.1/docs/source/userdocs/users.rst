.. _users:

Users
*****

Kofa distinguishes between four types of users: anonymous users,
applicants, students, portal officers/managers and the Zope manager.
Kofa distinguishes further between authenticated and unauthenticated
users and between users with and without account object.

The user authentication process in Kofa is quite complex. Briefly
and in simple terms, a so-called authenticator (plugin) validates
the credentials provided via the login form, fetches the matching
account object, extracts the account data and finally leads to the
creation of a temporary user object, a so-called principal. Kofa
principals provide `name`, `title`, `email`, `phone`, `public_name`
and `user_type` attributes.


Anonymous
=========

Anonymous users do not authenticate and thus do not provide
credentials. Their user id in logfiles is always ``zope.anybody``.
These users gain two permissions: :py:class:`Anonymous
<waeup.kofa.permissions.Anonymous>` and :py:class:`Public
<waeup.kofa.permissions.Public>`.

Only a few actions of anonymous users are logged. These are payment
data webservice requests, the execution of password mandates and the
self-registration of applicants.

.. _applicants_and_students:

Applicants and Students
=======================

Logged-in applicants or students are regular authenticated Kofa
users. Their user account object is an adaption of their
applicant/student object. More precisely, the Applicant/Student
authenticator fetches the matching applicant/student object and
turns it on-the-fly into a Kofa account object which is further used
for creating a principal instance. The `applicant_id`/`student_id`
attribute becomes the user name and the `display_fullname` property
serves as user title.

.. _officers:

Officers
========

.. seealso::

   :ref:`Officers Doctests <userscontainer_txt>`

   :ref:`Officers Python Test <test_suspended_officer>`

Officers are users with a dedicated user account object stored in the
``users`` container (of type :py:class:`UsersContainer
<waeup.kofa.userscontainer.UsersContainer>`) which is located in Kofa's root
container. The account object has three more attributes than the principal
instance which is created from the account data: (1) a `suspended` attribute
which allows to deactivate an account, (2) a `roles` attribute which is a list
of global role names assigned to the officer, and (3) a private `_local_roles`
attribute which maps local role names to lists of objects the respective local
role applies to. This information is important because local role assignment
is originally stored only with the objects the role applies to and not with
the user who got the role. When removing an officer, Kofa iterates over the
mapping and the list of objects in order to remove all these local role
assignments denoted in the mapping.

The management of portal officers is done in the 'Officers' section
of Kofa. The management page shows all officers registered in the
portal together with their global and local roles. The table can be
easily sorted or filtered. Deactivated officer accounst are marked
``(suspended)``.


Manager
=======

There is one and only one manager account (user id ``zope.manager``)
in Kofa. The manager has access to the root instance of the Kofa
application which has its own user interface (see screenshot below).
Through this 'Grok UI' the manager can access some basic functions
to manage the database and also access the Kofa user interface.

.. image:: images/Grok_UI.png

Although the manager automatically gains all permissions the system
defines, this real superuser (or emergency user) neither has an
account in Kofa nor can access Kofa through its regular login page.
The manager has to enter the portal through the Grok UI which
usually ony runs on a localhost port, for example
``http://localhost:8080``.
