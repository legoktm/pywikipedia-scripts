#!/usr/bin/env python
from __future__ import unicode_literals

import pywikibot
import mwparserfromhell
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


def player(name):
    print name
    text = name.get()
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.lower() == 'Infobox MLB player'.lower():
            if not template.has_param('team'):
                return 'retired'
            if not template.has_param('statyear'):
                return 'retired'
            return template.get('statyear').value.strip()
    return 'retired'

def main():
    site = pywikibot.Site()
    temp = pywikibot.Page(site, 'Template:Infobox MLB player')
    gen = pywikibot.pagegenerators.ReferringPageGenerator(temp, onlyTemplateInclusion = True, content = True)
    master_text = """{| class="sortable"
|-
! name
! date
|-"""
    for page in gen:
        try:
            time = player(page)
        except:
            continue
        if time == 'retired':
            continue
        text = "\n|%s\n|%s\n|-" % (page.title(asLink=True), time)
        print text
        master_text += text
    master_text += '\n|}'
    pg = pywikibot.Page(site, 'User:Legobot/Baseball')
    #print master_text
    pg.put(master_text, 'Bot: Updating list')

if __name__ == "__main__":
    main()