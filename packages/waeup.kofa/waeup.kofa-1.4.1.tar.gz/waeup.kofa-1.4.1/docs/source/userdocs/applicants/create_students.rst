.. _creating_students:

Single Record Creation vs. Mass Creation
========================================

As brought up in the :ref:`application_workflow` chapter, the final
step of the application process is the creation of the student
record on the basis of the application data. Only applicants in
state ``admitted`` can be turned into students. This is possible at
various application section levels:

1. Officers can create student records from single applicant
   records. A link button appears on the display page of each admitted
   applicant which directly triggers the creation process:

  |create_student_button|

2. The `ApplicantsContainerManageFormPage` provides a form button
   which allows to create student records from above selected
   applicants:

  |create_selected_students_button|

  Only admitted applicants will be processed. Other selected
  applicants will be skipped without further notice.

3. Last but not least, the portal manager with user id ``admin``
   does see a link button:

  |create_students_button|

  on the `ApplicantsContainerPage` and on the `ApplicantsRootPage`
  which creates student records from applicants inside a single
  applicants container or even portal-wide respectively.

  The reader may wonder: Why only user ``admin``?

  Batch creation of thousands or even tenthousands of student records
  is very computation intensive and takes quite a long time, even with
  powerful computers. Experience has shown that the portal must be
  disconnected from the Internet in order to avoid database write
  conflict errors, which cannot be resolved if also students access
  the portal. Usually conflict errrors are not serious. Unresolved
  conflicts just lead to an error message and the database remains
  unchanged. Unfortunataly, student creation does not only alter the
  object database. As we will see below, also folders and files in the
  filesystem are added. These filesystem changes are not being
  reverted after unresolved conflicts, a fact which can cause serious
  problems.

  So the answer to the question is trivial: We expect that the admin
  user knows what s/he is doing and is careful enough to start the
  creation process in maintenance mode, which means when the portal is
  disconnected from a public network.


The `createStudent` Method
==========================

The `Applicant.createStudent` method is called for each admitted
applicant. The method performs a series of checks before it creates
a new student record:

1. Is the applicant really in the correct state?

2. Has the registration number not been assigned to another student?

3. Is a certificate (`course_admitted`) provided?

4. Can all required student attributes be copied and set? The
   following attributes are copied:

   .. autoattribute:: waeup.kofa.applicants.applicant.Applicant.applicant_student_mapping
      :noindex:

5. Can the application slip be created? Defective images may
   cause the adapter method to raise an exception (``IOError``).

If all these checks are passed, a new student record is created, a
password is set, the transitions ``create`` and ``admit`` are fired
and all student study course attributes are set. All this is done
in one database transaction.

Furthermore, `createStudent` also produces an application slip pdf
file, creates a new folder for the student in the filesystem and
copies the pdf file together with the passport jpeg image file into
the newly created folder. The copied application slip ensures, that
the original application data do not get lost, when the application
section is being purged.

As mentioned above, folder creation and file copying are not part of
the transaction and are not being rolled back if the database
transactions fails, for example due to write conflict errors.
Therefore, batch student creation should only be performed if the
portal is offline.


.. |create_student_button| image:: ../images/create_student_button.png
   :scale: 50 %

.. |create_students_button| image:: ../images/create_students_button.png
   :scale: 50 %

.. |create_selected_students_button| image:: ../images/create_selected_students_button.png
   :scale: 50 %
