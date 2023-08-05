.. _applicants_interfaces:

Parent Containers Interfaces
============================

`IApplicantsRoot`
-----------------

Much like ``academics`` and ``students``, also ``applicants`` is a
unique container (of type `ApplicantsRoot`) located in the
`IUniversity` instance. It is the counterpart of the students
(section) container. The root container has a `description` schema
field attribute which contains human readable, multi-lingual
information about the application procedure in HTML format. This
description can be seen by anonymous users, when they enter the
applicants section (by pressing the 'Application' tab in the
navigation bar).

.. _multilingual:

.. note::

  A multi-lingual or localized text is a sequence of human-readable
  text strings in different languages. The languages must be separated
  by ``>>xy<<``, whereas ``xy`` is the language code. Text parts
  without correct leading language separator - usually the first part
  has no language descriptor - are interpreted as texts in the
  portal's language. The text strings can be either HTML or
  reStructuredText (REST) formatted.

.. literalinclude:: ../../../../src/waeup/kofa/applicants/interfaces.py
   :pyobject: IApplicantsRoot

`IApplicantsContainer`
----------------------

The applicants root contains the various `ApplicantsContainer`
objects and is also a configuration object.

.. literalinclude:: ../../../../src/waeup/kofa/applicants/interfaces.py
   :pyobject: IApplicantsContainer

`statistics` and `expired` are read-only property attributes.
`description_dict` contains the same information as the
`description`, but the sequence of language translations has been
split up and copied into a dictionary for faster processing. 

Crucial for application are the `prefix`, `year`, `mode` and
`application_category` schema fields. The `prefix` atribute can only
be set when adding a container. It cannot be edited afterwards. The
attribute determines the application type and automatically sets the
prefix of the container code and of all applicant ids inside the
container. The prefix is supplied by the `ApplicationTypeSource`
(see `application types of base package
<https://kofa-demo.waeup.org/sources#collapseAppTypes>`_). It is
followed by the year of entry. Thus, the identifiers of applicants
containers and the applicants inside the containers start with the
same prefix-year sequence. Example: ``app2015`` which translates
into 'General Studies 2015/2016'. Consequently, **applicants cannot
be moved from one container to another.**

.. _application_mode:

The application mode is either ``create`` or ``update``. In **create
mode** the container can be either left empty or it can be
pre-filled with fresh and 'unused' records. In the first case,
records are being created after submission of the first form. In the
second case, unused record are fetched and filled with the form
data. In both 'create mode' cases, applicants are requested to
provide all data needed, including their name details. In **update
mode**, the applicants container must have been pre-filled by import,
e.g. with records provided by an external board. These records are
called 'used' since they already contain data. Applicants can't
create new records in update mode, they can only open and take
possession of existing records.

The application category is supplied by the
`ApplicationCategorySource` (see `application categories of base
package <https://kofa-demo.waeup.org/sources#collapseAppCats>`_) and
refers to a group of study programmes (certificates) which the
applicant can apply for, read also chapter on :ref:`Certificates
<certificate>`.

Applicant Interfaces
====================

As already mentioned, the applicant objects contains all information
necessary for application, except for the payment ticket data. The
base set of the applicant's 'external behaviour' is described by the
following interface.

`IApplicantBaseData`
--------------------

.. literalinclude:: ../../../../src/waeup/kofa/applicants/interfaces.py
   :pyobject: IApplicantBaseData

As usual, the interface lists attributes first. Except for the
last two attributes (`password` and `application_date`), they are all
read-only property attributes, i.e. attributes with a getter method
only. These properties are computed dynamically and can't be set.

`IApplicant`
------------

In the base package `IApplicant` is derived from `IApplicantBaseData`
and only two methods are added:

.. literalinclude:: ../../../../src/waeup/kofa/applicants/interfaces.py
   :pyobject: IApplicant

In custom packages we have furthermore interfaces for undergraduate
and postgraduate students, both derived from `IApplicantBaseData`.

Then there is a customized interface `ISpecialApplicant` for former
students or students who are not users of the portal but have to pay
supplementary fees. This reduced interface is used in browser
components only, it does not instantiate applicant objects.

Applicant Payment Interfaces
============================

`IApplicantOnlinePayment`
-------------------------

Instances of this interface are called applicant payment tickets.
They contain the data which confirm that the applicant has paid the
application fee.
`waeup.kofa.students.interfaces.IStudentOnlinePayment` inherits from
`waeup.kofa.payments.interfaces.IOnlinePayment` and promises three
additional methods which process the applicant data after successful
or approved payment.

.. literalinclude:: ../../../../src/waeup/kofa/applicants/interfaces.py
   :pyobject: IApplicantOnlinePayment
