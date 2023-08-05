#!/usr/bin/env python

import biblib

f = 'example_bib/new.bib'

#-------------------------------------------------------------

# with BibTexFileStorage(f) as BTFS:
#     entryObject = biblib.entry_from_doi('10.1021/jp403862x')
#     ckey = BTFS.add_entry(entryObject)
#
#     print ckey
#     print BTFS.has_changed()

#-------------------------------------------------------------

BTFS = biblib.BibTexFile(f)

entryObject = biblib.entry_from_doi('10.1021/jp403862x')
ckey = BTFS.add_entry(entryObject, method='auto')
print ckey
print BTFS.has_changed()
print BTFS.fileEncoding
BTFS.close()


#-------------------------------------------------------------

# f = 'example_bib/new.bib'
#
# BTFS = BibTexFileStorage(f)
#
# entryObject = biblib.entry_from_doi('10.1021/jp403862x')
#
# ckey = BTFS.add_entry(entryObject)
#
# print ckey
# print BTFS.has_changed()
#
# BTFS.save()
#
# entryObject = biblib.entry_from_isbn('3499625334')
#
# ckey = BTFS.add_entry(entryObject)
#
# print ckey
# print BTFS.has_changed()
#
# BTFS.save()