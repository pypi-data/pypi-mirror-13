.. _accommodation_section:

Accommodation Section
*********************

The accommodation section is a built-in hostel management system.
African universities usually run their own student hostels which are
built on their huge university campuses. They combine the booking of
beds with the registration process. There are two major use cases.
Students either have to book a bed space before they can continue
with the registration, or they are only allowed to book, if they
have reached a certain registration state. In the first case, the
university requires students to stay on campus. They usually have
enough beds for all of their students and need to fill up the
hostels. In the second case, bed space is limited. Since
accommodation on campus is usually very reasonable and much safer
than on the free market outside, students prefer to stay on campus.
If bed allocation e.g. requires the payment of school fees, the
university benefits from bed shortage, because students are forced
to pay in order to get the highly coveted hostel bed.

From the database's point of view, the accommodation section is a
container of type `HostelsContainer` with id ``hostels``, which is
located in the `IUniversity` instance. It contains hostels
(instances of `IHostel`) which again contain the beds (instances of
`IBed`).

The :ref:`treelike storage of objects <object_database>` in the
accommodation section can be figured as follows::


  Accommodation Section (HostelsContainer)
  |
  +---> Hostel
        |
        +---> Bed

Interfaces
==========

`IHostelsContainer`
-------------------

The unique hostels container serves also as a configuration object.
It defines for which academic session booking is enabled. The
student's `current_session` must match the `accommodation_session`.
It also defines the booking period and the registration workflow
states for which booking is allowed, see :ref:`bed_tickets`. The
only property attribute is `expired` which returns ``True`` if the
current datetime is within the booking period.

.. literalinclude:: ../../../src/waeup/kofa/hostels/interfaces.py
   :pyobject: IHostelsContainer

`IHostel`
---------

The hostels container contains the various `Hostel` objects. Hostels
are buildings with blocks, floors rooms and beds. When adding a
hostel, the form page is requesting the hostel's name. The
`hostel_id` is derived from the name by applying
:code:`lower().replace(' ','-').replace('_','-')` to it. As usual,
the id will be omitted in manage forms and can thus not be changed
after hostel creation.

The add and manage form pages let us define the 'dimensions' of the
hostel and configure blocks with their assignment to either
female or male students. And they are requesting the number of
floors per block as well as the number of rooms per floor. All
blocks have the same number of floors with a fixed number of rooms
and a fixed number of beds per room. If beds or even entire rooms do
not exist on a floor, these beds must be later marked reserved, so
that they are skipped during the automatic allocation process, see
below.

.. note::

  Blocks for either female or male students? Does Kofa's hostel
  management accommodate girls and boys strictly separately? No,
  it doesn't. Blocks are not necessarily real buildings. They can
  be used as virtual subunits. If the entire hostel has only one
  block, then yes, either only female or only male students can be
  hosted in such a hostel. If two blocks are configured (one for
  male and one for female students), beds of the same room can be
  assigned twice, once in Block A and a second time in Block B.
  Consequently, one bed of such a bed pair must be set 'reserved'
  (see below) to avoid double allocation. In other words, there is
  always a trick which allows even such uncommon configurations.
  Not many universities will allow girls and boys to stay in the
  same room.

.. literalinclude:: ../../../src/waeup/kofa/hostels/interfaces.py
   :pyobject: IHostel

Beds can be dedicated to pre-study students, fresh students
(`entry_session` and the hostels container's `accommodation_session`
correspond), final-year students (`current_level` and the
certificate's `end_level` correspond, or is even higher) and
returning students (non-fresh and non-final-year students). Or they
can be made bookable for all students (beds without category). The
latter bed type can be configured but is not being used in the base
package by
:py:meth:`getAccommodationDetails<waeup.kofa.students.utils.StudentsUtils.getAccommodationDetails>`,
the method which determines the appropriate bed type of the
student.

Usually, not every student can be accommodated in every hostel.
Faculties are sometimes far apart and do manage their own student
hostels. These hostels require a 'special handling' in
:py:meth:`getAccommodationDetails<waeup.kofa.students.utils.StudentsUtils.getAccommodationDetails>`.
The special handling code must be set on the add and manage form
pages of hostels.

The interface defines also two schema invariants
(invariant-decorated methods). These methods validate one or more
depending schema fields. In our case, the methods take care that
blocks and beds are not assigned twice.

All the parameters above define the construction rules for beds when
filling the hostel with beds, which is done by the `updateBeds`
method described further below.

`IBed`
------

.. literalinclude:: ../../../src/waeup/kofa/hostels/interfaces.py
   :pyobject: IBed

The `bed_id` contains the 'coordinates' of the bed. It tells us
precisely in which hostel, in which block, on which floor and in
which room the bed can be found. The bed id is composed as follows:
``[hostel id]_[block letter]_[room number]_[bed letter]``. The room
number contains the floor level: :code:`room_nr = floor*100 + room`.
Example: ``hall-1_A_101_C`` means that the bed is located in Hostel
1, Block A, 1st Floor, Room 101 (or 1) and labelled with 'C'.

The `bed_type` attribute is similarly being constructed. It
describes which kind of student can be allocated: ``[special
handling code]_[sex]_[stage]``. Example: ``regular_female_re`` means
that this bed can be booked by regular female returning students.
Other stages are: ``fr`` (fresh), ``pr`` (pre-study), ``fi``
(final-year) and ``all`` (all students).

Beds of each hostel are consecutively numbered (`bed_number`).

Except for `owner`, all attributes of bed objects are being
determined by the system, no matter if they are property or schema
field attrributes. They can neither be edited nor imported (there is
no batch processor for beds). The `owner` attribute contains the
student id, if the bed is occupied. This attribute is either set by
Kofa when the student creates a bed ticket (see :ref:`bed_tickets`),
or can be set via the `BedManageFormPage`, see below. The
`allowed_owners` schema invariant ensures (1) that the selected user
exists, (2) that the student's current session corresponds with the
accommodation session and (3) that the student doesn't reside in
another bed.

.. _hostels_pages:

Browser Pages
=============

.. seealso::

   :ref:`Manage Hostel Python Test <test_manage_hostels>`

Update Beds
-----------

Hostels are empty after creation and configuration. They do not
contain any bed. The hostel's
:py:meth:`Hostel.updateBeds<waeup.kofa.hostels.hostel.Hostel.updateBeds>`
method must be called to fill the hostel with beds according to
the hostel's configuration parameters. This is done by the
same-named action of the `HostelManageFormPage`. `Hostel.updateBeds`
iterates over all block letters, floor levels, room numbers and bed
letters, which have been configured on the `HostelManageFormPage`.
In each bed letter iteration loop a bed is added and the `bed_id`,
`bed type` as well as the consecutive `bed_number` are determined
and stored with the bed.

As the method's name already promises, it does not only add beds to
an empty hostel container, but also updates existing beds after
re-configuration. It does this by removing all empty beds before the
iteration starts. Occupied beds remain in the hostel but get the bed
number ``9999``. When iterating over the newly configured blocks,
floors, rooms and bed letters, Kofa checks first, if the bed belongs
to the group of remaining beds, which could not be removed because
they are occupied. If so, the bed type is adjusted and the bed
number changed. The bed remains occupied by the same student, no
matter if the student meets the newly configured conditions or not.

It might happen that e.g. a room for male students is converted into
a room for female students, but a male student still resides in this
room. This has to be checked and the student has to be relocated
manually, see :ref:`student_relocation`. Moreover, due to the
reconfiguration of the hostel, an occupied bed may no longer exist
or offered for booking. This is then indicated by the bed number
``9999``. Also these students must be relocated manually.


Switch Reservations
-------------------

Beds can be blocked by switching ther reservation status. The switch
replaces the stage part of `bed_type` by ``_reserved``. Example:
``regular_female_re`` becomes ``regular_female_reserved``. Switching
again, reverts this process.

Reserved beds won't be allocated automatically. The beds remain
empty during the hostel booking period. Students can only be
allocated manually to reserved beds, which is done via the
`BedManageFormPage`, see below.

Release Beds
------------

Releasing a bed does not simply mean clearing the `owner` attribute
of the bed object. The student has to be notified that booking has
been cancelled. This is done by replacing the `bed_coordinates` of
the student's bed ticket. Instead of the coordinates, the student
will read: ``-- booking cancelled on <datetime of cancellation> --``.

Manage Bed
----------

Not many things can be managed on this form page. As mentioned above,
only the `owner` attribute can be changed by entering a student id.
The id is being validated by a schema invariant. The manage form
page cannot be accessed, if a student has aleady been allocated.
Beds must be released first, before they can be allocated to other
students.
