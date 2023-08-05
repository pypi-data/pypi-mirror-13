.. _documents:

Documents Section
*****************

The documents section of Kofa is a tiny built-in content management
system (CMS), which has been developed mainly for publishing
announcements, adverts, instructions or general information provided
by the university to inform prospective students about application
and registration procedures.

Technically speaking, the documents section is a container of type `DocumentsContainer` with id ``documents``, which is located in the `IUniversity` instance and which contains public documents. There are three types of public documents::

  Documents Section (DocumentsContainer)
  |
  +---> PDFDocument
  |
  +---> HTMLDocument
  |
  +---> RESTDocument

The first can be used to provide pdf files for download. The second
and third can be used to create multi-lingual static html pages on
the portal. HTML documents expect html coded text as input, REST
documents expect `reStructuredText <http://docutils.sf.net/rst.html>`_
which is transformed into html.

Interfaces
==========

The base for all three document interfaces is `IPublicDocument`
which inherits from `IDocument`. All attributes are read-only
properties, i.e. attributes with a getter method only. These
properties are computed dynamically and can't be set. Only the
`document_id` and the `title` can be entered on form pages or can be
imported.

.. literalinclude:: ../../../src/waeup/kofa/documents/interfaces.py
   :pyobject: IDocument

.. literalinclude:: ../../../src/waeup/kofa/documents/interfaces.py
   :pyobject: IPublicDocument

A PDF Document further specifies which pdf files are connected to
the object. Usually, only one filename is in the `filenames` tuple.

.. literalinclude:: ../../../src/waeup/kofa/documents/interfaces.py
   :pyobject: IPDFDocument

HTML and REST documents have a schema field for multi-lingual
content in HTML or in REST format respectively, see :ref:`note
<multilingual>`. The hidden `html_dict` attributes contain the same
information after saving the form, but the sequence of language
translations has been split up and copied into a dictionary for
faster processing.

.. literalinclude:: ../../../src/waeup/kofa/documents/interfaces.py
   :pyobject: IHTMLDocument

.. literalinclude:: ../../../src/waeup/kofa/documents/interfaces.py
   :pyobject: IRESTDocument


Workflow
========

Public documents have a publication workflow with two states:
created and published. Only the content or attached files of
published documents can be seen by anonymous users::

                 a
    created ----------- published

    a: publish
   -a: retract

History & Logging
=================

All transitions are automatically logged in ``main.log`` and the
document's history. This is a sample history of public document::

  2015-07-05 07:31:32 UTC - Document created by Admin
  2015-07-05 07:31:53 UTC - Document published by Admin
  2015-07-05 07:31:57 UTC - Document retracted by Admin

The corresponding logfile excerpt is as follows::

  2015-07-05 09:31:32,848 - INFO - admin - demodoc - Document created
  2015-07-05 09:31:32,850 - INFO - admin - documents.browser.DocumentAddFormPage - added: HTML Document demodoc
  2015-07-05 09:31:39,025 - INFO - admin - documents.browser.HTMLDocumentManageFormPage - demodoc - saved: html_multilingual
  2015-07-05 09:31:43,279 - INFO - admin - documents.browser.HTMLDocumentManageFormPage - added: benny|waeup.local.DocumentManager
  2015-07-05 09:31:53,152 - INFO - admin - demodoc - Document published
  2015-07-05 09:31:57,216 - INFO - admin - demodoc - Document retracted
  2015-07-05 09:32:46,679 - INFO - admin - documents.browser.DocumentsContainerManageFormPage - removed: demodoc


Quick Guide
===========

How to add and reference an HTML document
-----------------------------------------

1. Click *Documents > Manage > Add document*.
2. Select *HTML Document*, fill fields and press *Add document*.
3. Enter multi-lingual content in HTML format and press *Save*.
4. Click *View > Transition*.
5. Select *Publish document* and press *Save*.

The document is now published and available to anonymous users.

6. Mark and copy the HTML Element provided on the page:
   ``<a href= ... /a>``.
7. Open another HTML document or a page with multi-lingual content
   and paste the element where needed.


How to add and reference a PDF document
---------------------------------------

1. Click *Documents > Manage > Add document*.
2. Select *PDF Document*, fill fields and press *Add document*.
3. Select *Files* and upload a pdf file from your computer.
4. Click *View > Transition*.
5. Select *Publish document* and press *Save*.

The document and the connected pdf file are now published and
available to anonymous users.

6. Open the HTML source with your browser, search for the ``a``
   element
7. Mark and copy the HTML element found:
   ``<a target="image" href= ... /a>``.
8. Open another HTML document or a page with multi-lingual content
   and paste the element where needed.
