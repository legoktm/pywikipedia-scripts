#!/usr/bin/env python
from __future__ import unicode_literals
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
site=pywikibot.Site()

cat = ['Category:Anime series','Category:Anime OVAs','Category:Manga series','Category:Japanese television dramas',
'Category:Direct-to-video films','Category:Japanese films','Category:Television commercials','Category:Music videos']

def do_cat(cat):
    cat = pywikibot.Category(site, cat)
    gen = cat.articles(namespaces=[0], content=True)
    for page in gen:
        do_page(page, cat)

def do_page(page, cat):
    text = page.get()
    if cat.title().lower() in text.lower():
        print 'Skipping '+page.title(asLink=True)
        return
    newtext = pywikibot.replaceCategoryLinks(text, [cat], site=site, addOnly=True)
    pywikibot.showDiff(text, newtext)
    print 'Saving '+page.title(asLink=True)
    try:
        page.put(newtext, 'Robot: Adding [[:%s]]' % cat.title())
    except pywikibot.exceptions.LockedPage:
        pass

for c in cat:
    do_cat(c)