#!/usr/bin/env python
# -*- coding: utf-8 -*-

import biblib
import biblib.dev

f = 'example_bib/my.bib'
#f = 'example_bib/small.bib'

dois = ['10.1209/0295-5075/109/68001', '10.1021/jp403862x']
isbn =['3499625334','978-0486647418']

db = biblib.db_from_file(f, decode=True)
#db = biblib.db_from_doiList(dois,decode=True)
#db = biblib.db_from_isbnList(isbn, decode=True)


entrObj = db.get_entry('EPL-2015')

print entrObj.get_tag('journal')

entrObj.set_tag('journal','EPL')

print db.bibtex()

print '-----------------------'

print db['EPL-2015'].bibtex()