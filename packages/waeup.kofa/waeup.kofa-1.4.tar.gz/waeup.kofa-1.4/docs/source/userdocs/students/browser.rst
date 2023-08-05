.. _logging_in_as_student:

Impersonate Students
====================

Officers with
:py:class:`LoginAsStudent<waeup.kofa.students.permissions.LoginAsStudent>`
permission do see a 'Login as student' button on student display
pages which redirects to a page, where a temporary student password
can be set by clicking a 'Set password now' form button. The
temporary password is valid for 10 minutes. During this period the
student can't login. The officer is being redirected to a login page
which allows to directly login as student with pre-filled temporary
credentials. The second page is to avoid that officers must remember
the student credentials, have to logout from their own account and
manually login as student via the regular login page. After 10
minutes the officer is automatically thrown out and the student is
able to login again (if the officer hasn't changed the password).
Attention: When logging in as student, the officer really
impersonates the student. All actions are logged with the student id
and not with the officer's user id. However, start of student
impersonation is also logged, so that officers can be identified and
fraudulent use can be discovered.


.. _starting_clearance:

Starting Clearance
==================

When students start the clearance process, Kofa checks if the
passport picture has been uploaded and the email address field as
well as the phone number field filled. If not, students can't
proceed with clearance.


.. _rejecting_clearance:

Rejecting Clearance
===================

When a clearance officer clicks the 'Save comment and reject
clearance now' button, the `reject` action method of the
:py:class:`StudentRejectClearancePage<waeup.kofa.students.browser.StudentRejectClearancePage>`
is called. This method first checks, in which workflow state the
student is, and fires a transition accordingly. Then the comment,
which should explain why the request was requested, is saved twice
in the `officer_comment` attribute of the student and in
``students.log``. As soon as the `clear` transition (d) is effected,
an event handler clears the attribute again. The logfile message is
permanent and ensures that the original cause of rejection can
always be reconstructed.

Finally, the method redirects to the `ContactStudentFormPage` and prefills
the HTML form with the comment previously saved. The clearance
officer can leave the comment as it is, or can modify the text to
give more information about the reason of rejection. This comment
will then be sent to the student by email. This comment is not saved,
neither in the student object nor in the logfile.

.. important::

  All messages sent via Kofa contact forms are private. They are
  neither stored in the database nor in any logfile. The emails are
  also not forwarded to any other email address. Thus senders and
  recipients can be sure that nobody else is eavesdropping and the
  correspondence is kept secret.

.. seealso::

  :ref:`Clearance Handling Doctests <test_handle_clearance>`


.. _transferring_students:

Student Transfer
================

Transferring a student means enabling the student to study another
programme.

The simple but dirty way is to select another certificate and adjust
study course attributes accordingly. Existing study levels can be
either removed or, in case registered courses can be credited, left
as they are. This simple way is tedious and also dangerous, because
changes are not tracable. Only the logfile can tell us, that an
officer has edited the student's data. The data of the previous
study course are not backed up. They are lost.

Kofa provides a more adequate, cleaner and tracable way of
transferring students. It can make a backup of the entire study
course container and create a new and empty container for the new
study programme with only one click or even by batch processing.

After clicking the 'Transfer student' button the
`StudentTransferFormPage` opens and asks for the new certificate,
current session, current level and current verdict. After submitting
this form, the student transfer method checks if the old study
course is complete and ready for transfer. It also checks if the
number of possible transfers is not exceeded. Kofa allows two (2)
transfers! Finally the copying process is started and history and
logfile messages are added.

The old study course container(s) can still be accessed via links on
the current study course display form page. But, they can neither be
edited, removed, exported or reimported.


Batch Transferring Students
---------------------------

Sometimes students of an entire study programme have to be
transferred to another programme. This can be done with the
:py:class:`StudentStudyCourseProcessor<waeup.kofa.students.batching.StudentStudyCourseProcessor>`.
The import file must contain the following columns: `student_id`
(or any other locator), `certificate`, `current_session`,
`current_level` and `entry_mode`. Do not import `entry_session`. A
transfer is automatically initialized if the `entry_mode` value is
``transfer``.


Reverting Previous Transfers
----------------------------

Previous transfers can be reverted by opening the previous study
course and clicking the 'Reactivate this study course (revert
previous transfer)' button. This is a complete rollback of the last
transfer. The current study mode will be irrevocably deleted and
replaced by the previous study course. The second last study course
will become the previous study course.


.. _student_payment_tickets:

Payments
========

The `PaymentsManageFormPage` is used by both students and students
officers. The page tabulates existing payment tickets and allows to
add or remove tickets. Officers can remove all payment tickets,
students only those without a response code (`r_code`). Attention:
Students can remove tickets without response code even if they have
been marked paid.

There are three different add form pages to add
`StudentOnlinePayment` instances (= payment tickets). They all
create objects of the same type, only their attributes are set
differently.


Current Session Payment Tickets
-------------------------------

Current session payments are the regular payments which have to be
made in each session to proceed to the next registration step. The
add form provides a select box of available payment categories
(`p_category`). After submitting the form, Kofa determines the total
amount and sets attributes like payment item (`p_item`), payment
session (`p_session`) and payment level (`p_level`) automatically.
The Boolean `p_current` attribute is set ``True``. The creation
datetime is stored in the `creation_date` attribute and is also used
to construct the unique payment id (`p_id`).

.. note::

  Kofa always determines the total amount, including any fees charged
  by the school and its service providers. This is the amount which is
  authorized by students and finally submitted to one of the payment
  gateways. No fees can be added once the payment ticket is created.
  Payment tickets do not store any information about charged fees.


Payment Ticket Redemption
-------------------------

Directly after a student payment ticket has been paid - either by
approval by an officer or by receiving a positive response from a
payment gateway - the
:py:meth:`redeemTicket<waeup.kofa.students.payments.StudentOnlinePayment.redeemTicket>`
method is called. Depending on the category of the payment, an
appropriate access or activation code is beeing created for the
owner of the ticket. This code must be entered on certain form pages
to activate the paid service or to access the next stage of the
registration process. In other words, making a payment and redeeming
a payment are two different steps. Successful payments do not
automatically trigger any action in the portal but create a specifc
access code which can be used to trigger access-code-related actions
(see :ref:`accesscodes`).

Until May 2015 also school fee payments had produced access codes,
which enabled students to start the next session. Since software
revision 12889, Kofa bypasses SFE access code creation and starts
the next session automatically.


Previous Session Payment Tickets
--------------------------------

Previous session payments are additional payments which do not
induce further actions in Kofa. Their sole purpose is to enable
students to pay for services in previous sessions which they missed
to pay. The add form for previous session payments allows the
student to select the payment category, session and level by
him/herself.


Balance Payment Tickets
-----------------------

Balance payments have been introduced to correct previously made
payments. In some cases, students select the wrong payment category,
or other things may have happened which led students pay less than
expected. This can be balanced by paying a differential amount.
Therefore, the add form for balance payments allows to freely choose
the total amount to be paid. It also asks for the category, the
session and the level the payment is meant for. Like previous
session payments, balance payments do not induce further actions in
Kofa. Both can be omitted in customized versions of Kofa if these
features are not needed.

.. _course_registration:

Course Registration
===================

Study levels are pre-filled with course tickets. When adding a study
level,
:py:meth:`StudentStudyCourse.addStudentStudyLevel<waeup.kofa.students.studycourse.StudentStudyCourse.addStudentStudyLevel>`
automatically adds course tickets in two steps:

1.  :py:meth:`StudentStudyLevel.addCertCourseTickets<waeup.kofa.students.studylevel.StudentStudyLevel.addCertCourseTickets>`
    is called which iterates over the certificate courses of the
    certificate container object in the academic section and creates
    course tickets if the `level` attribute matches. `title`, `fcode`,
    `dcode`, `credits`, `passmark` and `semester` are copied from the
    course object which is attached to the certificate course;
    `mandatory` is taken from the certificate course itself. Finally,
    `automatic` is set to ``True`` and `carry_over` to ``False.``

2.  The portal can be configured
    (`IConfigurationContainer.carry_over`) such that failed courses are
    automatically carried over from one session to the next. Failed
    course tickets from the previous level, i.e. tickets with a score
    below the passmark, are collected and 'copied' into the current
    study level container. The attributes `automatic` and `carry_over`
    are set to ``True``.

In most cases such an automatically created course list is not
perfect or even ready for submission to the course adviser. The list
must be edited according to the student's needs. Students can select
further courses, which they desire to attend, and can create
additional course tickets, as long as the total number of credits do
not exceed 50 (value customizable). Course tickets can also be
removed. Whereas officers can remove any ticket from the list,
students can remove only optional (non-mandatory) course tickets
(condition customizable).

The edit form page provides a 'Register course list' button which
submits the course list to the course adviser for validation. If the
course registration deadline
(`ISessionConfiguration.coursereg_deadline`) is set and the
registration period has expired, a late registration fee
(`ISessionConfiguration.late_registration_fee`) is charged. This
payment has to be made first, otherwise a warning message appears in
the browser.

Course advisers can't edit the registered/submitted course list, but
they can validate or reject it by pressing the same-named link
buttons. After pressing the 'Reject courses' button, Kofa redirects
to the `ContactStudentFormPage` which can be used to inform the student
about the reason of rejection. In contrast to clearance rejection,
the message, which is being sent to the student by email, is neither
stored in the database nor in the logfiles.

.. seealso::

  :ref:`Course List Validation Doctests <test_handle_courses>`


.. _batch_editing_scores:

Batch Editing Scores by Lecturers
=================================

Lecturers cannot access student records directly. They don't have
access to the students section. Instead, lecturers go to their course
in the academic section and view or export lists of students who
attended the course, either in a previous or in the current session.
They do also see an 'Update scores' link button which opens the
`EditScoresPage` if score editing is enabled for that department
(`IDepartment.score_editing_disabled`) and
`IConfigurationContainer.current_academic_session` has been set on
the portal's configuration page. The `EditScoresPage` lists all
students, who are attending the course in the current academic
session. Score editing is allowed if the student's current session
corresponds with the current academic session and the student is in
state 'courses validated', see method
:py:meth:`CourseTicket.editable_by_lecturer<waeup.kofa.students.studylevel.CourseTicket.editable_by_lecturer>`.

.. seealso::

  :ref:`Batch Editing Scores Doctests <test_batch_editing_scores>`


.. _bed_tickets:

Bed Tickets
===========

.. _bed_allocation:

Bed Allocation
--------------

Students can obtain a bed ticket if a series of conditions is met:

- The current date must be inside the booking period (between
  `IHostelsContainer.startdate` and `IHostelsContainer.enddate`).

- The student's current session must match the accommodation session
  (`IHostelsContainer.accommodation_session`).

- A bed ticket for the same accommodation session does not exist.

- The student must be in the correct workflow state
  (`IHostelsContainer.accommodation_states`).

- A bed type, which fits to the student, can be determined.

- A bed of that type is available.

- The HOS activation code is not yet used.

- The student is the owner of the activation code.

The customizable utility method
:py:meth:`getAccommodationDetails<waeup.kofa.students.utils.StudentsUtils.getAccommodationDetails>`
composes a bed type string. Three criteria are checked: Is the
student a new, a returning or a final year student? Is the student
female or male? Has the student to be accommodated in a special
hostel (`IHostel.special_handling`)? The resulting bed type string
contains these information. Example: ``regular_female_fr`` means
that a bed for a new female student in a regular hostel is wanted.
If the student record allows to determine such a bed string, Kofa
starts searching a proper bed space.

Before Kofa searches for a free bed space, which meets the bed type
criteria above, it checks if a bed space has already been allocated
manually to the student. If so, then this bed is used, no matter
whether the bed meets the criteria or not. (Theoretically, a male
student can be accommodated in a hostel which is reserved for female
students.) If no manually allocated bed space is found, Kofa
searches for the right space. If bed booking is subject to a charge,
Kofa also checks, if the student has entered a valid activation code,
before delivering the bed coordinates to the student.


.. _student_relocation:

Student Relocation
------------------

Officers with `ManageHostels` permission do see a 'Relocate student' link
button which calls the `BedTicketRelocationView`. This view relocates the
student if student parameters or the bed type of the bed have changed. The
`update` method of this view calls the
:py:meth:`BedTicket.relocateStudent<waeup.kofa.students.accommodation.BedTicket.relocateStudent>`
method which checks first, if the student has a 'reserved' bed space.
Students in reserved beds are never subject to relocation. It checks secondly,
if booking has been cancelled in the accommodation section but other bed space
has been manually allocated after cancellation. Then this bed is used, no
matter whether the bed meets the bed type criteria or not. If both checks are
negative, Kofa searches for a free bed space, which meets the student's bed
type criteria. Only if it finds a new and free bed space, it starts the
relocation process by releasing the old bed, booking the new bed and
designating the new bed in the bed ticket.

.. seealso::

  :ref:`Bed Space Booking Doctests <test_handle_accommodation>`
