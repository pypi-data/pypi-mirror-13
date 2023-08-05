.. _export:

Data Export
***********

Regular data exporters (1) collect objects from specific containers,
(2) iterate over the collected objects, (3) extract and mangle
information from each object, (4) write the information of each object
into a row of a CSV file and (5) finally provide the file for
download. The CSV file is neither stored in the database nor archived
in the filesystem. (3) and (4) means a flattening of the hierarchical
data structure, i.e. a mapping of objects to flat relational data to
be stored in a CSV table. The extracted information must not
necessarily be based only on static attributes of the collected
object. The data, finally stored in the CSV file, can also be derived
from parent or child objects, or dynamically computed by the object's
methods and property attributes. These methods and properties can
retrieve information from everywhere in the portal's database. In the
following we list all exporter classes including two attributes and a
method description. The `fields` attribute contain the column titles
of the export file. These are not necessarily only attributes of the
exported objects.

.. note::

  The list of exported columns usually underlies heavy customizations.
  In the Kofa base package only very few columns are being exported. In
  some Kofa custom packages tons of data are being gathered from
  applicants and students and the number of columns increases
  accordingly.

The `title` attribute unveils the name of the exporter under which
this exporter will be displayed in the user interface. The
`mangle_value()` method shows how some of fields are being dynamically
computed.

Regular Exporters
=================

User Exporter
-------------

.. autoclass:: waeup.kofa.userscontainer.UserExporter()

  .. autoattribute:: waeup.kofa.userscontainer.UserExporter.fields
  .. autoattribute:: waeup.kofa.userscontainer.UserExporter.title
  .. automethod:: waeup.kofa.userscontainer.UserExporter.mangle_value()

Faculty Exporter
----------------

.. autoclass:: waeup.kofa.university.export.FacultyExporter()

  .. autoattribute:: waeup.kofa.university.export.FacultyExporter.fields
  .. autoattribute:: waeup.kofa.university.export.FacultyExporter.title
  .. automethod:: waeup.kofa.university.export.FacultyExporter.mangle_value()

Department Exporter
-------------------

.. autoclass:: waeup.kofa.university.export.DepartmentExporter()

  .. autoattribute:: waeup.kofa.university.export.DepartmentExporter.fields
  .. autoattribute:: waeup.kofa.university.export.DepartmentExporter.title
  .. automethod:: waeup.kofa.university.export.DepartmentExporter.mangle_value()

Course Exporter
---------------

.. autoclass:: waeup.kofa.university.export.CourseExporter()

  .. autoattribute:: waeup.kofa.university.export.CourseExporter.fields
  .. autoattribute:: waeup.kofa.university.export.CourseExporter.title
  .. automethod:: waeup.kofa.university.export.CourseExporter.mangle_value()

Certificate Exporter
--------------------

.. autoclass:: waeup.kofa.university.export.CertificateExporter()

  .. autoattribute:: waeup.kofa.university.export.CertificateExporter.fields
  .. autoattribute:: waeup.kofa.university.export.CertificateExporter.title
  .. automethod:: waeup.kofa.university.export.CertificateExporter.mangle_value()

Certificate Course Exporter
---------------------------

.. autoclass:: waeup.kofa.university.export.CertificateCourseExporter()

  .. autoattribute:: waeup.kofa.university.export.CertificateCourseExporter.fields
  .. autoattribute:: waeup.kofa.university.export.CertificateCourseExporter.title
  .. automethod:: waeup.kofa.university.export.CertificateCourseExporter.mangle_value()

Access Code Batch Exporter
--------------------------

.. autoclass:: waeup.kofa.accesscodes.export.AccessCodeBatchExporter()

  .. autoattribute:: waeup.kofa.accesscodes.export.AccessCodeBatchExporter.fields
  .. autoattribute:: waeup.kofa.accesscodes.export.AccessCodeBatchExporter.title

Access Code Exporter
--------------------

.. autoclass:: waeup.kofa.accesscodes.export.AccessCodeExporter()

  .. autoattribute:: waeup.kofa.accesscodes.export.AccessCodeExporter.fields
  .. autoattribute:: waeup.kofa.accesscodes.export.AccessCodeExporter.title
  .. automethod:: waeup.kofa.accesscodes.export.AccessCodeExporter.mangle_value()

Hostel Exporter
---------------

.. autoclass:: waeup.kofa.hostels.export.HostelExporter()

  .. autoattribute:: waeup.kofa.hostels.export.HostelExporter.fields
  .. autoattribute:: waeup.kofa.hostels.export.HostelExporter.title

Bed Exporter
------------

.. autoclass:: waeup.kofa.hostels.export.BedExporter()

  .. autoattribute:: waeup.kofa.hostels.export.BedExporter.fields
  .. autoattribute:: waeup.kofa.hostels.export.BedExporter.title

Document Exporter
-----------------

.. autoclass:: waeup.kofa.documents.export.DocumentExporterBase()

  .. automethod:: waeup.kofa.documents.export.DocumentExporterBase.mangle_value()

Application Data Exporters
==========================

Applicants Container Exporter
-----------------------------

.. autoclass:: waeup.kofa.applicants.export.ApplicantsContainerExporter()

  .. autoattribute:: waeup.kofa.applicants.export.ApplicantsContainerExporter.fields
  .. autoattribute:: waeup.kofa.applicants.export.ApplicantsContainerExporter.title

Applicant Exporter
------------------

.. autoclass:: waeup.kofa.applicants.export.ApplicantExporter()

  .. autoattribute:: waeup.kofa.applicants.export.ApplicantExporter.fields
  .. autoattribute:: waeup.kofa.applicants.export.ApplicantExporter.title
  .. automethod:: waeup.kofa.applicants.export.ApplicantExporter.mangle_value()

Student Data Exporters
======================

When starting a Student Data Exporter in the Data Center all student
records will be taken into consideration, no matter what or where a
student is studying. The exporter can also be started 'locally' at
various levels in the academic section. Starting one of the exporters
e.g. at faculty or department level means that only the data of
students are exported who study in this faculty or department
respectively. The exporter can also be started at certificate level.
Then only the data of students, who are studying the named study
course, will be taken into account. At course level the data of those
students are being exported who have attended or taken this specific
course.

Student Data Exporter can be further configured through a
configuration page. Search parameters like the student's current level,
current session and current study mode can be set to filter sets of
students in order to decrease the size of the export file. The set of
filter parameters varies and depends on the 'locatation' from where
the exporter is called. A completely different set of filter
parameters is provided for courses. In this case the session and level
can be selected when the course was taken by the student.

Student Exporter
----------------

.. autoclass:: waeup.kofa.students.export.StudentExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentExporter.title
  .. automethod:: waeup.kofa.students.export.StudentExporter.mangle_value()

Student Study Course Exporter
-----------------------------

.. autoclass:: waeup.kofa.students.export.StudentStudyCourseExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentStudyCourseExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentStudyCourseExporter.title
  .. automethod:: waeup.kofa.students.export.StudentStudyCourseExporter.mangle_value()

Student Study Level Exporter
----------------------------

.. autoclass:: waeup.kofa.students.export.StudentStudyLevelExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentStudyLevelExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentStudyLevelExporter.title
  .. automethod:: waeup.kofa.students.export.StudentStudyLevelExporter.mangle_value()

Course Ticket Exporter
----------------------

.. autoclass:: waeup.kofa.students.export.CourseTicketExporter()

  .. autoattribute:: waeup.kofa.students.export.CourseTicketExporter.fields
  .. autoattribute:: waeup.kofa.students.export.CourseTicketExporter.title
  .. automethod:: waeup.kofa.students.export.CourseTicketExporter.mangle_value()

Student Payment Exporter
------------------------

.. autoclass:: waeup.kofa.students.export.StudentPaymentExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentPaymentExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentPaymentExporter.title
  .. automethod:: waeup.kofa.students.export.StudentPaymentExporter.mangle_value()

Student Unpaid Payment Exporter
-------------------------------

.. autoclass:: waeup.kofa.students.export.StudentUnpaidPaymentExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentUnpaidPaymentExporter.title

Bed Ticket Exporter
-------------------

.. autoclass:: waeup.kofa.students.export.BedTicketExporter()

  .. autoattribute:: waeup.kofa.students.export.BedTicketExporter.fields
  .. autoattribute:: waeup.kofa.students.export.BedTicketExporter.title
  .. automethod:: waeup.kofa.students.export.BedTicketExporter.mangle_value()

.. note::

  The above exporters refer to a specific content type (object class).
  They export all attributes of these objects and a few additional
  parameters derived from the parent objects. These exporters can be
  used for reimport, or more precisely for backing up and restoring
  data. The following 'special' exporters are made on request of some
  universities to collect and compose student data for analysis and
  postprocessing by the university.

DataForBursary Exporter
-----------------------

.. autoclass:: waeup.kofa.students.export.DataForBursaryExporter()

  .. autoattribute:: waeup.kofa.students.export.DataForBursaryExporter.fields
  .. autoattribute:: waeup.kofa.students.export.DataForBursaryExporter.title
  .. automethod:: waeup.kofa.students.export.DataForBursaryExporter.mangle_value()

Student Payments Overview Exporter
----------------------------------

.. autoclass:: waeup.kofa.students.export.StudentPaymentsOverviewExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentPaymentsOverviewExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentPaymentsOverviewExporter.title
  .. autoattribute:: waeup.kofa.students.export.StudentPaymentsOverviewExporter.curr_year
  .. automethod:: waeup.kofa.students.export.StudentPaymentsOverviewExporter.mangle_value()

Student Study Levels Overview Exporter
--------------------------------------

.. autoclass:: waeup.kofa.students.export.StudentStudyLevelsOverviewExporter()

  .. autoattribute:: waeup.kofa.students.export.StudentStudyLevelsOverviewExporter.fields
  .. autoattribute:: waeup.kofa.students.export.StudentStudyLevelsOverviewExporter.title
  .. automethod:: waeup.kofa.students.export.StudentStudyLevelsOverviewExporter.mangle_value()

Combo Card Data Exporter
------------------------

.. autoclass:: waeup.kofa.students.export.ComboCardDataExporter()

  .. autoattribute:: waeup.kofa.students.export.ComboCardDataExporter.fields
  .. autoattribute:: waeup.kofa.students.export.ComboCardDataExporter.title
  .. automethod:: waeup.kofa.students.export.ComboCardDataExporter.mangle_value()

File Export
===========

You want to export files (passport images, pdf slips), for instance
of all students in a department or applicants in an applicants
container? There is no facility in Kofa which does this job for you,
but you can batch-download files by means of your operating system
on your local machine. This works perfectly with the the `wget`
command on Linux or MacOS computers. Windows does not provide such a
command.

If ``numbers.txt`` contains the application numbers of applicants in
the applicants container ``xyz``, the following bash script will
download all passport images directly onto you computer::

  wget --save-cookies cookies.txt --keep-session-cookies --post-data 'form.login=my-username&form.password=my-password' https://my-kofa-site/login

  for i in $(cat numbers.txt)
  do
   wget --load-cookies cookies.txt --output-document=$i.jpg https://my-kofa-site/applicants/xyz/$i/passport.jpg
  done

If ``numbers.txt`` contains the ids of students in a department, the
following bash script will download all passport images directly
onto you computer. The script is a slightly extended, more user
friendly version of the script above::

  if [ $# -lt 3 ]
  then
     echo "usage: $0 username password filename"
     exit 1
  fi

  wget --save-cookies cookies.txt --keep-session-cookies --post-data "form.login=$1&form.password=$2" https://my-kofa-site/login

  while read variable
  do
     echo https://my-kofa-site/students/$variable/passport.jpg
     wget --load-cookies cookies.txt --output-document $variable.jpg https://my-kofa-site/students/$variable/passport.jpg
  done < $3


