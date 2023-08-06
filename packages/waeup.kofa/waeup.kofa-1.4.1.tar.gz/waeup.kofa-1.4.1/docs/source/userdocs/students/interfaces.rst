.. _students_interfaces:

Student Interfaces
==================

The `Student` class is a container class which means, there are not
only attributes describing the student entity but also content. Each
student container contains three subcontainers:
``studycourse`` (instance of `StudentStudyCourse`), ``payments``
(instance of `StudentPaymentsContainer`) and ``accommodation``
(instance of `StudentAccommodation`). The purposes of them are
described further below. The student container with all its
subcontainers and subobjects is called **student record**.

Let's talk about the attributes and methods belonging to the
`Student` class, the so-called 'external behaviour' of student
objects specified in Zope 'interfaces'. The data stored with each
student object are subdivided into three parts: base data, personal
data and clearance data. Each part has its own interface.

.. _kofa_interfaces:

.. note::

  **Interfaces** are one of the pillars of Zope's Component
  Architecture (ZCA, see also :ref:`prerequisites`). They document the
  'external behaviour' of objects. In Kofa interfaces are used to
  specify the attributes, methods and schema fields of objects. The
  first two are well-known Python concepts. A Zope schema field is a
  bit more complicated. It's a detailed description of a field to be
  submitted via forms to the server, or which is processed by a batch
  processor. In both cases the input data are being validated against
  the schema field requirements. In Kofa, schema fields (see also note
  below) in interfaces are also used to automtically add
  `FieldProperty` attributes of the same name to most content classes.
  This is done by a function
  :py:func:`attrs_to_fields<waeup.kofa.utils.helpers.attrs_to_fields>`
  which is called once during startup of Kofa. These class attributes
  ensure that corresponding attributes of instances of this class -
  when being added or changed - always meet the requirements of the
  schema field. Another big advantage of such class attributes is,
  that attributes with a `FieldProperty` do not need to be set in
  `__init__` methods.

The `Student` class implements several interfaces which we will
quote to unveil the student's 'external behaviour'.

`IStudentBase`
--------------

`waeup.kofa.students.interfaces.IStudentBase` defines a fundamental
set of attributes, schema fields and methods which are being used
throughout the portal. This set is immutable. No class statement
must be removed or added in customized versions of Kofa.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentBase

The **first part** of the interface lists attributes. Except for the
last two attributes (`password` and `temp_password`) they are all
read-only property attributes, i.e. attributes with a getter method
only. These properties are computed dynamically and can't be set.
Most of them return data derived from the ``studycourse`` subobject.

The **second part** of the interface specifies the schema fields.

.. _kofa_schemas:

.. note::

  **Schema fields** are instances of schema field classes with `title`,
  `description`, `default`, `required`, `readonly` attributes. Class
  names and class attributes are self-explanatory and described in the
  `Zope Schema`_ documentation.

  A very powerful Zope Schema field is `Choice`. Choice fields are
  constrained to values drawn from a specified set, which can be
  static or dynamic. This set can be a simple list of choices (=
  `values`), a `vocabulary` or a `source` which produce dynamic
  choices.

  **Vocabularies and sources** are very similar. The latter is a newer
  concept of producing choices and considered to replace vocabularies.
  In Kofa we use both. Common to both is, that a set of values is
  accompanied by a user-friendly title, which is displayed on pages
  (e.g. in select boxes) instead of a less informative value token or
  even a cryptic representation of a persistent value object. In most
  cases we have a token-title pair which perfectly describes the
  values of a source or a vocabulary. The tokens are being sent in
  forms or imported by batch processors.

  See `token-title pairs <http://kofa-demo.waeup.org/sources>`_ of
  most (non-database-dependent) sources and vocabularies in the Kofa
  base package.

The **third part** of the interface lists the methods which can be
applied to student objects.

`IUGStudentClearance`
---------------------

Much like all the following student interfaces,
`waeup.kofa.students.interfaces.IUGStudentClearance` describes an
additional set of schema fields which are exclusively used on form
pages. They do not play any role beyond that purpose. Any kind of
schema field can be safely added in customized versions of these
interfaces to meet the conditions of the university's matriculation
process. Also `date_of_birth` and `nationality` are not used in the
base package for further data processing which means, there is no
dependency on these two parameters. Attention: This might be
different in customized versions of Kofa. Some views might use these
parameters to restrict access or make actions (e.g. payment of items)
conditional on the student's nationality or current age.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IUGStudentClearance

`clearance_locked` controls the access to the edit form page of
clearance data. The corresponding attribute is automatically set by
workflow transitions to lock or unlock the edit form page
respectively. The attribute can also be set by officers via the
manage form page to lock or unlock the page manually.

`officer_comment` is usually edited by clearance officers when
rejecting clearance previously requested by the student. The
attribute contains the message which informs the student about the
reasons of rejection. The attribute is cleared after final
clearance. The message can be also found in ``students.log``.

Both `clearance_locked` and `officer_comment` are controlled by
workflow transitions not by states, see below.

`IPGStudentClearance`
---------------------

Most universities acquire different data from undergraduate (UG) and
postgraduate (PG) students. The forms vary widely. Therefore Kofa
offers a second interface for acquiring PG clearance data. In the
base package `IPGStudentClearance` inherits from the
`IUGStudentClearance` interface. The additional `employer` field in
the base package only serves as an example.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IPGStudentClearance

`IStudentPersonal`
------------------

`waeup.kofa.students.interfaces.IUGStudentPersonal` defines an
additional set of personal student data which are permantly editable
by students. The set usually contains further contact data and
information about the student's relatives.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentPersonal

Kofa provides a mechanism which ensures that personal data are being
kept up to date. Students are regularly requested to update the
personal data directly after login. The personal data expire 180
days after saving the data for the last time which is stored in the
`personal_updated` attribute. Then the `personal_data_expired`
property returns ``True`` and the student is redirected to the
personal data edit page when logging in.

`IStudentNavigation`
--------------------

See docstring.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentNavigation

Student Study Course Interfaces
===============================

All data related to an individual course of study are stored with
the ``studycourse`` object. This container object is an instance of
the `StudentStudyCourse` class which implements
`waeup.kofa.students.interfaces.IStudentStudyCourse`,
`waeup.kofa.students.interfaces.IStudentNavigation` and
`waeup.kofa.students.interfaces.IStudentStudyCourseTranscript`. The
latter does not add further behaviour to our classes but is needed
for transcript pages only. It is not described in the user handbook.

`IStudentStudyCourse`
---------------------

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentStudyCourse

All attributes are read-only property attributes which are computed
dynamically.

The first schema field is a `Choice` field which allows values from
the `CertificateSource`. The source provides all certificates stored
in the portal. This way, `StudentStudyCourse` objects point to
exactly one `Certificate` object in the portal. If the certificate
is removed, an event handler takes care of clearing also all
referring `certificate` attribute. The tokens of the
`CertificateSource` are the certicate codes which means, that in
forms and import files the unique code must be given and the desired
`Certificate` object will be stored.

The interface has two entry parameter fields. `entry_mode` stores
the study mode of the programme and `entry_session` the academic
year when the study course was started. Usually these parameters are
fixed and must not be changed during course of study.

Very important - or even most important - are the parameters which
describe the current state of the student's study course.
`current_session`, `current_level`, `current_verdict`,
`previous_verdict` and the student's workflow state (see below)
declare precisely in which academic session and how successfully the
student has reached the current study level and state in the portal.
All these attributes are set automatically by the portal und must
(normally) not be changed via manage form pages or import.

What is a verdict? A verdict is the individual judgement of a jury
(senate in Nigeria) at the end of each academic session. The jury's
verdict tells the portal, if the student has successfully completed
an academic session or not. Depending on the verdict, the student
will be either allowed to proceed to the next study level or forced
to repeat the current level. Without a verdict, the student gets
stuck and cannot even pay school fees for the next academic year.
This will be further exlplained in the workflow section below.

`StudentStudyCourse` is a container class. Study courses contain
`StudentStudyLevel` instances which implement
`waeup.kofa.students.interfaces.IStudentStudyLevel` and also
`waeup.kofa.students.interfaces.IStudentNavigation`, see above.

`IStudentStudyLevel`
--------------------

`StudentStudyLevel` instances contain information about the study
progress achieved at that level. In Kofa study levels range from 100
to 900. There are two additional levels: a pre-studies level (10)
and a special postgraduate level (999). There are also two probation
levels per regular study level. Level 120, for instance, means level
100 on second probation. See `complete numbering of study levels
<https://kofa-demo.waeup.org/sources#collapseStudyLevels>`_ in the
base package.

`StudentStudyLevel` instances are container objects which contain
course tickets. We therefore sometimes speak of a level course list
instead of a study level. The study level stores and provides the
information when (`validation_date`) and by whom (`validated_by`)
the course list was validated, in which session the level was taken
(`level_session`) and which verdict the student finally obtained.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentStudyLevel

`StudentStudyLevel` instances also compute some statistics on the
fly to give an overview of the courses taken. These read-only
property attributes are: `number_of_tickets`, `passed_params`,
`gpa_params`, `gpa_params_rectified`, `cumulative_params`,
`total_credits` and `gpa`. The attentive reader may wonder why the
latter two are not listed in the attributes section of the interface,
but as read-only schema fields further below. This is a trick which
we used to properly display these fields on some display pages and
pdf slips. However, the `attrs_to_fields` function explicitly
excludes them when starting the portal, so that these fields are not
used for persistent storage of same-named attributes in the database.

The property attribute `course_registration_allowed` determines
whether course registration has ended. In the base package students
can proceed if they have paid late registration fee. The conditions
for course registration can be configured in custom packages.

`ICourseTicket`
---------------

Course tickets allow students to attend a course. Lecturers can
enter scores at the end of the term. A `CourseTicket` instance
contains a copy of the original `Course` and `CertificateCourse`
data. If the courses and/or the referring certificate courses are
removed, the corresponding tickets remain unchanged. So we do not
need any event triggered actions on course tickets.

The `CourseTicket` implements
`waeup.kofa.students.interfaces.ICourseTicket` and also
`waeup.kofa.students.interfaces.IStudentNavigation`, see above.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: ICourseTicket

The quite long list of schema fields pretends that form pages may
provide these fields for editing. This is not the case. Except for
`score`, all these fields are 'for display' only. They can neither
be changed through the UI nor by batch processing (import). They are
solely meant for backing up the orginal course data. See also
:ref:`course_ticket_processor`.

.. note::

  It may happen that a course has been accidentally misconfigured, for
  example the number of credits was set too high. The course object
  can be corrected, but, course tickets, which refer to this course,
  can not. They are neither adjusted automatically nor changeable by
  the batch processor. The only solution to 'adjust' course tickets is
  to replace them by new tickets.

Student Payment Interfaces
==========================

`IStudentOnlinePayment`
-----------------------

`IStudentOnlinePayment` instances are called student payment tickets
or sometimes only payments. They contain the data which confirm that
the student has paid a specific fee.
`waeup.kofa.students.interfaces.IStudentOnlinePayment` inherits from
`waeup.kofa.payments.interfaces.IOnlinePayment` and has only two
additional schema fields: `p_current` and `p_level` which are
student-specific. It also promises three additional methods which
process student data after successful or approved payment.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IStudentOnlinePayment

Student Accommodation Interfaces
================================

`IBedTicket`
------------

A bed ticket confirms that a bed space in a hostel has been
allocated to the student for the period of an academic session
(`booking_session`). The `bed_coordinates` specify which bed space
has been booked. Sometimes this value is too cryptic and
inappropriate to guide the student to the bed space. The
`display_coordinates` property can be used to 'translate' the
coordinates and display a customary description of the bed space.
Much like some study level attributes, also `display_coordinates` is
defined as a read-only schema field in order to automatically
display the field on form pages. It is excluded by the
`attrs_to_fields` function and thus not stored in the database.

.. literalinclude:: ../../../../src/waeup/kofa/students/interfaces.py
   :pyobject: IBedTicket

.. _zope schema: http://docs.zope.org/zope.schema
