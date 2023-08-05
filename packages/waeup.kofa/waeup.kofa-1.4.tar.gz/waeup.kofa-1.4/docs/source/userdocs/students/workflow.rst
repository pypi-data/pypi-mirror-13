.. _registration_workflow:

Registration Workflow
=====================

Studying at a higher education institution means following
orchestrated and repeatable patterns of activities or, in other
words, following a process workflow prescribed by the school
regulations. This process starts with application for studying a
programme offered by the school, and may end with de-registration of
a student. But even after de-registration, former students can be
kept in the system as alumni so that they can still access their
records or can apply for official transcripts.

Kofa divides these 'repeatable patterns of activities' into two
different and strictly seperated process workflows: an application
and a student registration workflow. The latter, which presupposes
the admission of the student, will be described here.

A worflow defines states and transitions between the states. The
following diagram shows the entire student registration workflow.
Workflow states are connected with dashed lines which symbolize
workflow transitions. There are no arrows at the end of each line
because in most cases, Kofa provides transitions in both directions.
Transitions are denoted by lower-case characters, reverse
transitions additionally by a preceded dash. A few transitions do
not make sense and are thus not available (N/A)::

              a
   created ------- admitted
              b       |
     +----------------+
     |                         e
     +------------------------------------------------------+
     |                  c                            d      |
   clearance started ------- clearance requested  ------- cleared
                                                            |
                                f                           |
     +--------+---------------------------------------------+
     |        |
     | h    school fee paid -------- returning -------------+
     |        |             \   l        |                  |
     +--------+ g            \ _ _ _ m   | k                |
              |                      \   |                  |
           courses registered ------ courses validated      |
                          |      i       |                  |
                          |              | n                |
                          | j            |                  |
                          |          graduated              |
                          |              |                  |
                          |              | o                |
                          |              |                  |
                          |          transcript requested   |
     a: admit             |                                 |
    -a: reset1            +---------------------------------+
     b: start_clearance
    -b: reset2
     c: request_clearance
    -c: reset3 (= reject request)
     d: clear
    -d: N/A
     e: N/A
    -e: reset4 (= annul clearance)
     f: pay_first_school_fee, approve_first_school_fee
    -f: reset5 (= annul payment)
     g: register_courses
    -g: reset7 (= unregister)
     h: pay_pg_fee, approve_pg_fee
    -h: N/A
     i: validate_courses
    -i: N/A
     j: bypass_validation
    -j: N/A
     k: return
    -k: reset9
     l: pay_school_fee, approve_school_fee
    -l: reset6 (= annul payment)
     m: N/A
    -m: reset8 (= annul validation)
     n: N/A
    -n: N/A
     o: request_transcript
    -o: process_transcript


Student registration starts with the first login of the student into
state ``admitted``. After filling the email adress and phone number
field, and also uploading a passport picture, the student
immediately proceeds with the clearance sub-workflow. S/he starts
clearance **(b)** either directly or by using a clearance access
code, depending on the configuration of the portal. After filling
the clearance form and uploading all necessary documents, the
student requests clearance **(c)** which can be either accepted **(d)**
or rejected **(-c)** by a clearance officer. A cleared student
can enter the 'cyclical' part of the workflow which starts after
first school fee payment **(f)**.

A properly registering undergraduate student creates a new study
level (course list) at the beginning of each academic session, adds
the necessary course tickets and finally registers the list **(g)**.
The student's course adviser subsequently validates the list **(i)**,
or rejects the course registration request **(-g)** so that the
student has to register again. Even after validation there is an
option to annul the already validated course list **(-m)** so that
the student can revise the list. At the end of the session, when all
exams have been taken, course results (scores) are either entered by
lecturers or imported by an import officer, a verdict is announced
and the student is finally enabled to return **(k)**. In Kofa the
last two steps are automatically performed by the Verdict Batch
Processor. In some cases, course validators are not available or
course validation is not necessary. Then validation can be skipped
**(j)** by setting `bypass_validation` in the processor's import
file to ``True``. In both cases the student arrives in state
``returning`` but is still in the same session. Also the current
level has not changed. The new session starts only if the student
pays school fee for the subsequent session **(l)**. Then
`current_session` increases by one, `current_level` is set according
to the verdict obtained, the old verdict is copied into
`previous_verdict` and `current_verdict` is cleared. The student has
arrived in the new academic session in state ``school_fee_paid``.
The **gikl** cycle is repeatedly passed through till the student is
ready for graduation.

So far we have spoken about undergraduate students. The same
sequence of transitions also applies to postgraduate students if
they have to pass several levels (e.g. 700 and 800). Very often the
level model does not apply to postgraduates. The students remain in
the same (999) level but pay for each year of studying. In this case
the **gikl** cycle collapses to the **h** cycle. Students may add
course tickets whenever they like, but cannot register their course
list.


.. _registration_workflow_batch_processing:

Workflow Batch Processing
=========================

The :py:class:`StudentProcessor
<waeup.kofa.students.batching.StudentProcessor>` allows to import
either workflow states or transitions. As already emphasized in the
description of the processor class, we refer to them as unsafe and
safe respectively. Transitions are only possible between allowed
workflow states. Only transitions ensure that the registration
workflow is maintained. Setting the workflow state by import is
considered brute and must be avoided.


.. _student_history:

Student History
===============

All transitions are automatically logged in ``students.log``. And
also the import of workflow states is recorded in the logfile.
However, these logfiles can only be accessed by some officers and
are hidden from students. Since Kofa takes up the cause of
transparancy, we are of the opinion, that also students must know,
when and by whom the state of their record was changed. Therefore we
store all workflow-relevant changes additionally in the student
history which is attached to the student object. The history is a
list of messages. Each message contains the local time, the workflow
transition message and the public name of the user who triggered the
transition, either online or by import::

  2015-05-16 05:11:34 UTC - Record created by System Admin
  2015-05-30 07:34:09 UTC - Admitted by System Admin
  2015-05-30 08:34:11 UTC - Clearance started by John Doe
  2015-05-30 09:34:15 UTC - Clearance requested by John Doe
  2015-05-30 10:37:27 UTC - Cleared by Clearance Officer

If the workflow state is set by import, the following message would
have been added instead::

  2015-05-30 10:37:27 UTC - State 'cleared' set by Import Officer

Student histories are exportable but cannot be imported.