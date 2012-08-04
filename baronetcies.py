#!/usr/bin/env python
#
# (C) Legoktm, 2012 under the MIT License
#
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=504648019#Baronetcy_articles
#
# Will mass move all non-redirect articles to their lower-case variants

import os
import pywikibot

site = pywikibot.getSite()
REASON = 'BOT: Moving %s to %s per [[Talk:Abdy_Baronets#Requested_move|RM]]'
LOGFILE = 'movepages.log'

def log(old_title, new_title):
    global LOGFILE
    if os.path.isfile(LOGFILE):
        f = open(LOGFILE, 'r')
        old = f.read()
        f.close()
    else:
        old = ''
    msg = '*[[:%s]] --> [[:%s]]\n' % (old_title, new_title)
    f = open(LOGFILE, 'w')
    f.write(old+msg)
    f.close()
    
    

def do_page(page):
    old_title = page.title()
    if page.isRedirectPage():
        print 'Skipping %s, it\'s a redirect' % page.title()
        return
    if not 'Baronets' in old_title:
        print 'Skipping %s, doesnt contain \'Baronets\' in it.' % page.title()
        return
    new_title = old_title.replace('Baronets', 'baronets')
    if old_title == new_title:
        print 'New title is same as old title? logging.'
        log(old_title, new_title)
    edit_summary = REASON % (old_title, new_title)
    print 'Moving: %s --> %s' % (old_title, new_title)
    try:
        page.move(new_title, reason=edit_summary, movetalkpage=True)
    except pywikibot.exceptions.Error, e:
        print e
        log(old_title, new_title)
        return
    
        

def main():
    cat = pywikibot.Category(pywikibot.Page(site, 'Category:Baronetcies'))
    gen = pywikibot.pagenerators.CategorizedPageGenerator(cat)
    for page in gen:
        do_page(page)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
    