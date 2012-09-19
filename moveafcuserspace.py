#!/usr/bin/env python
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
