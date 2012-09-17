#!/usr/bin/env python
from __future__ import unicode_literals

import webbrowser
import pywikibot
import mwparserfromhell
site = pywikibot.Site()

def fetch_pages():
    temp = pywikibot.Page(site, 'Template:AFC statistics')
    text = temp.get()
    code = mwparserfromhell.parse(text)
    do_these = list()
    for template in code.filter_templates():
        if template.name != 'AFC statistics/row':
            continue
        if template.get('s').value != 'p':
            continue
        do_these.append(template.get('t').value)
    
    for article in do_these:
        do_page(article)

def do_page(article):
    pg = pywikibot.Page(site, article)
    if not pg.exists():
        return
    while pg.isRedirectPage():
        pg = pg.getRedirectTarget()
    if pg.namespace() != 2:
        print 'Skipping %s.' % pg.title()
        return
    text = pg.get()
    text = pywikibot.removeDisabledParts(text)
    print '--------%s---------' % pg.title()
    print text[:150]
    print '-------------------'
    x=raw_input('What should the title be? ')
    if x == 's':
        print 'Skipping.'
        return
    elif x == 'o':
        webbrowser.open('http://enwp.org/%s' %pg.title())
        return
    new_title = 'Wikipedia talk:Articles for creation/' + x.strip()
    reason = 'Preferred location for [[WP:AFC|AfC]] submissions'
    new_pg = pywikibot.Page(site, new_title)
    if new_pg.exists():
        print '%s already exists, will add a (2) to the end.' % new_pg.title()
        new_title += ' (2)'
    print 'Moving to %s' % new_title
    pg.move(new_title, reason)
    
if __name__ == "__main__":
    fetch_pages()
