Introduction
============

**biblib** is a (pure) python library that provides several useful classes, methods and functions to work with
BibTeX bibliographic data within your python scripts.

The idea is to enabling you to prepare *your own tools*, which are specifically tailored to *your own literature investigation scheme*, comfortably.


Nomenclature
------------

We stay here with the naming convention as used on `bibtex.org`_.
The different types of bibliographic resources (like e.g. *article* or *book*) are called **Entry Types**.
The reffernce string, which is used to cite a resource like ``\cite{citation-key}``,
is called **citation-key** (aka *Bibtexkey*).
And the various properties an entry can possess, are called **Tags** (aka *Fields* or *Field Types*).

Here an example of a BibTeX entry::

	@EntryType{citation-key,
	  TagName = {TagContents},
	  ...
	}


Concept
-------

The basic (original) usage concept is shown in *Fig. 1*.
One uses :ref:`reader <api-reader>` function, to gain a :ref:`BibTeX entry <api-entry>` object
or a :ref:`BibTeX database <api-db>` object.
Like in the :ref:`example <usage example>` below, the function :func:`biblib.db_from_file` reads a BibTeX file
and returns a database object (:class:`.BibDB`).
If one request the bibliographic metadata referring to a *DOI* by using the :func:`biblib.entry_from_doi`
function, an entry object (:class:`.Entry`) object will be returned.
Both object types can now be manipulated.


.. figure:: _static/biblib_concept.png

	**Fig. 1**: *Schematic sketch showing the basic usage concept for biblib.*


Naturally one can all properties (*tags*, aka *fields*) of an entry object.
An entry object can be retrieved from a database, as well as added to this.
And of course the database object offers the obvious set of methods to set, get, and delete entries.
Additionally, both objects (:class:`.BibDB`, :class:`.Entry`) offer methods which are of interest in the context of
bibliographic data, or in particular of BibTeX.

To *export* an entry or database object, one uses a :ref:`writer <api-writer>`) function.
In the :ref:`usage example <usage example>`, the :func:`biblib.db_to_file` function
is used to write the contents of a database object a BibTeX file.

.. _ext concept:

.. note:: An extension of this concept in terms of e.g. *FileStorage* objects,
        which allow you for example to work persistently on a BibTeX file, will follow.
        *(Thanks to* `Jackalope`_ *!)*


.. _usage example:

Usage example
-------------

Lets assume we have the following BibTeX sample file :file:`bibtex.bib`::

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


The following code will add a citation by their DOI:

.. code-block:: py

	import biblib

	# create database from BibTeX file
	dbObj = biblib.db_from_file('bibtex.bib')

	# retrieve bibliographic meta data by DOI
	entryObj = biblib.entry_from_doi('10.1088/0959-5309/43/5/301')

	# add new entry to database
	dbObj.add_entry(entryObj)

	# write database to a new BibTeX file
	biblib.db_to_file(dbObj,'new.bib')

Now, :file:`new.bib` looks like::

	% Encoding: UTF8

	@Article{Lennard_Jones_1931,
		Author = {J E Lennard-Jones},
		Doi = {10.1088/0959-5309/43/5/301},
		Journal = {Proc. Phys. Soc.},
		Month = {sep},
		Number = {5},
		Pages = {461-482},
		Publisher = {{IOP}Publishing},
		Title = {Cohesion},
		Url = {http://dx.doi.org/10.1088/0959-5309/43/5/301},
		Volume = {43},
		Year = {1931}
	}

	@Article{JCP-127-234509,
		Author = {F. Römer and T. Kraska},
		Doi = {10.1063/1.2805063},
		Journal = {Journal of Chemical Physics},
		Number = {23},
		Pages = {234509},
		Title = {Homogeneous nucleation and growth in supersaturated zinc vapor investigated by molecular dynamics simulation},
		Volume = {127},
		Year = {2007}
	}


Requirements
------------

* currently **only** Python 2
* `isbnlib`_ for retreving citation entries via ISBN number
* `python-magic`_ for detecting character encoding


Installation
------------

You can install the latest version from the `Python package index`_.
From the command line, enter (in some cases you have to precede the command with :command:`sudo`):


.. code-block:: bash

	$ pip install biblib --pre


.. note:: Because currently only a *development* version is available, you need to use the ``--pre`` option.

More information about the usage and how to get and install ``pip`` you find in the `PIP documentation`_.

To install it manual, `download`_ the archive, unpack it, and type
(in some cases you have to precede the command with :command:`sudo`):


.. code-block:: bash

	$ python setup.py install


Source
------

The complete source code *will soon be* available on `sourceforge`_.


Thanks
------

Thanks to `Jackalope`_ for his support while planing and designing *biblib*,
and for his :ref:`future contributions <ext concept>`.


Links
-----

* The official resource of `BibTeX at CTAN`_.
* The BibTeX documentation: `BibTeXing`_ by Oren Patashnik.
* `BibTeX at Wikipedia`_
* My favorite GUI tool to manage my bibliography is `JabRef`_.



.. _Python package index: https://pypi.python.org/pypi
.. _download: https://pypi.python.org/pypi/biblib
.. _isbnlib: https://pypi.python.org/pypi/isbnlib
.. _sourceforge: https://sourceforge.net/projects/pybiblib
.. _python-magic: https://pypi.python.org/pypi/python-magic
.. _PIP documentation: https://pip.pypa.io/en/stable/#
.. _Jackalope: http://www.jackalope.eu
.. _bibtex.org: http://www.bibtex.org
.. _BibTeX at CTAN: https://www.ctan.org/pkg/bibtex
.. _BibTeXing: http://ftp.fau.de/ctan/biblio/bibtex/base/btxdoc.pdf
.. _BibTeX at Wikipedia: https://en.wikipedia.org/wiki/BibTeX
.. _JabRef: http://www.jabref.org