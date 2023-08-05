#!/usr/bin/env python
# -*- coding: utf-8 -*-

import biblib

inputdict = {'ENTRYTYPE': 'article', 'ID': 'R_mer_2015',
         'doi': u'10.1209/0295-5075/109/68001',
        'author': u'Römer, Frank and Fedosov, Dimitry A.',
         'url': u'http://dx.doi.org/10.1209/0295-5075/109/68001',
         'journal': u'{ EPL }',
         'title': u'Dense brushes of stiff polymers or filaments in fluid flow',
         'number': u'6', 'month': u'mar', 'volume': u'109', 'year': u'2015',
         'Pages': u'68001'}

eobj = biblib.Entry.get_Instance(inputdict)

print type(eobj)
print '-----------------------'
print eobj.datadict
print '-----------------------'
print eobj.bibtex()
print '-----------------------'
print eobj.ckey
print '-----------------------'
print eobj.authors
print '-----------------------'

eobj2 = biblib.Entry.get_Instance(inputdict)
#del eobj['month']

if eobj != eobj2:
    print 'not-equal'
else:
    print 'equal'
