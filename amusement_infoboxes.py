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
import pywikibot
import mwparserfromhell

site = pywikibot.Site()
category = pywikibot.Category(site, 'Category:Amusement parks')
COUNT = 0
ALL = []
for page in category.articles(recurse=True, namespaces=[0], content=True):
    if page.isRedirectPage():
        continue
    print page
    text = page.get()
    code = mwparserfromhell.parse(text)
    has = False
    for template in code.filter_templates(recursive=True):
        name = pywikibot.removeDisabledParts(unicode(template.name)).lower().strip()
        if name.startswith('infobox'):
            has = True
            break
    if not has:
        if page.title() in ALL:
            print 'Skipping duplicate of '+page.title()
            continue
        ALL.append(page.title())
        COUNT += 1
        print '+1'
    if COUNT >= 500:
        break

TEXT = ''
for item in ALL:
    TEXT+= '#[[%s]]\n' % item

pg = pywikibot.Page(site, 'Wikipedia:WikiProject Amusement Parks/Need infoboxes')
pg.put(TEXT, 'Bot: Updating list of pages needing an infobox')