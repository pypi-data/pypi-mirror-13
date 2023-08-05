.. _import_processors:

Batch Processors
****************

.. seealso::

   :ref:`Batch Processing Doctests (The Caveman Story) <batchprocessing_txt>`

   :ref:`Batch Processing via Browser Doctests <batchprocessing_browser_txt>`

All batch processors inherit from the
:py:class:`waeup.kofa.utils.batching.BatchProcessor` base class. The
`doImport` method, described above, always remains unchanged. All
processors have a property `available_fields` which defines the set
of importable data. They correspond with the column titles of the
import file. Available fields are usually composed of location fields,
interface fields and additional fields. Overlaps are possible.
Location fields define the minumum set of fields which are necessary
to locate an existing object in order to update or remove it.
Interface fields (schema fields) are the fields defined in the
interface of the data entity. Additional fields are additionally
needed for data processing. We further distinguish between required
and optional fields or between schema and non-schema fields.

In the following we list all available processors of the Kofa base
package including some important methods which describe them best. We
do not list available fields of each processor here. Available fields
are shown in the browser user interface on the upload page of the
portal. The processors of the Kofa base package can be viewed
`here <http://kofa-demo.waeup.org/processors>`_.

Regular Processors
==================

User Processor
--------------

.. autoclass:: waeup.kofa.authentication.UserProcessor()
  :noindex:

Faculty Processor
-----------------

.. autoclass:: waeup.kofa.university.batching.FacultyProcessor()
  :noindex:

Department Processor
--------------------

.. autoclass:: waeup.kofa.university.batching.DepartmentProcessor()
  :noindex:

Certificate Processor
---------------------

.. autoclass:: waeup.kofa.university.batching.CertificateProcessor()
  :noindex:

Course Processor
----------------

.. autoclass:: waeup.kofa.university.batching.CourseProcessor()
  :noindex:

Certificate Course Processor
----------------------------

.. autoclass:: waeup.kofa.university.batching.CertificateCourseProcessor()
  :noindex:

Access Code Batch Processor
---------------------------

.. autoclass:: waeup.kofa.accesscodes.batching.AccessCodeBatchProcessor()
  :noindex:

Access Code Processor
---------------------

.. autoclass:: waeup.kofa.accesscodes.batching.AccessCodeProcessor()
  :noindex:

Hostel Processor
----------------

.. autoclass:: waeup.kofa.hostels.batching.HostelProcessor()
  :noindex:

Bed Processor
--------------

.. autoclass:: waeup.kofa.hostels.batching.BedProcessor()
  :noindex:

Document Processor
------------------

.. autoclass:: waeup.kofa.documents.batching.DocumentProcessorBase()
  :noindex:

Application Data Processors
===========================

Applicants Container Processor
------------------------------

.. autoclass:: waeup.kofa.applicants.batching.ApplicantsContainerProcessor()
  :noindex:

Applicant Processor
-------------------

.. autoclass:: waeup.kofa.applicants.batching.ApplicantProcessor()
  :noindex:

Student Data Processors
=======================

Student Processor
-----------------

.. autoclass:: waeup.kofa.students.batching.StudentProcessor()
  :noindex:

Student Study Course Processor
------------------------------

.. autoclass:: waeup.kofa.students.batching.StudentStudyCourseProcessor()
  :noindex:

Student Study Level Processor
-----------------------------

.. autoclass:: waeup.kofa.students.batching.StudentStudyLevelProcessor()
  :noindex:

.. note::

  The student data processors described so far are mainly intended for
  restoring data. If the portal is operated correctly and without
  interruption and students follow the workflow from their first to the
  final study year, there is no need to use the above batch processors
  to maintain the data. The processors are not part of the student
  registration management. The following processors can or sometimes
  even must be integrated into the regular management of student data.
  Scores have to be imported, new payment tickets have to created, the
  verdicts have to be set or workflow transitions have to be triggered.

.. _course_ticket_processor:

Course Ticket Processor
-----------------------

.. autoclass:: waeup.kofa.students.batching.CourseTicketProcessor()
  :noindex:

Student Online Payment Processor
--------------------------------

.. autoclass:: waeup.kofa.students.batching.StudentOnlinePaymentProcessor()
  :noindex:

Verdict Processor
-----------------

.. autoclass:: waeup.kofa.students.batching.StudentVerdictProcessor()
  :noindex:
