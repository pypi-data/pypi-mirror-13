#!/usr/bin/env python

import biblib
#f='example_bib/one.bib'
f='example_bib/small.bib'


db = biblib.db_from_file(f)

print len(db.data)

print db.ckeys

# print db.data[0].datadict

entryDict = {'ID': 'xxxIDxxx', 'ENTRYTYPE':'article','year':'2001','author':'Lacomme , Philippe and Prins , Christian'}


print '-----------------------------------------'

for i in range(0,3):
    print i
    eobj = biblib._entry.Entry.get_Instance(entryDict)
    db.add_entry(eobj, method='auto')
    print db.ckeys
