.. _import_stages:

Stages of Batch Processing
**************************

.. seealso::

   :ref:`Data Center Doctests <datacenter_txt>`

The term 'data import' actually understates the range of funcnctions
importers really have. As already stated, many importers do not only
restore data once backed up by exporters or, in other words, take
values from CSV files and write them one-on-one into the database.
The data undergo a complex staged data processing algorithm.
Therefore, we prefer calling them 'batch processors' instead of
importers. The stages of the import process are as follows.

Stage 1: File Upload
====================

Users with permission
:py:class:`waeup.manageDataCenter<waeup.kofa.permissions.ManageDataCenter>`
are allowed to access the data center and also to use the upload
page. On this page they can access an overview of all available
batch processors. When clicking on a processor name, required,
optional and non-schema fields show up in the modal window.
Also a CSV file template, which can be filled and uploaded to avoid
header errors, is being provided in this window.

Many importer fields are of type 'Choice', which means only definied
keywords (tokens) are allowed, see :ref:`schema fields <kofa_schemas>`.
An overview of all sources and vocabularies, which feed the
choices, can be also accessed from the datacenter upload page and
shows up in a modal window. Sources and vocabularies of the base
package can be viewed `here <http://kofa-demo.waeup.org/sources>`_.

Data center managers can upload any kind of CSV file from their
local computer. The uploader does not check the integrity of the
content but the validity of its CSV encoding (see
:py:func:`check_csv_charset<waeup.kofa.utils.helpers.check_csv_charset>`).
It also checks the filename extension and allows only a limited
number of files in the data center.

.. autoattribute:: waeup.kofa.browser.pages.DatacenterUploadPage.max_files
   :noindex:

If the upload succeeded the uploader sends an email to all import
managers (users with role
:py:class:`waeup.ImportManager<waeup.kofa.permissions.ImportManager>`)
of the portal that a new file was uploaded.

The uploader changes the filename. An uploaded file ``foo.csv`` will
be stored as ``foo_USERNAME.csv`` where username is the user id of
the currently logged in user. Spaces in filename are replaced by
underscores. Pending data filenames remain unchanged (see below).

After file upload the data center manager can click the 'Process
data' button to open the page where files can be selected for import
(**import step 1**). After selecting a file the data center manager
can preview the header and the first three records of the uploaded
file (**import step 2**). If the preview fails or the header
contains duplicate column titles, an error message is raised. The
user cannot proceed but is requested to replace the uploaded file.
If the preview succeeds the user is able to proceed to the next step
(**import step 3**) by selecting the appropriate processor and an
import mode. In import mode ``create`` new objects are added to the
database, in ``update`` mode existing objects are modified and in
``remove`` mode deleted.

Stage 2: File Header Validation
===============================

Import step 3 is the stage where the file content is assessed for
the first time and checked if the column titles correspond with the
fields of the processor chosen. The page shows the header and the
first record of the uploaded file. The page allows to change column
titles or to ignore entire columns during import. It might have
happened that one or more column titles are misspelled or that the
person, who created the file, ignored the case-sensitivity of field
names. Then the data import manager can easily fix this by selecting
the correct title and click the 'Set headerfields' button. Setting
the column titles is temporary, it does not modify the uploaded
file. Consequently, it does not make sense to set new column titles
if the file is not imported afterwards.

The page also calls the `checkHeaders` method of the batch processor
which checks for required fields. If a required column title is
missing, a warning message is raised and the user can't proceed to
the next step (**import step 4**).

.. important::

  Data center managers, who are only charged with uploading files but
  not with the import of files, are requested to proceed up to import step 3
  and verify that the data format meets all the import criteria and
  requirements of the batch processor.

Stage 3: Data Validation and Import
===================================

Import step 4 is the actual data import. The import is started by
clicking the 'Perform import' button. This action requires the
:py:class:`waeup.importData<waeup.kofa.permissions.ImportData>`
permission. If data managers don't have this permission, they will
be redirected to the login page.

Kofa does not validate the data in advance. It tries to import the
data row-by-row while reading the CSV file. The reason is that
import files very often contain thousands or even tenthousands of
records. It is not feasable for data managers to edit import files
until they are error-free. Very often such an error is not really a
mistake made by the person who compiled the file. Example: The
import file contains course results although the student has not yet
registered the courses. Then the import of this single record has to
wait, i.e. it has to be marked pending, until the student has added
the course ticket. Only then it can be edited by the batch processor.

The core import method is:

.. automethod:: waeup.kofa.utils.batching.BatchProcessor.doImport()
   :noindex:

Stage 4: Post-Processing
========================

The data import is finalized by calling
:py:meth:`distProcessedFiles<waeup.kofa.datacenter.DataCenter.distProcessedFiles>`.
This method moves the ``.pending`` and ``.finished`` files as well as the
originally imported file from their temporary to their final location in the
storage path of the filesystem from where they can be accessed through the
browser user interface.
