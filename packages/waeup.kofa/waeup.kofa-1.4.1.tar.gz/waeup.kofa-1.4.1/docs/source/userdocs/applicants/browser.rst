.. _applicant_registration:

Registration
============

The `ApplicantRegistrationPage` allows to register in create or in
update mode, depending on the
:ref:`mode of its context<application_mode>`, i.e. the applicants
container.

In create mode, `firstname`, `middlename`, `lastname`, `email` and
`phone` are requested. An unused record is taken, or a new
record is being created if no unused record is found (see
:ref:`description of application modes <application_mode>`).

In update mode, only `reg_number`, `lastname` and `email` have to be
entered. Kofa searches for an applicant record with matching
registration number and lowercased lastname. If the search does not
yield a result, the flash message: 'No application record found' is
returned. The anonymous user will not know, if the registration
number does not exist or the provided lastname does not match.
Another ``if`` statement checks whether the password has already
been set and used, i.e. the application has already been
started. If so, the anonymous user can't register again and is being
requested to proceed to the login page.

In both registration modes a randomly generated password is set and
the email address is saved. An email with login credentials is sent
to this address. Finally, the browser is redirected to a landing
page. Depending on the portals configuration, the landing page tells
the user that an email has been send to her/his mailbox, or even
discloses additionally the login credentials. The disclosure of
credentials has two substantial drawbacks: (1) The login credentials
can be misused by web crawlers for bulk account creation, which may
cause the system to crash. (2) The email address provided by the
user is not being verified and there is no guarantee that the
address belongs to the user or that a mailbox with such an address
exists. Therefore, we strongly recommend to only send credentials to
email addresses.


.. _container_maintenance:

Preparation and Maintenance of Applicants Containers
====================================================

As described in the :ref:`interfaces chapter <application_mode>`,
applicants containers are aware of their application mode. In update
mode, containers must be pre-filled by import with application
records from an external board. In create mode, the container can
remain empty. Each time an applicant registers, a new record is
being created and a corresponding user account set up. This is the
method of choice, if the number of expected applicants is not very
high (e.g. less than 500). Since each single account creation causes
a significant growth of Kofa's database, we strongly recommend to
pre-fill applicants containers with empty application records, if
the number of expected applicants is higher. Pre-filling is done in
a single transaction and does thus save database volume when
application is ongoing.

During application, many records are being initialized but not used.
For various reasons, many applicants do create one or more
application records with corresponding user accounts but fail to log
in. These records remain in state ``initialized`` and are never
turned to state ``started``. After a while, these records can be
safely removed. When purging an applicants container, also all
unused pre-filled application records are being removed. If
necessary, the container must be pre-filled with empty records again.


.. _application_form_locking:

Form Locking
============

We mentioned regular :ref:`page_locking` mechanisms. The
`ApplicantEditFormPage` has two additional locks. One is the same
named applicant attribute `locked`. Applicants can only enter the
edit page if their record is 'unlocked'. Locking and unlocking is
automatically done by workflow event handlers. By default, the
record is unlocked. Only when the applicant submits the record, it
is being locked, which means the attribute is set ``True`` and the
data can no longer be edited.

The reader may wonder why Kofa is not using the workflow state
instead. The additional locking mechanism allows officers to unlock
and lock forms without triggering workflow transitions. A transition
is always a major, and sometimes inappropriate intervention which is
also recorded in the application history.

Use case: An applicant has made a mistake and requests a change of
submitted data. An officer accepts the change, temporarily unlocks
the form to allow editing the data. Unlocking and re-locking is
logged in ``applicants.log`` but not shown on pages or the
application slip.

The second lock is induced by the application deadline. If the
application period has expired and the applicants container's
`strict_deadline` attribute is set, the applicant is also not
allowed to edit or even submit the form.

.. note::

  A locked-out applicant can still login and access the display pages
  of the recod and also download payment and application slips. To
  expell an applicant from the portal, the account has to be suspended
  by setting the same-named attribute.


.. _applicant_payment_tickets:

Payment
=======

In contrast to the students section, there is no
`PaymentsManageFormPage` to handle payment tickets separately.
Payment tickets can be viewed, added and removed directly on the
applicant manage and edit form pages. Officers can remove all
payment tickets, applicants only those without a response code
(`r_code`) and, if the form is unlocked, so that they are allowed to
edit their data.

As already mentioned in the workflow chapter, making a payment and
redeeming a payment is done in one step. When the payment was
successful or has been approved, also the applicant is automatically
set to state ``paid``. There is no need to redeem the ticket
manually.

