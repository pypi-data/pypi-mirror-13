# -*- coding: utf-8 -*-
"""
This module contains the function to write BibTeX database objects to a file.

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__  = filter(str.isdigit, "$Revision: 126 $")


# import of internal package modules
from ._entry import *
from ._bibdb import BibDB
from .dev._latexenc import string_to_latex


def db_to_string(dbObj, encode=True):
    """
    Returns the BibTeX code of a database objects as a string.

    :param dbObj: BibTeX database
    :type dbObj: .BibDB
    :param encode:  unicode character to LaTeX codes
    :type encode: bool
    :return: BibTeX code
    :rtype: str
    :raises TypeError: if *dbObj* is not a valid database object
    """

    if not isinstance(dbObj, BibDB):
        raise TypeError('dbObj have to be a BibTeX database objec')
    out = ''
    for ckey, eObj in dbObj.datadict.items():
        out += entry_to_string(eObj, ckey=ckey, encode=encode)
    return out


def db_to_file(dbObj, file, encode=True):
    """
    Writes a database objects to a BibTeX *file*.

    :param dbObj: BibTeX database
    :type dbObj: .BibDB
    :param encode:  unicode character to LaTeX codes
    :type encode: bool
    :param file: output file name
    :type file: str
    :raises TypeError: if *dbObj* is not a valid database object
    """

    if encode:
        header = '% Encoding: ASCII\n\n'
        enc = 'us-ascii'
    else:
        header = "% Encoding: UTF8\n\n"
        enc = 'utf-8'

    out = db_to_string(dbObj, encode=encode)

    with open (file, 'w') as f:
        f.write(header.encode(enc))
        f.write(out.encode(enc))


def entry_to_string(entryObj, ckey=None, encode=True):
    """
    Returns the BibTeX code of an Entry objects as a string.
    If *ckey* is not defined, the object attribute :attr:`.Entry.ckey` will be used.

    :param entryObj: BibTeX Entry
    :type entryObj: :class:`.Article` | :class:`.Book` | ...
    :param ckey: citation-key
    :type ckey: str
    :param encode: unicode character to LaTeX codes
    :type encode: bool
    :return: BibTeX code
    :rtype: str
    :raises TypeError: if *entryObj* is not a valid Entry object
    """
    if not isinstance(entryObj, Entry):
        raise TypeError('entryObj is of wrong type!')
    dict = entryObj.datadict
    if ckey:
        dict['ID'] = ckey
    if encode:
        dict = _to_latex(dict)
    return _to_bibtex(dict)


def _to_bibtex(dict, ckey=None):
    """
    Returns the BibTeX Entry string.

    :param dict: dictionary containing tags and their contents
    :type dict: Entry.datadict
    :param ckey: citation-key
    :return: BibTeX Entry string
    :rtype: str
    """
    if not ckey:
        if dict.get('ID'):
            ckey = dict['ID']
        else:
            ckey = 'undefined'
    bibtex = ''
    # write BibTeX Entry type and citation-key
    bibtex += '@' + dict['ENTRYTYPE'].capitalize() + '{' + dict['ID']
    # write BibTeX tags
    for tag in [i for i in sorted(dict)]:
        if tag not in ['ENTRYTYPE', 'ID'] and tag in Entry.processedTags:
            bibtex += ",\n" + '	' + tag.capitalize() + " = {" + dict[tag] + "}"
    bibtex += "\n}\n\n"
    return bibtex


def _to_latex(dict):
    """
    Convert unicode character to LaTeX code.

    :param dict: BibTeX Entry dictionary
    :type dict: Entry.datadict
    :return: BibTeX Entry dictionary
    :rtype: Entry.datadict
    """
    for key, value in dict.items():
        if key not in Entry.protectedTags and key not in ['ENTRYTYPE','ID']:
            dict[key] = string_to_latex(value)
    return dict



