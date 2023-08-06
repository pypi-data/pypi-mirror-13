.. _application_workflow:

Application Workflow
====================

For an introduction see :ref:`registration_workflow`. The already
mentioned application workflow is shown here::

            initialized
             |
             |a
             |
    +--+--- started ----------------------+
    |  |     |                            |
    |  |     |b                           |
    |  |     |                            |
    |  |h   paid   +-- processed          |
    |  |     |     |                      |
   i|  |     |c    |k                     |
    |  |     |     |                      |
    |  +--- submitted ---------+          |
    |        |                 |          |
    |        |d                |e         |
    |        |         g       |          |
    +------ admitted ----- not admitted --+
             |
             |f
             |
            created


   a: start          -a: n/a
   b: pay, approve   -b: reset1
   c: submit         -c: reset2
   d: admit          -d: n/a
   e: refuse1        -e: n/a
   f: create         -f: n/a
   g: refuse2        -g: n/a
   h: n/a            -h: reset3
   i: n/a            -i: reset4
   j: n/a            -j: reset5
   k: process        -k: n/a

Application starts with the creation of the applicant record, either
by an anonymous user or by import. The first state is
``initialized``. After first login, the state turns to ``started``
**(a)**. Now the applicant is requested to fill the form, upload a
passport picture and create a payment ticket. In contrast to student
payments, making a payment and redeeming a payment is done in one
step. Not only the ticket is marked ``paid``, but also the applicant
is automatically set to state ``paid`` **(b)**. After successful
payment the student can directly submit the application request
**(c)**. Submitted records can be either sent back for editing and
resubmission **(-c)**, accepted with admission confirmed **(d)** or
accepted with admission refused **(e)**. Only applicant records
with confirmed admission into the university can be transormed into
student records. This final and **irreversible step** is accompanied
by a transition to state ``created`` **(f)**.

Submitted records can also be marked ``processed`` **(k)** in case
the application module is used for other kinds of application
processes which have nothing to do with student admission, e.g.
transcript application or late payments by alumni.


.. _application_history:

Application History
===================

All transitions are automatically logged in ``applicants.log`` and the
applicant's history. And also the import of workflow states is
recorded in the logfile and the history, see :ref:`student_history`
for further information. This is a sample history of an applicant
which passes through the application process without any
complications::

  2015-06-23 08:56:23 UTC - Application initialized by Anonymous
  2015-06-23 08:57:42 UTC - Application started by Demo Applicant
  2015-06-23 08:59:41 UTC - Payment approved by Benny Goodman
  2015-06-23 09:00:50 UTC - Application submitted by Demo Applicant
  2015-06-23 09:01:13 UTC - Applicant admitted by Benny Goodman
  2015-06-23 09:02:36 UTC - Student record created (K1000003) by Benny Goodman

Benny Goodman is the name of an applications manager. If the
workflow state is set by him by import, the following message would
have been added instead::

  2015-06-23 09:01:13 UTC - State 'admitted' set by Benny Goodman

Applicant histories are exportable but cannot be imported.