.. _logging:

Logfiles
********

Kofa logs actions, which cause changes to the database or the
filesystem, in separate human-redable event logfiles. Nearly all
actions are being logged, except some actions committed by
applicants and students during registration periods. During these
data initialization periods, applicants and students are requested
to edit many fields. Usually they press the 'Save' button quite
often to backup the data entered so far. Logging all these changes
would mean filling the logfiles with more or less useless or
redundant information.

The main purpose of Kofa's logging facilities is to trace changes
effected by portal officers. Applicants and students can only access
their own data. They don't have the permission to change anything
else. Whereas portal officers bear responsibility for the integrity
of the whole database. Depending on the roles they have, officers
can add, edit or remove application and study data without leaving a
trace in the object database itself. Kofa closes this security gap
by recording nearly all actions of portal officers into various
event logfiles.

.. note::

  Kofa logs the changing but not the viewing of data (except
  downloading export files or reports). Also entering (login) end
  leaving (logout) the portal is **not** being recorded.

Critics may claim that extensive logging may discourage officers
from working with the portal. Persons in key functions often don't
want to be controlled or supervised by anybody else. Indeed, Kofa
does not respond to the desire for this kind of privacy. Datacenter
managers can search all logfiles and can even see what their
principles have done with the data. Goal behind is **transparency
and security**, i.e. transparent data processing and reduction of
the vulnerability to corruption combined with cutting-edge
technologies to protect the data against attacks from outside.

Logfiles can not be accessed directly. They can neither be
downloaded nor viewed entirely online. But the files can be searched
online for arbitrary `regular expressions`_. The simplest regular
expression is a single word or a string. A technical description,
how logfiles are being querried, can be found
:py:meth:`here<waeup.kofa.datacenter.DataCenter.queryLogfiles>`.

Each line in the logfile means a single log entry. It is composed of
four parts: a datetime string, the log level (mainly 'INFO'), the id
of the logged-in user, and a message part. Depending on the module,
the message part is subdivided into further parts which are
described below.


main.log
========

All actions in the academic section are logged in ``main.log``.
Changes of faculties, departments, certificates, courses and
certificate courses done via pages in the user interface (browser
page) are recorded in the following form::

  2014-12-11 13:09:22,855 - INFO - admin - browser.pages.DepartmentAddFormPage - added: FAC1/DEP1
  2014-12-11 13:19:31,755 - INFO - admin - browser.pages.DepartmentManageFormPage - DEP1 - saved: title
  2014-12-12 13:19:43,255 - INFO - admin - browser.pages.FacultyManageFormPage - removed: DEP1

The message part is composed of the browser page name and the action
taken. In the example above a department ``DEP1`` was added on
December 11, 2014 by user ``admin`` in faculty ``FAC1``, the title
was changed 10 minutes later and, finally, the department was
entirely removed one day later. In the same way user data and
configuration data are logged in the main logfile. Examples::

  2015-04-01 08:33:47,474 - INFO - admin - browser.pages.UserManageFormPage - Test edited: roles
  2015-04-27 09:39:24,073 - INFO - admin - browser.pages.SessionConfigurationAddFormPage - added: 2014

Furthermore, ``main.log`` does contain information about reports::

  2015-04-28 15:34:31,852 - INFO - admin - students.reports.student_statistics.StudentStatisticsReportGeneratorPage - report 3029 created: Student Statistics (session=1989, mode=All, breakdown=faccode)
  2015-04-28 15:34:37,698 - INFO - admin - students.reports.student_statistics.StudentStatisticsReportPDFView - report 3029 downloaded: StudentStatisticsReport_1989_1990_All_2015-04-28_13-34-36_UTC.pdf
  2015-04-28 15:36:30,106 - INFO - admin - browser.reports.ReportsContainerPage - report 3029 discarded

the management of documents::

  2015-01-09 17:30:49,819 - INFO - admin - HOWTO - Document created
  2015-01-09 17:30:49,822 - INFO - admin - documents.browser.DocumentAddFormPage - added: REST Document HOWTO

password change requests and the usage of password mandates::

  2015-04-28 13:42:52,753 - INFO - zope.anybody - browser.pages.ChangePasswordRequestPage - B1234567 - myname@gmail.com
  2015-04-28 13:43:51,056 - INFO - zope.anybody - PasswordMandate used: B1234567

``zope.anybody`` is the user id of anonnymous (non-logged-in) users.

Some log entries do not contain information about a browser page.
These entries were generated deeper in the system. The ``Document
created`` entry, for example, was added by a workflow transition.
The ``PasswordMandate used`` entry was added by
:py:meth:`waeup.kofa.mandates.mandate.PasswordMandate.execute` and
not directly by the browser page which calls this method
(:py:meth:`waeup.kofa.mandates.browser.MandateView.update`).

``main.log`` is also the place where plugins store information about
system upgrades. If catalogs have to be re-indexed or new attributes
of objects have to be initialized, a corresponding message is stored
in the main logfile.


datacenter.log
==============

All actions in the data center (uploading, processing, downloading
and deleting of files) are logged in ``datacenter.log``::

  2015-04-29 06:52:23,483 - INFO - admin - browser.pages.DatacenterUploadPage - uploaded: /kofa/trunk/var/datacenter/users_admin.csv
  2015-04-29 06:52:44,025 - INFO - admin - processed: /kofa/trunk/var/datacenter/users_admin.csv, update mode, 3 lines (0 successful/ 3 failed), 0.129 s (0.0430 s/item)
  2015-04-29 06:53:10,404 - INFO - admin - browser.pages.DatacenterPage - deleted: users_admin.update.pending.csv
  2015-04-29 06:54:41,963 - INFO - admin - browser.pages.DatacenterUploadPage - uploaded: /kofa/trunk/var/datacenter/users2_admin.csv
  2015-04-29 06:54:51,748 - INFO - admin - processed: /kofa/trunk/var/datacenter/users2_admin.csv, create mode, 3 lines (3 successful/ 0 failed), 0.024 s (0.0079 s/item)

In the example above a user data file ``users.csv`` was uploaded and
processed in update mode. The import failed since the 3 users didn't
exist. The file was then deleted. User ``admin`` uploaded the file a
second time. The file name had to be changed because the uploader
does not allow to upload files with same name twice. The file was
finally successfully processed in create mode.

Also the export of data (export, download and discard) is recorded
in detail::

  2015-04-29 06:55:20,485 - INFO - admin - browser.pages.ExportCSVPage - exported: certificates, job_id=3036
  2015-04-29 06:55:25,697 - INFO - admin - browser.pages.ExportCSVView - downloaded: WAeUP.Kofa_certificates_3036.csv, job_id=3036
  2015-04-29 06:55:30,579 - INFO - admin - browser.pages.ExportCSVPage - discarded: job_id=3036


accesscodes.log
===============

The creation of access code batches, disabling and re-enabling of
single access codes and archiving and removal of entire batches is
logged as follows::

  2015-04-29 08:12:26,091 - INFO - admin - accesscodes.browser.AddBatchPage - created: ABC-1-2015_04_29_06_12_24-admin.csv (1000, 2300.000000)
  2015-04-29 08:13:07,024 - INFO - admin - accesscodes.browser.BatchContainerSearchPage - disabled: ABC-1-6003657048
  2015-04-29 08:13:11,502 - INFO - admin - accesscodes.browser.BatchContainerSearchPage - (re-)enabled: ABC-1-6003657048
  2015-04-29 08:14:13,668 - INFO - admin - accesscodes.browser.BatchContainerPage - archived: ABC-1 (ABC-1_archive-2015_04_29_06_14_13-admin.csv)
  2015-04-29 08:14:14,152 - INFO - admin - accesscodes.browser.BatchContainerPage - deleted: ABC-1

Not all access code workflow transitions are being logged. Each
access code has a history attribute which contains a detailed list
of all transitions. The history is shown on the
`BatchContainerSearchPage`.


applicants.log
==============

The creation, editing and removal of applicants containers as well
as editing applicant records is being logged. Also
the approval of payment tickets and all other payment ticket
transactions are being recorded in ``applicants.log``. Kofa also
logs all workflow transitions into both the applicant's history
attribute and the logfile. Okay, this is somehow redundant, but it
has proved useful to get a complete overview over all applicant
data transactions also in the logfile. In return, Kofa does not
aditionally log actions of browser pages if a workflow transition is
triggered at the same time. Let's see the example::

  2015-04-29 10:14:40,565 - INFO - admin - applicants.browser.ApplicantsContainerAddFormPage - added: app2015
  2015-04-29 10:14:45,398 - INFO - admin - applicants.browser.ApplicantsContainerManageFormPage - app2015 - saved: startdate + enddate + application_fee
  2015-04-29 10:15:08,779 - INFO - admin - app2015_262037 - Application initialized
  2015-04-29 10:15:28,703 - INFO - admin - app2015_262037 - Application started
  2015-04-29 10:15:28,704 - INFO - admin - applicants.browser.ApplicantManageFormPage - app2015_262037 - saved: reg_number + sex + course1 + date_of_birth
  2015-04-29 10:16:27,654 - INFO - admin - applicants.browser.ApplicationFeePaymentAddPage - app2015_262037 - added: p4302953958139
  2015-04-29 10:16:38,921 - INFO - admin - app2015_262037 - Payment approved
  2015-04-29 10:16:38,922 - INFO - admin - applicants.browser.OnlinePaymentApprovePage - app2015_262037 - approved: p4302953958139
  2015-04-29 10:16:58,026 - INFO - admin - app2015_262037 - Application submitted
  2015-04-29 10:17:01,040 - INFO - admin - applicants.browser.ApplicantManageFormPage - app2015_262037 - saved: course_admitted
  2015-04-29 10:17:10,978 - INFO - admin - app2015_262037 - Applicant admitted
  2015-04-29 10:17:10,979 - INFO - admin - applicants.browser.ApplicantManageFormPage - app2015_262037 - saved: locked
  2015-04-29 10:17:34,135 - INFO - admin - app2015_262037 - Student record created (K1000004)
  2015-04-29 10:45:15,298 - INFO - admin - app2015_262037 - Applicant record removed
  2015-04-29 10:45:15,299 - INFO - admin - applicants.browser.ApplicantsRootManageFormPage - removed: app2015

An applicants container was added first. The `startdate`, `enddate`
and the `application_fee` attributes were edited and a new
applicant record was added some seconds later. The
`ApplicantManageFormPage` was opened, `reg_number`, `sex`, `course1`
and `date_of_birth` was edited and the ``start`` transition was
selected. This was done in the same transaction. The time difference
between both log entries is only 0.001s. Furthermore, a payment
ticket was created and the payment approved. Then the applicant was
set to ``sumitted``, a `course_admitted` was selected and the
applicant subsequently admitted. The form was automatically locked
(see time difference). A student container was created and filled
with the data from the applicant record. Finally, the entire
applicants container including its content was removed in the same
transaction, see time diffence between the last two log entries.


students.log
============

The following example shows a typical Nigerian logfile excerpt for a
student from the very beginning (student record creation from
applicant data) till the first registration of courses at level
100. Such an excerpt can be produced simply by searching for
``B1234567`` on the ``students.log`` search page::

  2014-12-11 10:21:21,930 - INFO - admin - B1234567 - Record created
  2014-12-11 10:21:21,935 - INFO - admin - B1234567 - Admitted
  2014-12-19 05:53:02,760 - INFO - admin - Student Processor - physical_clearance_date_adm - B1234567 - updated: reg_number=12345678AB, physical_clearance_date=FRIDAY 9TH JANUARY 2015
  2014-12-22 14:16:50,494 - INFO - B1234567 - waeup.kofa.students.browser.OnlinePaymentAddFormPage - B1234567 - added: p4192542104720
  2014-12-22 14:51:36,959 - INFO - B1234567 - waeup.kofa.interswitch.browser.InterswitchPaymentRequestWebservicePageStudent - B1234567 - valid callback for clearance payment p4192542104720: 00:Approved Successful:4500000:5964:p4192542104720:FBN|WEB|UNIBEN|22-12-2014|02345:000382768769
  2014-12-22 14:51:36,985 - INFO - B1234567 - waeup.kofa.interswitch.browser.InterswitchPaymentRequestWebservicePageStudent - B1234567 - successful clearance payment: p4192542104720
  2014-12-22 14:53:09,148 - INFO - B1234567 - B1234567 - Clearance started
  2014-12-22 14:53:39,983 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: birth_certificate.jpg (birth.JPG)
  2014-12-22 14:53:54,482 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: acc_let.jpg (acceptance.JPG)
  2014-12-22 14:54:08,943 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: lga_ident.jpg (LGA.JPG)
  2014-12-22 14:54:23,541 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: fst_sit_scan.jpg (waec.JPG)
  2014-12-22 14:54:56,663 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: ref_let.jpg (guarantor.JPG)
  2014-12-22 14:56:16,039 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: stat_dec.jpg (good.JPG)
  2014-12-22 14:56:37,895 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: jamb_letter.jpg (JAMB.JPG)
  2014-12-22 14:56:54,696 - INFO - B1234567 - waeup.kofa.students.browser.StudentClearanceEditFormPage - B1234567 - uploaded: secr_cults.jpg (cult.JPG)
  2014-12-22 15:02:42,550 - INFO - B1234567 - B1234567 - Clearance requested
  2015-01-17 11:58:12,643 - INFO - clearanceofficer - B1234567 - Cleared
  2015-03-10 10:58:46,217 - INFO - B1234567 - waeup.kofa.students.browser.OnlinePaymentAddFormPage - B1234567 - added: p4259815262042
  2015-03-13 11:38:21,658 - INFO - B1234567 - waeup.kofa.interswitch.browser.InterswitchPaymentRequestWebservicePageStudent - B1234567 - valid callback for schoolfee payment p4259815262042: 00:Approved Successful:4950000:2022:p4259815262042:GTB|WEB|UNIBEN|13-03-2015|001234:0001234566
  2015-03-13 11:38:22,016 - INFO - B1234567 - waeup.kofa.interswitch.browser.InterswitchPaymentRequestWebservicePageStudent - B1234567 - successful schoolfee payment: p4259815262042
  2015-03-16 13:01:09,989 - INFO - B1234567 - B1234567 - First school fee payment made
  2015-03-16 13:03:50,977 - INFO - B1234567 - waeup.kofa.students.browser.StudyLevelEditFormPage - B1234567 - added: PHY124|100|2014
  2015-03-16 13:05:04,504 - INFO - B1234567 - B1234567 - Courses registered
  2015-03-28 07:18:21,846 - INFO - admin - Student Processor - Matno_for_upload_25_03_2015-1_admin - B1234567 - updated: student_id=B1234567, matric_number=LSC123456

The log entry format of transactions due to imports is slightly
different::

  2015-04-30 08:40:51,088 - INFO - admin - Student Processor - studentcreate_admin - B3333333 - updated: state=returning, reg_number=BIA12326, firstname=FRIDAY, middlename=None, lastname=Olonko, sex=m, nationality=NG, matric_number=SSC4444444
  2015-04-30 08:41:27,179 - INFO - admin - StudentStudyCourse Processor (update only) - studycourseaupdate_admin - B3333333 - updated: entry_mode=ug_pt, certificate=BIA, current_session=2002, entry_session=2002, current_level=100, current_verdict=Z

Two files had been uploaded by admin (``studentcreate.csv`` and
``studycourseaupdate.csv``, see entries in ``datacenter.log``) and
subsequently imported with the Student Processor and Student Study
Course Processor respectively.

As already stated above, not all actions committed by students are
beeing logged. The student did not only upload a lot of files but
also edited dozens of fields on the clearance form page and probably
pressed the 'Save' button very often to backup the data entered so
far. These backup transactions were skipped. All other transactions
are being recorded. Some examples of further logfile records are
listed below.

Setting a temporary password::

  2012-10-20 20:59:28,392 - INFO - admin - students.browser.LoginAsStudentStep1 - W4444444 - temp_password generated: Paa3ZVrV

Deactivating and re-activating students::

  2014-11-15 14:28:49,859 - INFO - admin - students.browser.StudentDeactivatePage - W1111111 - account deactivated
  2014-11-17 10:19:05,735 - INFO - admin - students.browser.StudentActivatePage - W1111111 - account activated

Rejection of clearance requests (an email is sent and the body of
the email is stored as comment in the logfile)::

  2014-10-27 12:39:34,499 - INFO - clearanceofficer - students.browser.StudentRejectClearancePage - W2222222 - comment: no credit in english

Approval of payment tickets (which does not automatically goes along
with a student workflow transition)::

  2012-11-02 12:01:03,022 - INFO - admin - students.browser.OnlinePaymentApprovePage - W1000000 - schoolfee payment approved: p3517158705027

Bed allocation and re-allocation::

  2012-11-07 12:56:26,745 - INFO - W1000000 - waeup.kwarapoly.students.browser.BedTicketAddPage - W1000000 - booked: white-house_W_106_B
  2013-10-29 11:49:55,048 - INFO - hostelofficer - students.browser.BedTicketRelocationPage - W1000000 - relocated: block-a-upper-hostel_A_118_E

Password changes by students::

  2013-02-19 08:54:50,177 - INFO - K9999999 - students.browser.StudentChangePasswordPage - K9999999 - saved: password


payments.log
============

This file is hidden and can only be accessed directly in the
filesystem. The payment logger is not needed in the Kofa base
package. Only `OnlinePaymentApprovePage.update()` writes into the
``payments.log`` file. The logger is primarily intended for storing
information about successfull financial transactions via external
payment gateways (e.g. PayPal, Interswitch, eTranzact). No external
payment gateway module is configured in the base package.


hostels.log
===========

Whereas the reservation/allocation of bed spaces is being logged in
``students.log`` (see above), the management of hostels and beds is
recorded in ``hostels.log``::

  2015-04-30 11:44:29,145 - INFO - admin - hostels.browser.HostelAddFormPage - hostels - added: Hall 1
  2015-04-30 11:45:29,283 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - saved: rooms_per_floor + blocks_for_female
  2015-04-30 11:46:29,330 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - 0 empty beds removed, 10 beds added, 0 occupied beds modified ()
  2015-04-30 11:47:29,433 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - switched: hall-1_A_101_A (reserved), hall-1_A_101_B (reserved), hall-1_A_101_C (reserved), hall-1_A_101_D (reserved)
  2015-04-30 11:47:59,283 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - saved: beds_for_fresh + beds_for_all
  2015-04-30 11:48:29,498 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - 9 empty beds removed, 9 beds added, 1 occupied beds modified (hall-1_A_101_E, )
  2015-04-30 11:49:29,560 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - switched: hall-1_A_101_A (unreserved), hall-1_A_101_B (unreserved), hall-1_A_101_C (unreserved), hall-1_A_101_D (unreserved)
  2015-04-30 11:50:29,689 - INFO - admin - hostels.browser.HostelManageFormPage - hall-1 - released: hall-1_A_101_D (K1000000)
  2015-04-30 11:51:29,898 - INFO - admin - hostels.browser.BedManageFormPage - hall-1_A_101_A - saved: owner
  2015-04-30 11:54:30,163 - INFO - admin - hostels.browser.HostelsContainerManagePage - hostels - deleted: hall-1

In this example, the hostel ``Hall 1`` was added and configured,
beds were updated, beds were reserved (switched), the hostel
configuration was changed, beds were updated again, beds were
unreserved, a single bed was released, a new student was allocated
and, finally, the entire hostel was removed.

Also all transactions of the Hostel Processor are being logged::

  2015-04-30 11:51:12,840 - INFO - system - Hostel Processor - sample_hostel_data - hall-b - updated: beds_for_pre=['F'], floors_per_block=1, beds_for_final=['A', 'B'], rooms_per_floor=44, blocks_for_male=['C', 'D'], hostel_id=hall-b, sort_id=100, beds_for_returning=['C'], hostel_name=Hall B, beds_for_fresh=['D', 'E'], blocks_for_female=[], beds_for_all=[], beds_reserved=[]



.. _regular expressions: http://en.wikipedia.org/wiki/Regular_expression