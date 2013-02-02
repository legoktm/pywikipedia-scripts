#!/usr/bin/env python
from __future__ import unicode_literals

import re
import pywikibot
import mwparserfromhell
"""
Copyright (C) 2013 Legoktm

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
template = 'HarzMountain-geo-stub'

def do_page(page):
    text = page.get()
    newtext = re.sub('\{\{(h|H)arzM(ountain|tn)-geo-stub\}\}\s?','', text)
    pywikibot.showDiff(text, newtext)
    page.put(newtext, 'Bot: Removing {{HarzMountain-geo-stub}} per [[WP:Categories_for_discussion/Log/2013_January_24#Category:Harz_Mountain_geography_stubs|CfD]]')

def main():
    site = pywikibot.Site()
    temp = pywikibot.Page(site, 'Template:HarzMountain-geo-stub')
    gen = pywikibot.pagegenerators.ReferringPageGenerator(temp, onlyTemplateInclusion = True)
    for page in gen:
        do_page(page)

if __name__ == "__main__":
    main()