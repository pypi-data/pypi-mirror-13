#!/usr/bin/env python

import biblib
import biblib.dev

f = 'example_bib/my.bib'


db = biblib.db_from_file(f)

tst = db.data[0].datadict['author']

print tst

ctst = biblib.dev.string_to_latex(tst)

print ctst