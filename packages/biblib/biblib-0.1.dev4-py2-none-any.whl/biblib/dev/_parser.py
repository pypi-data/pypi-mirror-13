# -*- coding: utf-8 -*-
"""
This module contains the object class for BibTeX parsing.

-------------------------------------------------------------------------------
"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__  = filter(str.isdigit, "$Revision: 107 $")


# import external modules
import re


def _clear_comments(data):
    """
    Strips the comments and returns plain (BibTeX) data.

    :param data: input data
    :type data: st
    :return: plain data
    :rtype: str
    """
    res = re.sub(ur"(%.*\n)", '', data)
    res = re.sub(ur"(comment [^\n]*\n)", '', res)
    return res


def parse_data(data):
    """
    Function parsing a string of BibTeX data containing one or more entries
    and returns a list of dictionaries.

    .. warning:: If a citation-key is used twice, the last Entry will win!

    :param data: input BibTeX data
    :type data: str
    :return: list of dicts
    :rtype: list
    """

    bib = Parser(_clear_comments(data))
    bib.parse()
    return bib.records.values()


class Parser() :
    """Main class for BibTeX parsing

    This class is a modified version of Bibpy (yet another) BibTex file parser in python,
    published 2011 by Panagiotis Tigkas under the MIT licence.
    (https://github.com/ptigas/bibpy)

    :param data: plain BibTeX data
    :type data: str
    :return: BibTeX parser object
    :rtype: .parser.parser
    """

    def tokenize(self) :
        for item in self.token_re.finditer(self.data):
            i = item.group(0)
            if self.white.match(i) :
                if self.nl.match(i) :
                    self.line += 1
                continue
            else :
                yield i


    def __init__(self, data) :
        self.data = data    
        self.token = None
        self.token_type = None
        self._next_token = self.tokenize().next
        self.hashtable = {}
        self.mode = None
        self.records = {}        
        self.line = 1

        # compile some regexes
        self.white = re.compile(r"[\n|\s]+")
        self.nl = re.compile(r"[\n]")
        self.token_re = re.compile(r"([^\s\"#%'(){}@,=]+|\n|@|\"|{|}|=|,)")


    def parse(self) :
        """Parses :py:attr:`data` and stores the parsed BibTeX entries to :attr:`.records`"""
        while True :
            try :
                self.next_token()               
                while self.database() :
                    pass            
            except StopIteration :
                break


    def next_token(self):
        self.token = self._next_token()
        #print self.line, self.token


    def database(self) :
        if self.token == '@' :            
            self.next_token()            
            self.entry()


    def entry(self) :
        if self.token.lower() == 'string' :
            self.mode = 'string'
            self.string()
            self.mode = None
        else :
            self.mode = 'record'            
            self.record()
            self.mode = None


    def string(self) :
        if self.token.lower() == "string" :
            self.next_token()
            if self.token == "{" :
                self.next_token()
                self.field()
                if self.token == "}" :
                    pass
                else :                      
                    raise NameError("} missing")


    def field(self) :
        name = self.name()
        if self.token == '=' :
            self.next_token()
            value = self.value()
            if self.mode == 'string' :                
                self.hashtable[name] = value
            return (name, value)            


    def value(self) :
        value = ""
        val = []

        while True :
            if self.token == '"' :              
                while True:
                    self.next_token()
                    if self.token == '"' :
                        break
                    else :
                        val.append(self.token)            
                if self.token == '"' :          
                    self.next_token()
                else :
                    raise NameError("\" missing")
            elif self.token == '{' :            
                brac_counter = 0
                while True:
                    self.next_token()
                    if self.token == '{' :
                        brac_counter += 1
                    if self.token == '}' :              
                        brac_counter -= 1
                    if brac_counter < 0 :
                        break
                    else :
                        val.append(self.token)            
                if self.token == '}' :
                    self.next_token()
                else :
                    raise NameError("} missing")
            elif self.token != "=" and re.match(ur"\w|#|,", self.token) :
                value = self.query_hashtable(self.token)
                val.append(value)
                while True:
                    self.next_token()                    
                    # if token is in hashtable then replace                    
                    value = self.query_hashtable(self.token)
                    if re.match(ur"[^\w#]|,|}|{", self.token) : #self.token == '' :
                        break
                    else :
                        val.append(value) 

            elif self.token.isdigit() :
                value = self.token
                self.next_token()
            else :
                if self.token in self.hashtable :
                    value = self.hashtable[ self.token ]
                else :
                    value = self.token          
                self.next_token()

            if re.match(ur"}|,",self.token ) :
                break            

        value = ' '.join(val)

        # PATCH!
        value = value.replace('\\ " ','\\"')
        value = value.replace(' { ','{')
        value = value.replace(' } ','}')
        value = value.replace('{ ','{')
        value = value.replace('} ','}')
        value = value.replace(' {','{')
        value = value.replace(' }','}')

        return value


    def query_hashtable( self, s ) :
        if s in self.hashtable :
            return self.hashtable[ self.token ]
        else :
            return s


    def name(self) :
        name = self.token
        self.next_token()
        return name


    def key(self) :
        key = self.token
        self.next_token()
        return key


    def record(self) :
        if self.token not in ['comment', 'string', 'preamble'] :          
            record_type = self.token
            self.next_token()            
            if self.token == '{' :
                self.next_token()
                key = self.key()
                self.records[ key ] = {}
                self.records[ key ]['ENTRYTYPE'] = str(record_type.lower())
                self.records[ key ]['ID'] = str(key)
                if self.token == ',' :              
                    while True:
                        self.next_token()
                        field = self.field()
                        if field :
                            k = str(field[0].lower())
                            val = field[1]

                            if k == 'page':
                                k = 'pages'

                            if k == 'pages':
                                val = val.replace('--', '-')

                            if k == 'title' :
                                #   Preserve capitalization, as described in http://tex.stackexchange.com/questions/7288/preserving-capitalization-in-bibtex-titles
                                #   This will likely choke on nested curly-brackets, but that doesn't seem like an ordinary practice.
                                def capitalize(s):
                                    return s.group(1) + s.group(2).upper()
                                while val.find('{') > -1:
                                    caps = (val.find('{'), val.find('}'))
                                    val = val.replace(val[caps[0]:caps[1]+1], re.sub("(^|\s)(\S)", capitalize, val[caps[0]+1:caps[1]]).strip())
                        
                            self.records[ key ][k] = val
                        if self.token != ',' :                      
                            break               
                    if self.token == '}' :
                        pass
                    else :
                        # assume entity ended
                        if self.token == '@' :
                            pass
                        else :                            
                            raise NameError("@ missing")


