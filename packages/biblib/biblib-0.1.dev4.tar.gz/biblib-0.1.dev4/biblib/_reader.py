# -*- coding: utf-8 -*-
"""
This module contains the functions to read BibTeX entries to a entry or database object.

.. note:: By default LaTeX codes will be *decode* to a unicode character.

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__  = filter(str.isdigit, "$Revision: 111 $")


# import external package modules
import magic

# import of internal package modules
from ._entry import Entry
from ._bibdb import BibDB
from .dev._parser import parse_data
from .dev._latexenc import latex_to_string
from .dev._doilib import (doi2bibtex, _doi_to_inputdict)
from .dev._isbnlib import _isbn_to_inputdict


def db_from_string(bibStr, decode=True, method=None):
    """
    Function parsing a BibTeX bibStr containing one or more entries
    and returns a BibTeX database object.

    :param bibStr: input BibTeX string
    :type bibStr: unicode
    :param decode: LaTeX codes to unicode character
    :type decode: bool
    :param method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    """

    # decode LaTeX code to unicode characters
    if decode:
        bibStr = latex_to_string(bibStr)

    # parses a bibStr
    listOfDicts = parse_data(bibStr)

    if listOfDicts:
        return _db_from_listOfDicts(listOfDicts, method=method)
    else:
        return None


def db_from_file(filename, decode=True, method=None):
    """
    Function parsing a BibTeX file containing one or more entries
    and returns a BibTeX database object.

    :param filename: input BibTeX file
    :type filename: str
    :param decode: LaTeX codes to unicode character
    :type decode: bool
    :param method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    """
    # determine the encoding of the file
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_file(filename)

    # read the file to a string
    dataStr = open(filename, 'r').read().decode(encoding)

    return db_from_string(dataStr, decode=decode, method=method)


def db_from_doiList(doiList, decode=True, method=None):
    """
    Function to retrieve BibTeX citation entries by their DOI
    and returns a BibTeX database object.

    :param doiList: list of DOIs as strings
    :type doiList: list
    :param decode: LaTeX codes to unicode character
    :type decode: bool
    :param method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    """
    dataStr = u''
    for DOI in doiList:
        dataStr += doi2bibtex(DOI) + "\n"

    return db_from_string(dataStr, decode=decode, method=method)


def db_from_isbnList(isbnList, method=None):
    """
    Function to retrieve BibTeX citation entries by their ISBN
    and returns a BibTeX database object.

    :param isbnList: list of ISBN numbers as strings
    :type isbnList: list
    :param method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    """
    listOfDicts = []
    for isbn in isbnList:
        inputdict = _isbn_to_inputdict(isbn)
        if inputdict:
            listOfDicts.append(inputdict)
    if listOfDicts:
        return _db_from_listOfDicts(listOfDicts, method=method)
    else:
        return None


def entry_from_doi(doi, decode=True):
    """
    Creates an entry object by DOI.

    :param doi: DOI ss string
    :type doi: str
    :param decode: LaTeX codes to unicode character
    :type decode: bool
    :return: BibTeX entry object
    :rtype: :class:`.Article` | :class:`.Book` | ...
    """
    inputdict = _doi_to_inputdict(doi, decode=decode)
    if inputdict:
        return Entry.get_Instance(inputdict)
    else:
        return None


def entry_from_isbn(isbn):
    """
    Creates an entry object by ISBN.

    :param isbn: ISBN ss string
    :type isbn: str
    :return: BibTeX entry object
    :rtype: .Book
    """
    inputdict = _isbn_to_inputdict(isbn)
    if inputdict:
        return Entry.get_Instance(inputdict)
    else:
        return None


def _db_from_listOfDicts(listOfDicts, method=None):
    """
    Creates a database from a list of inputdicts.

    :param listOfDicts: list of inputdicts
    :param method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :type method: str
    :return:  BibTeX database object
    :rtype: .BibDB
    """
    listOfEntryObj=[]
    for entryDict in listOfDicts:
        entryObj = Entry.get_Instance(entryDict)
        listOfEntryObj.append(entryObj)

    return BibDB(listOfEntryObj, method=method)
