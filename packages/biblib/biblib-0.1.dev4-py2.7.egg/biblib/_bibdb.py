# -*- coding: utf-8 -*-
"""
ThisThis module contains the BibTeX database class.

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__  = filter(str.isdigit, "$Revision: 127 $")


import string
import sys

# import of internal package modules
from . import _entry


class BibDB(object):
    """
    This is the BibTeX database main class.

    Optional a database can be initially populate by a list of Entry objects.

    :param ListOfEntryObj: list of BibTeX Entry object (:class:`.Article` | :class:`.Book` | ...)
    :type ListOfEntryObj: .BibDB.data
    :param method: keyword for merging method (see :meth:`.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    :raises TypeError: if an *EntryObj* is not of a valid object type
    :raises KeyError: if there is trouble with a citation-key of an *EntryObj*
    """


    # generate lists for counters used in proposeCKey()
    _clist = {
            'alpha' : string.ascii_lowercase,
            'Alpha' : string.ascii_uppercase,
            'num' : xrange(0, sys.maxint)
        }


    def __init__(self, ListOfEntryObj=None, method=None):

        #: Template for a citation-key, based on the tag names within an Entry.
        #: By default: ``{family}{year}``, here *family* refers to the first author family name.
        self.ckey_tpl = '{family}{year}'

        #: Template for a citation-key with a counter.
        #: By default: ``{family}{year}{cnt}``, here *cnt* will be replaced with the choosen counter (:attr:`.ckey_tpl_cnt`).
        self.ckey_tpl_wc = '{family}{year}{cnt}'

        #: Counter style for the citation-key template: ``alpha`` (*default* a,b,..,z), ``Alpha`` (A,B,..,Z) or ``num`` (1,2,3,...).
        self.ckey_tpl_cnt ='alpha'

        # initiate variables
        self._data = {}

        # initially populate database
        if ListOfEntryObj:
            for EntryObj in ListOfEntryObj:
                self.add_entry(EntryObj, method=method)


    def __iter__(self):
        return iter(self._data)


    def keys(self):
        """
        Returns a list of citation-keys defined in the database.

        :return: list of citation-keys
        :rtype: list
        """
        return self._data.keys()


    def values(self):
        """
        Returns a list of entry objects stored in the database.

        :return: list of entry objects
        :rtype: list
        """
        return self._data.values()


    def items(self):
        """
        Returns a list of sets containing citation-key/entry object.

        :return: list of sets citation-key/entry object
        :rtype: list
        """
        return self._data.items()


    def get_entry(self, ckey):
        """
        Returns the Entry object with the given citation-key in the database.

        :param ckey: citation-key
        :type ckey: str
        :return: BibTeX Entry object
        :rtype: :class:`.Article` | :class:`.Book` | ...
        :raises NameError: if citation-key did not exist in database
        """
        return self[ckey]
        # if not self._data.has_key(ckey):
        #     msg = 'Citation-key "' + ckey + '" did not exists in database!'
        #     raise NameError(msg)
        # return  self._data[ckey]


    def __getitem__(self, key):
        """
        Returns the Entry object with the given citation-key in the database.

        :param key: citation-key
        :type key: str
        :return: BibTeX Entry object
        :rtype: :class:`.Article` | :class:`.Book` | ...
        :raises NameError: if citation-key did not exist in database
        """
        if not self._data.has_key(key):
            msg = 'Citation-key "' + key + '" did not exists in database!'
            raise NameError(msg)
        return  self._data[key]


    def add_entry(self, entryObj, ckey=None, method=None):
        """
        Adds an Entry object to the database using *ckey* or :attr:`.Entry.ckey` of *entryObj* as
        citation-key. The method argument will overwrite an existing object attribute.
        There are different methods available how to handle the citation-key.
        If *method* is:

        * ``None``: (default) an invalid or conflicting citation-key will raise a KeyError.
        * ``'lazy'``: Try to use :attr:`.Entry.ckey` of *entryObj* or *ckey* as citation-key. If the it is already in use or invalid, generate a new using :py:meth:`.proposeCKey`.
        * ``'auto'``: Always use :py:meth:`.proposeCKey` to generate a proper citation-key.
        * ``'force'``: Use :attr:`.Entry.ckey` of *entryObj* or *ckey*  as citation-key. If the it is already in used, the old Entry object will be replaced. If it is invalid, generate a new using :py:meth:`.proposeCKey`.

        :param entryObj: BibTeX Entry object
        :type entryObj: :class:`.Article` | :class:`.Book` | ...
        :param ckey: citation-key
        :type ckey: str
        :param method: keyword for adding method (see above)
        :type method: str
        :return: citation-key as used for the database
        :rtype: str
        :raises TypeError: if entryObj is not of a valid object type
        :raises KeyError: if there is trouble with a citation-key
        :raises NameError: if argument for *method* is invalid
        """
        # check if it is a valid object type
        if not isinstance(entryObj, _entry.Entry):
            msg = 'entryObj is of wrong type!'
            raise TypeError(msg)

        if not ckey:
            ckey = entryObj.ckey

        if not method:
            if not ckey or self._data.has_key(ckey):
                msg = 'Citation-key already exists in database or is invalid!'
                raise KeyError(msg)
            else:
                self._data[ckey]= entryObj
                return ckey

        elif method == 'lazy':
            if not ckey or self._data.has_key(ckey):
                ckey = self.proposeCKey(entryObj)
            self._data[ckey]= entryObj
            return ckey

        elif method == 'auto':
            ckey = self.proposeCKey(entryObj)
            self._data[ckey]= entryObj
            return ckey

        elif method == 'force':
            if not ckey:
                ckey = self.proposeCKey(entryObj)
                self._data[ckey]= entryObj
            else:
                self._data[ckey]= entryObj
                return ckey

        else:
            msg='Invalid value for "method" argument!'
            raise NameError(msg)


    def __setitem__(self, key, value):
        self.add_entry(value, key)


    def del_entry(self, ckey):
        """
        Deletes the Entry object with a given BibTeX citation-key.

        :param ckey: citation-key
        :type ckey: str
        :raises NameError: if citation-key did not exist in database
        """
        del self[ckey]


    def __delitem__(self, key):
        """
        Deletes the Entry object with a given BibTeX citation-key.

        :param key: citation-key
        :type key: str
        :raises NameError: if citation-key did not exist in database
        """
        if key not in self.keys():
            msg = 'Citation-key "' + key + '" did not exist in database!'
            raise NameError(msg)
        del self._data[key]


    def mod_entry_type(self, ckey, newtype):
        """
        Modifies the BibTeX Entry type for a given citation-key.

        :param ckey: citation-key
        :type ckey: str
        :param newtype: new Entry type
        :type newtype: str
        :raises NameError: if citation-key did not exist in database or *newtype* is invalid
        """
        if ckey not in self.keys():
            msg = 'ID "' + ckey + '" did not exist in database!'
            raise NameError(msg)
        if newtype not in _entry.Entry._registeredTypes:
            msg = '"' +newtype + '" is not a valid Entry type!'
            raise NameError(msg)
        edict = self._data[ckey].datadict
        edict['ENTRYTYPE'] = newtype
        neobj = _entry.Entry.get_Instance(edict)
        self.add_entry(neobj, ckey=ckey, method='force')


    def update_ckey(self, old, new):
        """
        Updates the BibTeX citation-key of an Entry object in the database.

        .. note:: The citation-key stored in the respective Entry object (:attr:`.Entry.ckey`) will left unchanged!

        :param old: old citation-key
        :param new: new citation-key
        :type old: str
        :type new: str
        :raises NameError: if one of the citation-keys are invalid
        """
        if old not in self.keys():
            msg = 'Citation-key "' + old + '" not found!'
            raise NameError(msg)
        if new in self.keys():
            msg = 'New citation-key "' + new + '" alreday occupied!'
            raise NameError(msg)
        self._data[new] = self._data.pop(old)


    def proposeCKey(self, entryObj):
        """
        Proposes a BibTeX citation-key for a given Entry object.

        Based on the tag names and their contents within the Entry object and with the
        template strings (:attr:`.ckey_tpl`, :attr:`.ckey_tpl_wc`), the method will
        return a citation-key which suits the database.

        :param entryObj: BibTeX Entry object
        :type entryObj: :class:`.Article` | :class:`.Book` | ...
        :return: proposed citation-key
        :rtype: str
        :raises TypeError: if *entryObj* is not of a valid object type
        :raises KeyError: if a tag is used in :attr:`.ckey_tpl` or :attr:`.ckey_tpl_wc` which is not defined
        :raises ValueError: if :attr:`.ckey_tpl` or :attr:`.ckey_tpl_wc` string is erroneous.
        :raises IndexError: if the counter runs out of elements.
        """

        # check if it is a valid object type
        if not isinstance(entryObj, _entry.Entry):
            msg = 'entryObj is of wrong type!'
            raise TypeError(msg)

        # construct dictionary to replace keywords
        dataDict = entryObj.datadict.copy()
        if not entryObj.authors:
            dataDict.update( dict(given=u'Jon', family=u'Dow') )
        else:
            dataDict.update( entryObj.authors[0] )
        dataDict['cnt'] = ''
        counterSymbols = BibDB._clist[self.ckey_tpl_cnt]

        # patch for problem:
        # UnicodeEncodeError: 'ascii' codec can't encode character ...
        for key, value in dataDict.items():
            dataDict[key] = value.encode('us-ascii','replace')

        # generate citation-key without counter
        ckey = self.ckey_tpl.format(**dataDict)

        # while citation-key is already in use ...
        pos = 0
        while ckey in self.keys():
            # and generat citation-key with counter
            dataDict['cnt'] = counterSymbols[pos]
            ckey = self.ckey_tpl_wc.format(**dataDict)
            pos += 1

        return ckey


    def merge_bibdb(self, dbObj, method=None):
        """
        Merges the Entry objects of another database object.
        There are different methods available how to handle the citation-key.
        It returns a dictionary where the keys refer to the original citation-key
        of an Entry object and the value to the new one used in the database.

        :param dbObj: BibTeX database object
        :type dbObj: .BibDB
        :param method: keyword for merging method (see :meth:`.add_entry`)
        :type method: str
        :return: dictionary mapping old to new citation-key
        :rtype: dict
        :raises TypeError: if dbObj is not a valid BibTeX database object
        :raises KeyError: if there is trouble with a citation-key
        :raises NameError: if argument for *method* is invalid
        """

        # check if it is a valid object type
        if not isinstance(dbObj, BibDB):
            msg = "dbObj have to be a BibTeX database object"
            raise TypeError(msg)

        # add each Entry object to the database
        out = {}
        for ckey, eObj in dbObj.items():
            out[ckey] = self.add_entry(eObj, ckey=ckey, method=method)

        return out


    def bibtex(self):
        """
        Returns the BibTeX formatted string of data base.

        .. deprecated:: 0.1.dev1-r67
            Use function :func:`.db_to_string` instead.

        :return: BibTeX formatted string
        :rtype: str
        """
        out=''
        for ckey, entryObj in self.items():
            out += entryObj.bibtex(ckey = ckey)
        return out


    def has_ckey(self, ckey):
        """
        Test if a citation-key is defined within the database.

         .. deprecated:: 0.1.dev4
            Use ``ckey in dbOject`` instead.

        :param ckey: citation-key
        :type ckey: str
        :return: True | False
        :rtype: bool
        """
        return ckey in self._data


    def __contains__(self, key):
        return key in self._data


    def has_doi(self, doi):
        """
        Test if a DOI is defined within the database.

        :param doi: digital object identifier
        :type doi: str
        :return: True | False
        :rtype: bool
        """
        return doi in self.dois


    def __hash__(self):
        """
        Support for hash()

        :return: hash value
        """
        hashDict= {}
        for ckey, eObj in self.datadict.items():
            hashDict[ckey] = hash(eObj)
        return hash(frozenset(hashDict.items()))


    def __len__(self):
        return len(self._data)


    def __eq__(self, other):
        return hash(self) == hash(other)


    def __ne__(self, other):
        return hash(self) != hash(other)


    @property
    def datadict(self):
        """
        A dictionary containing the citation-keys as keys and the BibTeX Entry objects
        (:class:`.Article` | :class:`.Book` | ...) as values.
        """
        return self._data


    @property
    def data(self):
        """
        A list containing the BibTeX objects (:class:`.Article` | :class:`.Book` | ...) of the database.

        .. deprecated:: 0.1.dev4
            Use :meth:`.BibDB.values` instead.

        """
        return self._data.values()


    @property
    def ckeys(self):
        """
        A list of the BibTeX citation-keys of the database.

        .. deprecated:: 0.1.dev4
            Use :meth:`.BibDB.keys` instead.

        """
        return self._data.keys()


    @property
    def dois(self):
        """
        Returns a dictionary with *doi* as key and citation-key as value.
        """
        out = {}
        for ckey, eObj in self.items():
            doi = eObj.get_tag('doi')
            if doi:
                out[doi] = ckey
        return out
        #return { entryObj.get_tag('doi'): ckey for ckey, entryObj in self._data if entryObj.get_tag('doi') }


