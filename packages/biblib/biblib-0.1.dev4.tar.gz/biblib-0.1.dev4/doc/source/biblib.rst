biblib package API
==================

In the namespace ``biblib`` you have access to the core functions (:ref:`reader <api-reader>`,
:ref:`writer <api-writer>`) and classes (:ref:`database <api-db>`, :ref:`entry <api-entry>`).
You can extend the lib by using the classes and functions exposed in namespace ``biblib.dev``,
which are decribed :ref:`here <api-dev>`.


.. _api-entry:

Entry class
-----------

The :py:class:`.Entry` class is the generic class of an entry from which the classes
for the different BibTeX entry *types* (like :class:`.Article`, :class:`.Book`, etc.) are derived.
A list of the :ref:`implemented types <entryTypes>` is appended to the tutorial.

A BibTeX entry is of a certain type, which reflects in the object type, and might have a citation-key.
The various characteristic of a specific BibTeX entry is defined by a number of tags.
A tag is a key-value pair, the tag name and its contents.
The allowed tag names are defined in :attr:`.Entry.processedTags`, and a list is given :ref:`here <entryTags>`.

To create an entry object, we recommend to use the classmethod :meth:`.Entry.get_Instance`.
It will return an entry object of proper type, depending on the dictionary committed.

.. code-block:: py

	>>> # First we setup a dictionary containing the initial data, ..
	>>> inputdict = {'ENTRYTYPE': 'mastersthesis', 'ID': 'Mayer2008',
				 'author': u'Hans. H. Mayer',
				 'school': u'University of Nowhere'
				 'title': u'A very interesting thesis.',
				 'year': u'2008'}

	>>> # and than create the entry object.
	>>> entryObject = biblib.Entry.get_Instance(inputdict)
	>>> print entryObject
	<biblib._entry.Mastersthesis object at 0x7f25456d6810>

The entry object is designed to behave similar to a python dictionary, which seems likely because of its
key-value structure regarding the tags.
Therefore the standard operators (get-,set-, delitem) are implemented.
To manipulate the tags of an entry, one can either use the class methods
(:meth:`.Entry.get_tag`, :meth:`.Entry.set_tag` and :meth:`.Entry.del_tag`) or the standard operators,
like:

.. code-block:: py

    >>> tag_contents = entryObject['tag name']
    >>> entryObject['tag name'] = u'tag contents'
    >>> del entryObject['tag name']

Like a dictionary it supports the methods *keys()*, *values()*, and *items()*.
Furthermore it is iterable, like:

.. code-block:: py

    >>> for tag_name, tag_contents in entryObject.items():
    >>>     ...

It also supports the built-in function `hash()`_ and comparison operator: ``==``, ``!=``.

.. note:: Because the hash value represents the *contents*, an entry object
          should not been used as a key in hashable collections!

To check if a tag is defined, one can simply:

.. code-block:: py

    >>> if tag_name in entryObject:
    >>>     ...

Some tags are mandatory for certain types of BibTeX entries (*e.g.* :attr:`.Article.mandatoryTags`), some are optional.
The property :attr:`.Entry.is_complete` can be used to check if a mandatory tag is missed, and the property
:attr:`.Entry.missingTags` which tag is missed.


-------------------------------------------------------------------------------

.. autoclass:: biblib.Entry
	:members:

-------------------------------------------------------------------------------

As examples for a class specified for an entry type, we show here the :class:`.Article` and :class:`.Book` class.

.. autoclass:: biblib.Article
	:members:

.. autoclass:: biblib.Book
	:members:


.. _api-db:

Database class
--------------

The :class:`.BibDB` class provides methods to store and manage BibTeX entry objects,
like :class:`.Article`, :class:`.Book`, etc..

Like the entry object, it is designed to behave similar to s python dictionary.
The citation-key and the respective entry object are the key-value pair.
To manipulate database entries, one can either use the class methods
(:meth:`.BibDB.get_entry`, :meth:`.BibDB.add_entry` and :meth:`.BibDB.del_entry`) or the standard operators,
like:

.. code-block:: py

    >>> entryObject = dbObject['citation-key']
    >>> dbObject['citation-key'] = entryObject
    >>> del dbObject['citation-key']

.. note:: The method :meth:`.BibDB.add_entry` offers more flexibility regarding the citation-key than the set-operator!

Like a dictionary it supports the methods *keys()*, *values()*, and *items()*.
Furthermore it is iterable, like:

.. code-block:: py

    >>> for citation_key, entryObject in dbObject.items():
    >>>     ...

It also supports the built-in function `hash()`_ and comparison operator: ``==``, ``!=``.

.. note:: Because the hash value represents the *contents*, an database object
          should not been used as a key in hashable collections!

To check if a citation-key is defined, one can simply:

.. code-block:: py

    >>> if citation_key in dbObject:
    >>>     ...

The built-in function `len()`_ returns the number of entries stored in the database.

-------------------------------------------------------------------------------

.. autoclass:: biblib.BibDB
	:members:


.. _api-reader:

Reader functions
----------------

This functions are to read BibTeX bibliographic data to a :class:`.Entry` or :class:`.BibDB` object.

One can read either a BibTeX **string** or **file**.
Additionally one can try to catch citation data by a *Digital Object Identifier* (**DOI**) or
*International Standard Book Number* (**ISBN**) via webservice.
To resolve DOIs a request to `doi.org`_ will be made.
The python library `isbnlib`_ is utilized to fetch meta data from *worldcat.org* and/or *Google Books* service.

.. note:: By default, LaTeX codes for non-ascii character will be *decode* to a unicode character.

.. autofunction:: biblib.db_from_string

.. autofunction:: biblib.db_from_file

.. autofunction:: biblib.db_from_doiList

.. autofunction:: biblib.db_from_isbnList

.. autofunction:: biblib.entry_from_doi

.. autofunction:: biblib.entry_from_isbn


.. _api-writer:

Writer functions
----------------

This module contains the function to write BibTeX database objects to a file or the screen.

`BibTeX`_ itself is an ASCII-only program! Therefore ``encode=True`` *by default* to write out ASCII files.
If you intend to use an alternative which allows to use UTF8, you can set ``encode=False`` to write out UTF8 files.


.. autofunction:: biblib.db_to_string

.. autofunction:: biblib.db_to_file

.. autofunction:: biblib.entry_to_string



.. _api-dev:

dev module
----------

To access this functions you need to extend the lib by importing ``biblib.dev``.

.. autofunction:: biblib.dev.parse_data

.. autofunction:: biblib.dev.latex_to_string

.. autofunction:: biblib.dev.string_to_latex

.. autofunction:: biblib.dev.doi2bibtex

.. autofunction:: biblib.dev.isbn2bibtex

.. autoclass:: biblib.dev.DOIError
	:members:



experimental
------------

.. autoclass:: biblib.BibTexFile
	:members:

-------------------------------------------------------------------------------

.. autoclass:: biblib.BibTexFileSet
	:members:



.. _doi.org: https://www.doi.org
.. _isbnlib: https://pypi.python.org/pypi/isbnlib
.. _hash(): https://docs.python.org/3/library/functions.html#hash
.. _len(): https://docs.python.org/3/library/functions.html#len
.. _BibTeX: https://www.ctan.org/pkg/bibtex



