.. _student_section:

Students Section
****************

'Student' is a multi-purpose term in Kofa which may lead to some
misconceptions. First of all, 'Student' is a Python/Grok container
class and student objects are the instances of this class. Sometimes
we are sluggish when talking about 'creating students' and actually
mean: 'creating student container objects and storing the objects
(persistently) in the ``students`` container'. The latter is the
parent container for all students in the portal.

The :ref:`treelike storage of objects <object_database>` in the
students section can be figured as follows::


  Students Section (StudentsContainer)
  |
  +---> Student
        |
        +---> StudentStudyCourse
        |     |
        |     +-----> StudentStudyLevel
        |             |
        |             +-----> CourseTicket
        |
        +---> StudentPaymentsContainer
        |     |
        |     +-----> StudentOnlinePayment
        |
        +---> StudentAccommodation
              |
              +-----> BedTicket


.. note::

  Throughout Kofa we distinguish singular and plural expressions. A
  students container contains students (or more precisely student
  containers), a payments container contains payments, a courses
  container contains courses, a certificates container contains
  certificates.

Furthermore, a student is also a user of the portal and the student
object is a user account surrogate, see :ref:`Applicants and
Students <applicants_and_students>`. In the following we always
refer to the student container when talking about a student.

Interfaces
==========

.. toctree::
   :maxdepth: 3

   students/interfaces

Workflow & History
==================

.. toctree::
   :maxdepth: 3

   students/workflow

Browser Pages
=============

.. toctree::
   :maxdepth: 3

   students/browser
