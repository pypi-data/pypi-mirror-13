#!/usr/bin/env python

import biblib

f = 'example_bib/my.bib'


dbObj = biblib.db_from_file(f)

print dbObj.datadict

# A list containing the BibTeX objects of the database.
print dbObj.data

# A list of the BibTeX citation-keys of the database.
print dbObj.ckeys

# Returns a dictionary with doi as key and citation-key as value.
print dbObj.dois

print '----------------------------------'

print dbObj.has_ckey('EPL-2015')
print dbObj.has_doi('10.1209/0295-5075/109/68001')

print '----------------------------------'

# Lets retrieve the JCP article...
entryObj = dbObj.get_entry('JCP-127-234509')

# and for eyample. print the *journal* tag:
print entryObj.get_tag('journal')

print '----------------------------------'


# First we setup a dictionary containing the initial data, ..
inputdict = {'ENTRYTYPE': 'mastersthesis', 'ID': 'Mayer2008',
             'author': u'Hans H. Mayer',
             'title': u'A very interesting thesis.',
             'school': u'University of Nowhere',
             'year': u'2008',}

# and than create the entry object.
newEntry = biblib.Entry.get_Instance(inputdict)

# Now we can add the new entry to the database:
dbObj.add_entry(newEntry)

# lets look if it worked ;)
print dbObj.ckeys


print '----------------------------------'

dbObj.del_entry('EPL-2015')
print dbObj.datadict


print '----------------------------------'

# lets promote H. H. Mayer to PhD ;) ,...
dbObj.mod_entry_type('Mayer2008','phdthesis')

# and change the citation-key of the JCP article.
dbObj.update_ckey('JCP-127-234509','Roemer2007')

# This we get..
print dbObj.datadict

print '----------------------------------'

# Lets retrieve the PhD thesis...
entryObj = dbObj.get_entry('Mayer2008')

# The BibTeX entry type of the entry object.
print entryObj.BibTeXType

# BibTeX tag names and contents of the entry object as key-value pairs in a dictionary.
print entryObj.datadict

# The initial BibTeX citation-key of the entry object.
print entryObj.ckey

# A list of dictionaries for the author(s).
print entryObj.authors

print '----------------------------------'

# As you remember, we have changed the citation-key of the JCP article above,
# but when we call the object property, we get...
print dbObj.get_entry('Roemer2007').ckey


print '----------------------------------'

# Here we retrieve the 'title' tag:
print entryObj.get_tag('title')

# If we request a non defined tag, we get a 'None' instead of a KeyError:
print entryObj.get_tag('doi')

# Lets update the 'title' tag, ...
entryObj.set_tag('title',u'Mayers PhD thesis')
# and delete the 'school' tag.
entryObj.del_tag('school')
print entryObj.datadict

print '----------------------------------'

# The 'Phdthesis' type has the following mandatory fields:
print entryObj.mandatoryTags

# Because we have deleteted the 'school' tag recently, the entry object is incomplete:
print entryObj.is_complete

print entryObj.missingTags

# If we now reset the 'school' tag:
entryObj.set_tag('school','University of Elsewhere')
print entryObj.is_complete

print '----------------------------------'

# We have a DOI, like
doi = '10.1088/0959-5309/43/5/301'
# and retrieve now a new entry object ...
doiEntry = biblib.entry_from_doi(doi)
# we've got..
print biblib.entry_to_string(doiEntry)

print '----------------------------------'

# We have a ISBN
isbn = '978-0486647418'
# and retrieve now a new entry object ...
isbnEntry = biblib.entry_from_isbn(isbn)
# we've got..
print biblib.entry_to_string(isbnEntry)

print '----------------------------------'