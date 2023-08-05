#!/usr/bin/env python

import argparse
import biblib, biblib.dev
import webbrowser


# parse command line arguments
parser = argparse.ArgumentParser(description='*** literature enquiry tool ***')
parser.add_argument('doiList', metavar='DOI', type=str, nargs='+',
                   help='a Digital Object Identifier')
parser.add_argument('--db', metavar='BibTeX file', action='append')
args = parser.parse_args()


def header(msg, lineChar="-"):
    print "\n  " + msg + "  \n" + lineChar*(len(msg)+4)

def mainheader(msg):
    header(msg, "=")

def subheader(msg):
    header(msg)


def add_to_db(entryObj):

    if len(BTFS) > 1:
        print '\n select DB:'
        for i in range(0, len(BTFS)):
            print str(i) + ') ' + BTFS.keys()[i]
        dbid=''
        while dbid not in range(0, len(BTFS)):
            dbid = int(raw_input('selection: '))
    else:
        dbid = 0

    alias = BTFS.keys()[dbid]
    prop_ckey = BTFS[alias].proposeCKey(entryObj)

    msg = 'Save in ' + alias + ' with citation key [' + prop_ckey + ']: '
    usr_ckey = raw_input(msg)
    if usr_ckey == '':
        ckey =  prop_ckey
    else:
        ckey = usr_ckey

    print '<- add entry to ' + alias + ' with citation-key ' + ckey
    BTFS[alias][ckey] = entryObj
    BTFS[alias].save()



# read BibTeX files ...
if args.db:
    mainheader('read BibTeX file(s):')
    BTFS = biblib.BibTexFileSet()
    for bibfile in args.db:
        print '* ' + bibfile + ' ...',
        alias = BTFS.add_file(bibfile)
        print 'done! [' + str(len(BTFS[alias])) + ']'

# process DOIs ...
for i in range(0,len(args.doiList)):

    doi = args.doiList[i]

    mainheader('process DOI ' + doi + ':')

    # check if DOI is already known...
    if BTFS.has_doi(doi):
        alias, ckey = BTFS.dois[doi]
        print '* DOI found: ' + alias + ' [' + ckey + '] !'

    # request meta data for DOI...
    print '* request doi.org ... ',
    try:
        entryObj = biblib.entry_from_doi(doi)
    except biblib.dev._doilib.DOIError as e:
        print e.msg
        continue
    print 'done!'
    print 'found..'
    print biblib.entry_to_string(entryObj)

    # Menu
    selection=''
    while not 'x' == selection:
        print '--------------------------------'
        print 'w) open journal   s) open SciHub'
        print 'a) add to DB'
        if i+1 < len(args.doiList):
            print 'x) next DOI'
        else:
            print 'x) exit'
        selection = raw_input('selection: ')
        if selection == 'w':
            url = entryObj.get_tag('url')
            if url:
                webbrowser.open_new(url)
        elif selection == 's':
            url = 'http://sci-hub.io/%s' % doi
            webbrowser.open_new(url)
        elif selection == 'a':
            add_to_db(entryObj)