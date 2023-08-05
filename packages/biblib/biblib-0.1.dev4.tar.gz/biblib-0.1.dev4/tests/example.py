#!/usr/bin/env python

import biblib




class BibTexFileSet(object):


    def __init__(self):

        # initiate variables
        self._data = {}


    def __iter__(self):
        return iter(self._data)


    def keys(self):
        """
        Returns a list of alias defined in the set.

        :return: list of alias
        :rtype: list
        """
        return self._data.keys()


    def values(self):
        """
        Returns a list of BibTexFile object stored in the set.

        :return: list of BibTexFile object
        :rtype: list
        """
        return self._data.values()


    def items(self):
        """
        Returns a list of sets containing alias/ BibTexFile object.

        :return: list of sets alias/ BibTexFile object
        :rtype: list
        """
        return self._data.items()


    def __getitem__(self, key):
        """
        Returns the BibTexFile object with the given alias in the set.

        :param key: alias
        :type key: str
        :return: BibTeX file object
        :rtype: .BibTexFile
        :raises NameError: if alias did not exist in set
        """
        if not self._data.has_key(key):
            msg = 'Alias "' + key + '" did not exists in set!'
            raise NameError(msg)
        return  self._data[key]


    def __setitem__(self, key, value):
        """
        Add/set a BibTeX file object with an alias to the set.

        :param key: alias
        :type key: str
        :param value: BibTeX file object
        :type value: .BibTexFile
        :raises TypeError: if value is not of a valid object type
        :raises KeyError: if alias already exists in set
        """

        # check if it is a valid object type
        if not isinstance(value, biblib.BibTexFile):
            msg = 'Value (object) is of wrong type!'
            raise TypeError(msg)

        if key in self._data.keys():
            msg = 'Alias "' + key + '" already exists in set!'
            raise KeyError(msg)

        self._data[key] = value


    def __delitem__(self, key):
        """
        Deletes a BibTeX file object from the set.

        :param key: alias
        :type key: str
        :raises NameError: if citation-key did not exist in database
        """
        if key not in self._data.keys():
            msg = 'Alias "' + key + '" did not exists in set!'
            raise NameError(msg)
        del self._data[key]


    def add_file(self, filename, alias=None):
        btfileObj = biblib.BibTexFile(filename)
        if not alias:
            key = btfileObj.fileName
        else:
            key = alias
        self[key] = btfileObj


    def has_doi(self, doi):
        if doi in self.dois:
            return self.dois[doi]
        else:
            return False


    @property
    def dois(self):
        """
        Returns a dictionary with *doi* as key and [alias, citation-key] list as value.
        """
        out = {}
        for alias, btfileObj in self.items():
            for doi, ckey in btfileObj.dois.items():
                out[doi] = [alias, ckey]
        return out



#==============================================================================

f0 = 'example_bib/my.bib'
f1 = 'example_bib/new.bib'


BTFS = BibTexFileSet()

BTFS.add_file(f0)
BTFS.add_file(f1)

print BTFS.dois

f, c = BTFS.has_doi('10.1063/1.2805063')
print f, c

print BTFS['my.bib']['JCP-127-234509']['author']