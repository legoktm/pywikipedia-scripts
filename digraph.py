#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pywikibot

# (C) Legoktm 2012 under the MIT License
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=503238261#narrow_down_digraph_redirects for details

site = pywikibot.getSite()

def logError(page):
    logFile = 'errors.txt'
    if os.path.isfile(logFile):
        f = open(logFile, 'r')
        old = unicode(f.read())
        f.close()
    else:
        old = ''
    new = old + u'[[%s]]' % page.title()
    f = open(logFile, 'w')
    try:
        f.write(new)
    except UnicodeEncodeError:
        print 'UnicodeError on logging'
    f.close()
    print u'*Logged an error on [[%s]]' % page.title()

def parseSection(section):
    split = section.split('\n')
    if split[0].startswith('other'):
        target = 'Other letters'
    elif split[0] == "=='==":
        target = 'Apostrophe'
    else:
        target = split[0][0].upper()
    split = split[1:]
    for page in split:
        processPage(page, target)

def processPage(pg, target):
    pg = pg.replace('[[','').replace(']]','') #de-wikilink
    page = pywikibot.Page(site, pg)
    shouldBeText = '#REDIRECT [[List of Latin-script digraphs#%s]]' % target
    #^what the redirect should point to
    if page.exists():
        if page.isRedirectPage():
            currentTarget = page.getRedirectTarget()
            if currentTarget == pywikibot.Page(site, 'List of Latin-script digraphs'):
                #check the section linking
                currentText = page.get(get_redirect=True)
                if currentText == shouldBeText:
                    print '*Skipping [[%s]]' % page.title()
                    return
                #not pointing at the right section, lets fix that
                print '*Fixed [[%s]]' % page.title()
                page.put(shouldBeText, 'BOT: Fixing section link in redirect.')
                return
            #page is redirecting somewhere else? log as an error and lets continue    
            logError(page)
            return
        #page exists, but isn't a redirect? log error and move on
        logError(page)
        return
    #page doesn't exist, lets create it!
    print '*Created [[%s]]' % page.title()
    page.put(shouldBeText, 'BOT: Creating redirect for digraph')
    

def main():
    run_page = pywikibot.Page(site, 'User:Legoktm/list')
    parse = run_page.get()
    split = parse.split('\n==')
    for section in split:
        parseSection(section)

if __name__ == "__main__":
    main()