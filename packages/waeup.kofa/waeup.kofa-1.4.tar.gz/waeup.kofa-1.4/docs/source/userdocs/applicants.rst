.. _applicants_section:

Applicants Section
******************

Applicants and students are different entities and stored in
different places. Moreover, the students section is completely
independent from the applicants section. Kofa can be configured
without its `applicants` module but not without its `students`
module.

Anonymous users can self-register and automatically become
applicants (users) of the portal. The number of applicants is not
limited and, theoretically, Kofa can host hundredthousands of
applicants in various applicants containers. Usually, only a few of
them are beeing accepted for studying at the university. Once the
application process has ended, admitted applicants are transformed
into student records. New student records are created and the data
are copied from the applicant records. When this 'student creation'
process is finished, the applicant records are dispensable. Aim was
to provide an easy way to get rid of the huge batches of applicant
records by only one click, in order to keep the database clean and
tidy. The process is described further below.

.. note::

  The term 'application' has a double meaning in English. An
  'application' in computer sciences stands for a software or web
  application. Software developers may get confused by using the term
  in a different context. To take this into account, we prefer to
  speak of 'applicant' in this documentation, instead of 'application'
  although, in the linguistic context, it sometimes makes more sense
  to speak of the latter. However, in the user interface (UI) and also
  in Python docstrings the term 'application' predominates.

Much like students, applicants are also users of the portal and
the applicant object is a user account surrogate, see
:ref:`Applicants and Students <applicants_and_students>`. In the
following we always refer to the applicant container when talking
about an applicant.

In contrast to student containers, applicant containers do not
contain subcontainers. The only objects they contain are applicant
payment tickets (i.e. instances of `ApplicantOnlinePayment`). Thus
the hierarchy is flat and not really treelike as the students
section. Also, applicants (applicant containers) are stored in
different parent containers (instances of `IApplicantsContainer`).
There is not one single parent container like in the students
section but one container for each application session and
application type::

  Applicants Section (ApplicantsRoot)
  |
  +---> ApplicantsContainer
        |
        +---> Applicant
              |
              +-----> ApplicantOnlinePayment


Interfaces
==========

.. toctree::
   :maxdepth: 3

   applicants/interfaces

Workflow & History
==================

.. toctree::
   :maxdepth: 3

   applicants/workflow

Browser Pages
=============

.. toctree::
   :maxdepth: 3

   applicants/browser


Student Record Creation
=======================

.. toctree::
   :maxdepth: 3

   applicants/create_students

