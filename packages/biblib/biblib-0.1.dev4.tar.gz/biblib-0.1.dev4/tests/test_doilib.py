#!/usr/bin/env python

import sys

import biblib
import biblib.dev

dois = ['10.1209/0295-5075/109/68001', '10.1039/C5CP04949K', '10.1063/1.4934017' ]

# for doi in dois:
#     print '--------------------------------------------'
#     res = biblib.doilib.get_bibtex(doi)
#     print res

try:
    res = biblib.dev.doi2bibtex('10.1007/BF01341258')

except biblib.dev.DOIError as e:
    print e.msg

except:
    print "Unexpected error:", sys.exc_info()

else:
    print res