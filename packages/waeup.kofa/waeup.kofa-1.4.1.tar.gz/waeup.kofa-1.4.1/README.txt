What is WAeUP.Kofa ?
********************

Kofa means 'entrance' or 'portal' in Hausa language.

WAeUP.Kofa is a multifunctional, open source, web based student
management system to provide transparent and comprehensive
information about application and study progress. The system
controls all kinds of application and student registration processes
at large schools and universities in Nigeria. It is a generic system
which can be deployed by, and is useful to most universities,
colleges or schools wordlwide.

WAeUP.Kofa is the flagship of the West African eUniversity Project
(WAeUP). See http://www.waeup.org to learn more about WAeUP.

WAeUP.Kofa is really an allrounder. The best way to briefly describe
its functionality, is to explain what the software can *not* do for
you, rather than trying to describe all its features in just a few
words. Kofa is primarily not an e-learning system, although, it has
some basic content management features which can be used by
lecturers to disseminate course material. Kofa is also not a
scheduler which generates lesson plans or timetables for lecturers
or students. Although students register their courses with Kofa and
can see or print course lists for each academic session, so far,
courses do not contain information, when or where they take place.
However, due to the modular design of Kofa, a scheduler or room
planner could be easily added.

WAeUP.Kofa is divided into sections. Each section has its own folder
in Kofa's `object database`. When starting Kofa in debug mode::

  $ ./bin/kofactl debug

we can use simple Python expression to view the first two levels of
the database structure::

  >>> list(root.keys())
  [u'app']
  >>> list(root['app'].keys())
  [u'accesscodes', u'applicants', u'configuration', u'datacenter',
   u'documents', u'faculties', u'hostels', u'mandates', u'reports',
   u'students', u'users']


The section/folder structure can be figured as follows::

  root (Database Root)
  |
  +---> app (University)
        |
        +---> faculties (Academic Section)
        |
        +---> students (Students Section)
        |
        +---> applicants (Aplicants Section)
        |
        +---> documents (Documents Section)
        |
        +---> hostels (Accommodation Section)
        |
        +---> accesscodes (Access Codes Section)
        |
        +---> configuration (Configuration Section)
        |
        +---> users (Officers)
        |
        +---> datacenter (Data Center)
        |
        +---> mandates (Mandates)
        |
        +---> reports (Reports)

The user handbook follows this organizational structure and adds
further chapters where needed. Also installation instructions and
basic information about customization can be found there.

You can also find latest docs at https://kofa-doc.waeup.org/
