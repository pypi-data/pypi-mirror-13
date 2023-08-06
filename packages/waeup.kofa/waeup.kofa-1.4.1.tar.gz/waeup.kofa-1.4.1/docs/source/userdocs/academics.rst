.. _academic_section:

Academic Section 
****************

Academic bodies of universities are hierarchically structured. A
university contains faculties which again host departments. The
latter offer courses (course units) and study programmes (courses of
study). A course is a series of classes or lessons on a particular
subject. This can be a lecture, tutorial, seminar, practical work
offered by a lecturer of the department over a period of an academic
term. A course can also be only an exam at the end of an academic
term. A study programme is defined by a set of course units to be
taken at various programme levels and by an academic degree
certificate, which is issued at the end of the programme.
Information about universities, their study programmes, lecturers
and courses can be found in the university prospectus.

Kofa's academic section takes on the task of the university
prospectus. It is build to disseminate information about faculties,
departments, courses, study programmes and the sets of courses to be
taken. The academic section reflects exactly the universities'
hierarchical structure as described above. Technically speaking, the
academic section is a container of type `FacultiesContainer` with id
``academics`` which contains faculty subcontainers. They again
contain department subobjects and so on. This leads to a
:ref:`treelike storage of objects <object_database>`::

  Academic Section (FacultiesContainer)
  |
  +---> Faculty
        |
        +---> Department
              |
              +---> CoursesContainer
              |     |
              |     +---------------------> Course
              |                             ^
              +---> CertificatesContainer   |
                    |                       |
                    +-----> Certificate     |
                            |               |
                            +-----> CertificateCourse


Faculty
=======

Faculties are container objects of type `Faculty`. They have a
`code`, a `title` and a `title_prefix` attribute. Furthermore,
faculties and departments have a `longtitle` property which
:py:func:`composes <waeup.kofa.university.faculty.longtitle>` and
returns the full title as it appears in tables, in breadcrumbs and
in many other places:

  `longtitle` = `title_prefix` + `title` (`code`)

The following :ref:`local roles <local_roles>` can be assigned at
faculty tree level:

  .. autoattribute:: waeup.kofa.university.faculty.Faculty.local_roles
     :noindex:


Department
==========

Additionally, each department object has the attributes
`certificates` and `courses`. These attributes again are containers
which hold certificate and course objects respectively.
A :py:meth:`traverse
<waeup.kofa.university.department.Department.traverse>` method leads
the user to believe that `certificates` and `courses` are the ids of
objects stored inside a department container. De facto they are not.
However, it doesn't matter if we store a subobject 'in' or 'at' a
parent object. The result is exactly the same: :ref:`a hierarchical,
treelike storage of objects <object_database>` (see also diagram above).

The following :ref:`local roles <local_roles>` can be assigned at
department tree level:

  .. autoattribute:: waeup.kofa.university.department.Department.local_roles
     :noindex:

Course
======

The `Course` class inherits from `grok.Model` which means it is
designed as a pure model and not a container. Courses are tips of
the database tree branches. Course objects contain information as
they are offered by the department. In the base package these are:
`code`, `title`, `credits`, `passmark`, `semester` and the boolean
attribute `former_course`. Like all objects in the academic section,
they also have a `longtitle` property. A former course is an
archived course which had been offered in the past and is no longer
part of any curriculum.

.. note::

  Only the manager of the department, which offers the course,
  decides how many credits can be earned, which pass mark must be
  achieved and in which semester the course can be taken. The
  manager cannot decide whether a course is mandatory or not, or
  at which study level the course has to be taken when studying a
  certain programme. This information is stored in
  `CertificateCourse` objects, see below. Therefore it does not
  make sense to speak e.g. of a 300 level course. Also course
  codes like ``AEE311``, which tell the student that the course
  is primarily intended for 300 level students, is somehow
  misleading. There might be other study programmes which
  recommend to take this course earlier or later.


The following :ref:`local roles <local_roles>` can be assigned at
course tree level:

  .. autoattribute:: waeup.kofa.university.course.Course.local_roles
   :noindex:

.. _certificate:

Certificate
===========

.. seealso::

   :ref:`Certificates and Certificate Courses Doctests <certcourse_txt>`

In Kofa, the terms 'certificate' and 'study programme' are used
synonymously. A certificate object holds information about the study
programme. Important data for further processing in Kofa are: the
various school fees to be paid at certain levels, programme start
and end level, the study mode and, last but not least, the
application category to which the programme belongs.

Certificates are containers which contain `CertificateCourse`
objects. That means a certificate defines the curriculum, i.e. the
list of course units which have to or can be taken within the
programme.

The following :ref:`local roles <local_roles>` can be assigned at
certificate tree level:

  .. autoattribute:: waeup.kofa.university.certificate.Certificate.local_roles
   :noindex:

.. warning::

  Do not remove certificates without backing up the student data
  of this department. If a certificate or even one of its parent
  containers is removed, students studying this programme are
  'homeless' and need to be re-allocated to another study
  programme.


Certificate Course
==================

`CertificateCourse` objects point to `Course` objects which means
they have a `course` attribute which is one of the course objects
stored in the portal. If the course is removed, an event handler
takes care of deleting also all referring certificate courses. The
same happens if a course is beeing marked as former course (see
above). A former course cannot be part of a curriculum.

Certificate courses have two more attributes: `level` (integer) and
`mandatory` (boolean). Simply put, certificate courses carry the
information at which level a certain course can or has to be taken
to meet the current curriculum.

No local role can be assigned at certificate course tree level.

Browser Pages
=============

In the user handbook we do not describe how to browse the academic
section. The menu navigation is self-explanatory and it's
quite easy to follow the menu prompts. However, in the beginning of
the development of Kofa, we used extensive doc tests which describe
the navigation very well. Thus navigating through the academic
section and other parts of Kofa with a test browser is perfectly
described in :ref:`pages.txt <pages_txt>`.
