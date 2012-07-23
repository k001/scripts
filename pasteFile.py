#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
This work is licensed under the Creative Commons Atribución-NoComercial-CompartirIgual 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
"""
#Upload a code  to http://paste.ideaslabs.com
_authors_ = ['"Ivan Zenteno" <ivan.zenteno@ideaslabs.com>', '"David Valdez" <david.valdez@ideaslabs.com>', '"Edgar García" <edgar.garcia@ideaslabs.com>']

from optparse import OptionParser
import locale, getopt, urllib, urllib2, os, sys, string
locale.setlocale(locale.LC_NUMERIC, "")

parser = OptionParser()
parser.add_option("-f", "--file", action="store", help="File name [required]", dest="file")
parser.add_option("-t", "--time", action="store", help="Time of store (hour, day, week, month)", dest="time")
parser.add_option("-l", "--language", action="store", help="Language file", dest="language")
parser.add_option("-d", "--description", action="store", help="Description of the file", dest="descrip")
(options, args) = parser.parse_args()

class Paste:
    def __init__(self):
        self.time = 1
        self.language = 57
        self.file_name = options.file
        self.code = None
        self.status = 1
        self.description = None
    
    def upload(self, options):
        self.setFile(options)
        if options.time:
            self.setTime(options)        
        if options.language:
            self.setLanguage(options)
        values = {
            'name':self.name,
            'language':self.language,
            'time':self.time,
            'code':self.code,
            'description':self.description,
            'status':self.status,
            'submit':'submit'
        }
        params = urllib.urlencode(values)
        headers =   {
                        'Referer': 'http://paste',
                        'Content-type':'application/x-www-form-urlencoded',
                        'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.10) Gecko/20050813 Epiphany/1.7.6',
                        'Accept-Language' : 'en',
                        'Accept-Charse' :   'utf-8'
        }
        try:
            request = urllib2.Request("http://paste.ideaslabs.com/code/file", params, headers)
            r = urllib2.urlopen(request).read()
            self.setResponse(r)
        except urllib2.HTTPError, e:
            self.setError(e)

    def setFile(self, options):
        try:
            f = open(options.file)
            self.code = f.read()
            self.name = os.getlogin()
            self.file_name = options.file
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def setResponse(self, response):
        self.response = response
    
    def printResponse(self):
        print self.response
    
    def setTime(self, options):
        t = options.time.lower()
        time = {"hour": 1, "week": 2, "day": 3, "month": 4}
        if (t in time):
            self.time = time[t]
        else:
            self.time = 1
    
    def setLanguage(self, options):
        l = options.language.lower()
        lang = {"bash":"10","c++":"19","c#":"21","css":"22","delphi":"24","dos":"27","eeliffel":"29","abap":"2","fortran":"30","freebasic":"31","genero":"32","gml":"34","groovy":"35","haskell":"36","html":"37","actionscript":"3","java":"42","javascript":"43","latex":"44","lisp":"45","lua":"46","matlab":"47","mirc":"48","mysql":"50","objective c":"52","ocaml":"53","pascal":"54","perl":"56","php":"57","ada":"5","python":"60","qbasic":"61","rails":"62","ruby":"65","smalltalk":"69","smarty":"70","sql":"71","tcl":"72","txt":"73","visualbasic":"76","vb.net":"77","visualfoxpro":"79","applescript":"7","batch":"80","xml":"81","asm":"8"}
        if (l in lang):
            self.language = lang[l]
        else:
            print "I still don't know that language sorry"
            sys.exit(2);
    
def main(options):
    if not (options.file):
        print parser.print_help()
        return 0
    else:
        pasting = Paste()
        pasting.upload(options)
        pasting.printResponse()
        
if __name__ == '__main__':
    main(options)