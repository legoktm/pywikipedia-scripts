#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2012 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import sys
import os
import pywikibot

# (C) Legoktm 2012 under the MIT License
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=503238261#narrow_down_digraph_redirects for details

site = pywikibot.getSite()

def logError(page):
    logFile = 'errors2.txt'
    if os.path.isfile(logFile):
        f = open(logFile, 'r')
        old = f.read()
        f.close()
    else:
        old = ''
    new = old + u'*[[%s]\n' % page.title()
    f = open(logFile, 'w')
    try:
        f.write(new)
    except UnicodeEncodeError:
        print 'UnicodeEncodeError while logging'
    f.close()
    print u'*Logged an error on [[%s]]' % page.title()

def parseSection(section):
    target = section['target']
    
    for page in section['pages']:
        processPage(page, target)

def processPage(pg, target):
    #fix the pagename
    page = pywikibot.Page(site, pg)
    shouldBeText = '#REDIRECT [[List of Latin-script trigraphs#%s]]' % target
    #^what the redirect should point to
    if page.exists():
        if page.isRedirectPage():
            currentTarget = page.getRedirectTarget()
            if currentTarget == pywikibot.Page(site, 'Trigraph (orthography)'):
                #check the section linking
                currentText = page.get(get_redirect=True)
                if currentText == shouldBeText:
                    print '*Skipping [[%s]]' % page.title()
                    return
                #not pointing at the right section, lets fix that
                print 'Fixing [[%s]]' % page.title()
                page.put(shouldBeText, 'BOT: Fixing section link in redirect.')
                return
            #page is redirecting somewhere else? log as an error and lets continue    
            logError(page)
            return
        #page exists, but isn't a redirect? log error and move on
        logError(page)
        return
    #page doesn't exist, skip it    

def main():
    run_page = pywikibot.Page(site, 'User:Legoktm/list2')
    parse = run_page.get()
    sections = list()
    lines = parse.split('\n')
    new = False
    current = {}
    for line in lines:
        if line == '':
            continue
        if line.startswith('=='):
            if current:
                sections.append(current)
                current = {}
            current['target'] = line.split('==')[1]
            current['pages'] = list()
        else:
            current['pages'].append(line)
    if current:
        sections.append(current)
    for section in sections:
        parseSection(section)

if __name__ == "__main__":
    main()