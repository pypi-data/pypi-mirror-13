.. _datacenter_intro:

Introduction
************

.. _object_database:

The Object Database
===================

Most web portals store their data in a relational database like
PostgreSQL, MySQL or Oracle. A relational database is organized in
tables of rows and columns, with a unique key for each row. Each data
entity gets its own table. Rows in tables can be linked to rows in
other tables by storing the unique key of the row to which it should
be linked. This sounds quite simple. Many computer users are familiar
with this kind of data storage because they are used to spreadsheet
programmes like Excel oder Calc which also organize data in tables.
Kofa's persistent data are stored in a native object database designed
for the Python programming language, the so-called ZODB_. An object
database stores objects with attributes and not records as rows with
columns in tables. These persistent objects can hold any kind of
information in attributes and must not adhere to a specific schema
like records in tables of a relational database.

The ZODB_ also supports a hierarchical, treelike storage of objects.
Objects can contain other objects if they are declared as containers.
Objects are stored like folders and files in a filesystem. This makes
the object handling very fast and transparent because we can access
objects, or more precisely views of objects, by indicating their path
in the database, i.e. by traversing the database tree to the object's
location. Furthermore, we are accessing the views of objects through a
web browser by entering a URL (Uniform Resource Locator). This
publication path corresponds more or less to the traversal path of our
objects. In Kofa the path always contains the object identifiers of
all objects which are passed when traversing the database tree.
Example:

https://kofa-demo.waeup.org/students/K1000000/studycourse/100/DCO

is the URL which requests a display view of a course ticket with id
``DCO``. This object is stored in a study level container object with
id ``100``, stored in a study course container object with id
``studycourse``, stored in the student container object with id
``K1000000``, stored in the students root container, stored in the
root container of the application, stored in the root of the database
itself.

This kind of storage requires that each object gets a unique object
identifier (object id) within its container. The id string is visible
in the browser address bar. Though it's technically possible for ids
to contain spaces or slashes we do not allow these kinds of special
characters in object ids to facilitate the readability of URLs.

Batch Processing
================

Administrators of web portals, which store their data in relational
databases, are used to getting direct access to the portal's database.
There are even tools to handle the administration of these databases
over the Internet, like phpMyAdmin or phpPgAdmin to handle MySQL or
PostgreSQL databases respectively. These user interfaces bypass the
portals' user interfaces and give direct access to the database. They
allow to easily import or export (dump) data tables or the entire
database structure into CSV or SQL files. What at first sight appears
to be very helpful and administration-friendly proves to be very
dangerous on closer inspection. Data structures can be easily damaged
or destroyed, or data can be easily manipulated by circumventing the
portal's security machinery or logging system. Kofa does not provide
any external user interface to access the ZODB_ directly, neither for
viewing nor for editing data. This includes also the export and import
of sets of data. Exports and imports are handled via the Kofa user
interface itself. This is called batch processing which means either
producing CSV files (comma-separated values) from portal data (export)
or processing CSV files in order to add, update or remove portal data
(import). Main premise of Kofa's batch processing technology is that
the data stored in the ZODB_ can be specifically backed up and
restored by exporting and importing data. But that's not all. Batch
processors can do much more. They are an integral part of the student
registration management.

.. note::

  Although exporters are part of Kofa's batch processing module, we will
  not call them batch processors. Only importers are called batch
  processors. Exporters produce CSV files, importers process them.


.. _ZODB: http://www.zodb.org/