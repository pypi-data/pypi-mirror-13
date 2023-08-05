#!/usr/bin/env python

import biblib
import biblib.dev

entry_string = ur'@Article{EPL-2015, ' \
               ur'Title = {Dense brushes of stiff polymers or filaments in fluid flow}, ' \
               ur'Author = {F. R\"omer and D. A. Fedosov}, Journal = {EPL (Europhysics Letters)}, ' \
               ur'Year = {2015}, Number = {6}, Pages = {68001--68009}, Volume = {109},' \
               ur'Doi = {10.1209/0295-5075/109/68001}, Owner = {frank}, Timestamp = {2015.03.17}, ' \
               ur'Url = {http://wgserve.de/fr/wp-content/papercite-data/pdf/EPL_109_68001_(2015).pdf} }'

res = biblib.dev.parse_data(entry_string)

print res