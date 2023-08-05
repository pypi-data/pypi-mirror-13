Tutorial
========


.. note:: **Based on version 0.1.dev3!**
        Nothing should be *wrong* here, but for some examples more intuitive or comfortable solutions might be provided.
        Have a look at the `Package API <biblib.html>`_.


Parsing a BibTeX file into database object
------------------------------------------

Lets assume we have the following BibTeX sample file ``bibtex.bib``::

    % This file was created with JabRef 2.10b2.
    % Encoding: UTF8

    @Article{JCP-127-234509,
      Title                    = {Homogeneous nucleation and growth in supersaturated zinc vapor investigated by molecular dynamics simulation},
      Author                   = {F. R\"{o}mer and T. Kraska},
      Journal                  = {Journal of Chemical Physics},
      Year                     = {2007},
      Number                   = {23},
      Pages                    = {234509},
      Volume                   = {127},
      Doi                      = {10.1063/1.2805063},
    }

    @Article{EPL-2015,
      Title                    = {Dense brushes of stiff polymers or filaments in fluid flow},
      Author                   = {F. Römer and D. A. Fedosov},
      Journal                  = {EPL (Europhysics Letters)},
      Year                     = {2015},
      Number                   = {6},
      Pages                    = {68001},
      Volume                   = {109},
      Doi                      = {10.1209/0295-5075/109/68001}
    }


To read the BibTeX file into a database object (:class:`.BibDB`), which might be often the initial step,
we use a :ref:`reader function <api-reader>` (here :meth:`biblib.db_from_file`), simply like:

.. code-block:: py

    >>> import biblib

    >>> dbObj = biblib.db_from_file('bibtex.bib')

Now we have access on the database level by the methods provided by the :class:`.BibDB` class,
and to the individual bibliographic entries by the :class:`.Entry` methods.


Database properties
-------------------

A databse object has some properties:

.. code-block:: py

    >>> # A dictionary which contains the citation-keys and the BibTeX entry objects:
    >>> print dbObj.datadict
    {'JCP-127-234509': <biblib._entry.Article object at 0x7f9977e1c4d0>, 'EPL-2015': <biblib._entry.Article object at 0x7f9977ecebd0>}

    >>> # A list containing the BibTeX objects of the database:
    >>> print dbObj.data
    [<biblib._entry.Article object at 0x7f2d49de6410>, <biblib._entry.Article object at 0x7f2d49e98b10>]

    >>> # A list of the BibTeX citation-keys of the database:
    >>> print dbObj.ckeys
    ['JCP-127-234509', 'EPL-2015']

    >>> # A dictionary with doi as key and citation-key as value:
    >>> print dbObj.dois
    {u'10.1209/0295-5075/109/68001': 'EPL-2015', u'10.1063/1.2805063': 'JCP-127-234509'}

Becuase the *DOI* as well as the *citation-key* is of special interest, there are methods offered
to determine whether one exists in the database or not:

.. code-block:: py

    >>> print dbObj.has_ckey('EPL-2015')
    True
    >>> print dbObj.has_doi('10.1209/0295-5075/109/68001')
    True


Get, add, or delete a database entry
------------------------------------

Basic operations are natural to *get*, *add* or *delete* an entry. To do so, entries will be
addressed by their *citation-key*, which is always unique in a database.
The method :meth:`.BibDB.get_entry` simple returns the respective entry object:

.. code-block:: py

    >>> # Lets retrieve the JCP article...
    >>> entryObj = dbObj.get_entry('JCP-127-234509')

    >>> # and for example. print the contents of the journal tag:
    >>> print entryObj.get_tag('journal')
    Journal of Chemical Physics

In order to add an entry object, we first need to create one. The example below shows the method how to create it
from scratch by using the classmethod :meth:`.Entry.get_Instance` with a dictionary containing the initial values.
There are far more options to create entry object or to add one to the database, which will be discussed
in detail later.

.. code-block:: py

    >>> # First we setup a dictionary containing the initial data, ..
    >>> inputdict = {'ENTRYTYPE': 'mastersthesis', 'ID': 'Mayer2008',
                 'author': u'Hans. H. Mayer',
                 'school': u'University of Nowhere'
                 'title': u'A very interesting thesis.',
                 'year': u'2008',}

    >>> # and than create the entry object.
    >>> newEntry = biblib.Entry.get_Instance(inputdict)

    >>> # Now we can add the new entry to the database:
    >>> dbObj.add_entry(newEntry)

    >>> # lets look if it worked ;)
    >>> print dbObj.ckeys
    ['Mayer2008', 'JCP-127-234509', 'EPL-2015']

The method :meth:`.BibDB.add_entry` provides the option *method*, which controls how to handle the citation-key.
We will have a closer look at this in a :ref:`separate chapter <addMethod>` later.

To delete an entry from the database, simply call the :meth:`.BibDB.del_entry` method:

.. code-block:: py

    >>> dbObj.del_entry('EPL-2015')
    >>> print dbObj.ckeys
    {'Mayer2008': <biblib._entry.Mastersthesis object at 0x7f25456d6810>, 'JCP-127-234509': <biblib._entry.Article object at 0x7f25456d64d0>}


Modify a database entry
-----------------------

Actually there are two modifications of a bibliographic entry which have to made on the database level:
updating the citation-key (:meth:`.BibDB.update_ckey`) and
changing the BibTeX entry type (:meth:`.BibDB.mod_entry_type`):

.. code-block:: py

    >>> # lets promote H. H. Mayer to PhD ;) ,...
    >>> dbObj.mod_entry_type('Mayer2008','phdthesis')

    >>> # and change the citation-key of the JCP article.
    >>> dbObj.update_ckey('JCP-127-234509','Roemer2007')

    >>> # This we get..
    >>> print dbObj.datadict
    {'Mayer2008': <biblib._entry.Phdthesis object at 0x7f2545788bd0>, 'Roemer2007': <biblib._entry.Article object at 0x7f25456d64d0>}

Of course, when you intend to change the type of an entry, you need to ensure that the new entry type is valid.
At the end of this tutorial you find a :ref:`list of valid BibTeX entry types <entryTypes>`.


Entry properties & tags
-----------------------

We can also access to the properties of the individual entry objects at their level:

.. code-block:: py

    >>> # Lets retrieve the PhD thesis...
    >>> entryObj = dbObj.get_entry('Mayer2008')

    >>> # The BibTeX entry type of the entry object.
    >>> print entryObj.BibTeXType
    phdthesis

    >>> # BibTeX tag names and contents of the entry object as key-value pairs in a dictionary.
    >>> print entryObj.datadict
    {'school': u'University of Nowhere', 'author': u'Hans H. Mayer', 'title': u'A very interesting thesis.', 'year': u'2008', 'ENTRYTYPE': 'phdthesis', 'ID': 'Mayer2008'}

    >>> # The initial BibTeX citation-key of the entry object.
    >>> print entryObj.ckey
    Mayer2008

    >>> # A list of dictionaries for the author(s).
    >>> print entryObj.authors
    [{'given': u'Hans H.', 'family': u'Mayer'}]

The property :attr:`.Entry.authors` contains only a reasonable contents, if the ``author`` tag contents is in a :ref:`valid BibTeX format <authorForm>`.
This might be not every time the case, even if you retrieve citation data from publishers websites e.g., so be careful!
Also you should note, that the citation-key stored in an entry object (:attr:`.Entry.ckey`) does not have to be equal with its
referring citation-key in the database, it keeps always its *initial* value as shown here:

.. code-block:: py

    >>> # As you remember, we have changed the citation-key of the JCP article above,
    >>> # but when we call the object property, we get...
    >>> print dbObj.get_entry('Roemer2007').ckey
    JCP-127-234509

With the methods :meth:`.Entry.get_tag`, :meth:`.Entry.set_tag` and :meth:`.Entry.del_tag` you can access the individual
*tags* (aka *fields*) of an entry object:

.. code-block:: py

    >>> # Here we retrieve the 'title' tag:
    >>> print entryObj.get_tag('title')
    A very interesting thesis.

    >>> # If we request a non defined tag, we get a 'None' instead of a KeyError:
    >>> print entryObj.get_tag('doi')
    None

    >>> # Lets update the 'title' tag, ...
    >>> entryObj.set_tag('title',u'Mayers PhD thesis')
    >>> # and delete the 'school' tag.
    >>> entryObj.del_tag('school')
    >>> print entryObj.datadict
    {'author': u'Hans H. Mayer', 'title': u'Mayers PhD thesis', 'year': u'2008', 'ENTRYTYPE': 'phdthesis', 'ID': 'Mayer2008'}


BibTeX entries have mandatory tags depending on the :ref:`entry type <entryTypes>`.
Because in real life the bibliographic data sets are often incomplete, we decided to make the library not that
strict. Therefore, no error or warning will raised, if an entry object did not hold all mandatory tags.
Nevertheless, we thought it would be worth to provide a method to check if an entry is *complete* or not.
The properties :attr:`.Entry.is_complete` and :attr:`.Entry.missingTags` will do this:

.. code-block:: py

    >>> # The 'Phdthesis' type has the following mandatory fields:
    >>> print entryObj.mandatoryTags
    ['author', 'title', 'school', 'year']

    >>> # Because we have deleteted the 'school' tag recently, the entry object is incomplete:
    >>> print entryObj.is_complete
    False

    >>> print entryObj.missingTags
    ['school']

    >>> # If we now reset the 'school' tag:
    >>> entryObj.set_tag('school','University of Elsewhere')
    >>> print entryObj.is_complete
    True


Get citation by DOI
-------------------

Nearly very modern publication has its *Digital Object Identifier* (DOI).
The `International DOI Foundation`_ (IDF) offers by a webservice not only to retrieve the URL for a respective
publications, but also bibliographic meta data.
To use this service in a comfortable manner within this library two :ref:`reader functions <api-reader>`
are implemented: :func:`.entry_from_doi` to retrieve a entry object for a single citation, and :func:`.db_from_doiList`
to retrieve a database based on a list od DOIs.
The following example will show you how easy you can catch a BibTeX entry by its DOI:

.. code-block:: py

    >>> # We have a DOI, like
    >>> doi = '10.1088/0959-5309/43/5/301'
    >>> # and retrieve now a new entry object ...
    >>> doiEntry = biblib.entry_from_doi(doi)
    >>> # we've got..
    >>> print biblib.entry_to_string(doiEntry)
    @article{Lennard_Jones_1931,
        author = {J E Lennard-Jones},
        doi = {10.1088/0959-5309/43/5/301},
        journal = {Proc. Phys. Soc.},
        month = {sep},
        number = {5},
        pages = {461-482},
        publisher = {{IOP}Publishing},
        title = {Cohesion},
        url = {http://dx.doi.org/10.1088/0959-5309/43/5/301},
        volume = {43},
        year = {1931}
    }


Get citation by ISBN
--------------------

Another unique identifier is the *International Standard Book Number* (ISBN).
Here we make use of the functionality of the `isbnlib`_.
Like for DOIs, we implemented here two functions to retrieve bibliographic data by the ISBN:
:func:`.entry_from_isbn` and :func:`.db_from_isbnList`.
Have a look at the example:

.. code-block:: py

    >>> # We have a ISBN
    >>> isbn = '978-0486647418'
    >>> # and retrieve now a new entry object ...
    >>> isbnEntry = biblib.entry_from_isbn(isbn)
    >>> # we've got..
    >>> print biblib.entry_to_string(isbnEntry)
    @book{9780486647418,
        author = {Sybren Ruurds de Groot and Peter Mazur},
        publisher = {Dover Publications},
        title = {Non-Equilibrium Thermodynamics},
        year = {1984}
    }


Merging databases
-----------------

...


Write a BibTeX file
-------------------

...


.. _cKeyTpl:

Citation-key template
---------------------

In order to offer a comfortable way to get a suitable citation-key for a new entry object,
the database object provides the method :meth:`.BibDB.proposeCKey`,
which proposes a BibTeX citation-key for a given entry object in the context of the database.
Therefore, one needs to define templates, which describe how a citation-key should be build up.
These templates are stored as strings, and consist of keywords enclosed in curly braces, like e.g. ``{family}{year}``.
Here the keywords refer to the BibTeX tag names, whose content of the respective entry object
will be replaced. Additionally to the :ref:`BibTeX tag names <entryTags>`, you can use:

* ``{family}`` and ``{given}``, which refer to the name of the *first* author (using :attr:`.Entry.authors`), as well as
* ``{cnt}`` to define the position of a counter element.

The database holds three attributes concerning the citation-key template:

* :attr:`.BibDB.ckey_tpl` template for a citation-key *without* a counter (default: ``{family}{year}``),
* :attr:`.BibDB.ckey_tpl_wc` template for a citation-key *with* a counter (default: ``{family}{year}{cnt}``), and
* :attr:`.BibDB.ckey_tpl_cnt` keyword for counter style for the citation-key template (default: ``alpha``).

The counter will be introduced, if citation-key without counter would collide because it already exists in the database.
Currently three different counter styles are implemented:

* ``alpha``: a,b,c,.. ,z
* ``Alpha``: A,B,C,.. ,Z
* ``num``: 1,2,3,...

.. note:: If you use ``{family}`` and/or ``{given}``, ensure that the *author* tag contents is in a :ref:`valid BibTeX name format <authorForm>`!


.. _addMethod:

Adding/merging *method*
-----------------------

When adding an entry to a database (:meth:`.BibDB.add_entry`) or when merging one database into another (:meth:`.BibDB.merge_bibdb`),
an important question is: *What should happen with the citation-key?*

A citation-key of an entry object may be invalid or may collide with an existing entry in the database.
In order to provide a robust scheme to add entries to a database, with respect to the citation-key, all methods which
are involved provide the option *method*. By default it is set to *None*,
which means an invalid or conflicting citation-key will raise a KeyError.
If *method* is:

    * ``'lazy'``: First try to use the given citation-key.
                  If it is already in use or invalid, :ref:`generate <cKeyTpl>` a new using the template.
    * ``'auto'``: Always use the template to :ref:`generate <cKeyTpl>` a proper citation-key.
    * ``'force'``: Use the given citation-key. If it is already in used, the old entry object will be replaced.
                  If it is invalid, :ref:`generate <cKeyTpl>` a new using the template.


.. _entryTypes:

BibTeX entry types
------------------

Here is a list of *valid* BibTeX entry types with a description when to use them [#f1]_.

There is a separate class available for each entry type, which is derived from the :class:`.Entry` class.
The names of the mandatory tags (as listed in the table) are stored in the respective (:attr:`.Entry.mandatoryTags`) property,
e.g. for the type *article* in :attr:`.Article.mandatoryTags`.

.. note:: If you need to use the keyword in the context of this library, **always use lowercase diction**!

+---------------+----------------------------------------------------------------------------------------------------+
| Keyword       | Description *(mandatory tags)*                                                                     |
+===============+====================================================================================================+
| article       | An article from a journal or magazine.                                                             |
|               | *(author, title, journal, year)*                                                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| book          | A book with an explicit publisher.                                                                 |
|               | *(author or editor, title, publisher, year)*                                                       |
+---------------+----------------------------------------------------------------------------------------------------+
| booklet       | A work that is printed and bound, but without a named publisher or sponsoring institution.         |
|               | *(title)*                                                                                          |
+---------------+----------------------------------------------------------------------------------------------------+
| inbook        | A part of a book, e.g., a chpater, section, or whatever and/or a range of pages.                   |
|               | *(author or editor, title, chapter and/or pages, publisher, year)*                                 |
+---------------+----------------------------------------------------------------------------------------------------+
| incollection  | A part of a book having its own title.                                                             |
|               | *(author, title, booktitle, publisher, year)*                                                      |
+---------------+----------------------------------------------------------------------------------------------------+
| inproceedings | An article in a conference proceedings.                                                            |
|               | *(author, title, booktitle, year)*                                                                 |
+---------------+----------------------------------------------------------------------------------------------------+
| manual        | Technical documentation.                                                                           |
|               | *(title)*                                                                                          |
+---------------+----------------------------------------------------------------------------------------------------+
| mastersthesis | A master's thesis.                                                                                 |
|               | *(author, title, school, year)*                                                                    |
+---------------+----------------------------------------------------------------------------------------------------+
| misc          | Use this type when nothing else fits.                                                              |
|               | *(None)*                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+
| phdthesis     | A Ph.D. thesis.                                                                                    |
|               | *(author, title, school, year.)*                                                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| proceedings   | Conference proceedings.                                                                            |
|               | *(title, year)*                                                                                    |
+---------------+----------------------------------------------------------------------------------------------------+
| techreport    | A report published by a school or other institution, usually numbered within a series.             |
|               | *(author, title, institution, year)*                                                               |
+---------------+----------------------------------------------------------------------------------------------------+
| unpublished   | A document having an author and title, but not formally published.                                 |
|               | *(author, title, note)*                                                                            |
+---------------+----------------------------------------------------------------------------------------------------+


.. _entryTags:

BibTeX entry tags
-----------------

Here is a list of *processed* BibTeX entry tags (aka fields) with a description what they should content [#f1]_.

.. note:: If you need to use the keyword in the context of this library, **always use lowercase diction**!

+---------------+----------------------------------------------------------------------------------------------------+
| Keyword       | Description                                                                                        |
+===============+====================================================================================================+
| abstract      | The abstract, which can contain multiple lines.                                                    |
+---------------+----------------------------------------------------------------------------------------------------+
| address       | Usually the address of the publisher or other institution.                                         |
+---------------+----------------------------------------------------------------------------------------------------+
| annote        | An annotation.                                                                                     |
+---------------+----------------------------------------------------------------------------------------------------+
| author        | The name(s) of the author(s), in :ref:`BibTeX name format <authorForm>`.                           |
+---------------+----------------------------------------------------------------------------------------------------+
| booktitle     | Title of a book, part of which is being cited.                                                     |
+---------------+----------------------------------------------------------------------------------------------------+
| chapter       | A chapter (or section or whatever) number.                                                         |
+---------------+----------------------------------------------------------------------------------------------------+
| comment       | A comment.                                                                                         |
+---------------+----------------------------------------------------------------------------------------------------+
| crossref      | The database key of the entry being cross-referenced.                                              |
+---------------+----------------------------------------------------------------------------------------------------+
| doi           | The digital object identifier (DOI) of the publication.                                            |
+---------------+----------------------------------------------------------------------------------------------------+
| edition       | The edition of a book (e.g., "Second").                                                            |
+---------------+----------------------------------------------------------------------------------------------------+
| editor        | Name(s) of editor(s), in BibTeX name format.                                                       |
+---------------+----------------------------------------------------------------------------------------------------+
| howpublished  | How something strange has been published.                                                          |
+---------------+----------------------------------------------------------------------------------------------------+
| institution   | Institutuion sponsoring a technical report.                                                        |
+---------------+----------------------------------------------------------------------------------------------------+
| journal       | Journal name. Abbrevations are provided for many journals.                                         |
+---------------+----------------------------------------------------------------------------------------------------+
| key           | Used for alphabetizing, cross-referencing, and creating a label when the *author* is missing.      |
+---------------+----------------------------------------------------------------------------------------------------+
| keywords      | Keywords                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+
| month         | The month in which the work was published or, for an unpublished work, in which it was written.    |
+---------------+----------------------------------------------------------------------------------------------------+
| note          | Any additional information that can help the reader.                                               |
+---------------+----------------------------------------------------------------------------------------------------+
| number        | The number (issue) of a journal, magazine, technical report, or work in a series.                  |
+---------------+----------------------------------------------------------------------------------------------------+
| organization  | The organization that sponsors a conference or that publishes a manual.                            |
+---------------+----------------------------------------------------------------------------------------------------+
| pages         | One or more page numbers or range of numbers.                                                      |
+---------------+----------------------------------------------------------------------------------------------------+
| publisher     | The publisher's name.                                                                              |
+---------------+----------------------------------------------------------------------------------------------------+
| school        | The name of the school where the thesis was written.                                               |
+---------------+----------------------------------------------------------------------------------------------------+
| series        | The name of a series or set of books.                                                              |
+---------------+----------------------------------------------------------------------------------------------------+
| title         | The work's title.                                                                                  |
+---------------+----------------------------------------------------------------------------------------------------+
| type          | The type of a technical report(e.g., "Research Note").                                             |
+---------------+----------------------------------------------------------------------------------------------------+
| url           | URL of the publication document.                                                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| volume        | The volume of a journal or multivolume book.                                                       |
+---------------+----------------------------------------------------------------------------------------------------+
| year          | The year of publication or, for an unpublished work, the year it was written.                      |
+---------------+----------------------------------------------------------------------------------------------------+


.. _authorForm:

BibTeX name format
------------------

To ensure that BibTeX it self, as well as this library (e.g. :attr:`.Entry.authors`) handle the contents of
the *author* tag properly, this has to be in a proper format.

A *valid* BibTeX name format is:  *"John Doe and ..."* or *"Doe, John and ..."*.

.. note:: Unfortunately even official sources, like e.g. publishers's web sites, often provide BibTeX citations
            to download, which didn't fulfill this format, so be careful.


Footnotes & References
----------------------

.. [#f1] taken from http://bib-it.sourceforge.net/help/fieldsAndEntryTypes.php


.. _International DOI Foundation: https://www.doi.org
.. _isbnlib: https://pypi.python.org/pypi/isbnlib