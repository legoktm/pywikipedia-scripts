#!/usr/bin/env python
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
import re
import pywikibot
import mwparserfromhell
SITE = pywikibot.Site()
months=['January','February','March','April','May','June','July','August','September','October','November','December']
j='|'.join(months)
regex=re.compile('(?P<month>'+j+'|)\s*(?P<year>\d\d\d\d)')
def gen():
    page = pywikibot.Page(SITE, 'Template:Infobox NRHP')
    for c in page.getReferences(onlyTemplateInclusion=True,namespaces=[0], content=True):
        yield c

def process_page(page):
    text = original = page.get()
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.lower().strip() == 'infobox nrhp':
            if template.has_param('built'):
                val = template.get('built').value.strip()
                s=regex.search(val)
                if not s:
                    return
                d=s.groupdict()
                if int(d['year']) < 1583:
                    return
                if d['month']:
                    d['month'] = months.index(d['month'])+1
                    template.get('built').value = '{{Start date|{year}|{month}}}'.format(**d)
                else:
                    template.get('built').value = '{{Start date|{year}}}'.format(**d)
    text = unicode(code)
    if original == text:
        return
    page.put(text, 'Bot: Wrapping date in {{start date}} to add [[WP:UF|microformats]]')

def main():
    for page in gen():
        process_page(page)

if __name__ == "__main__":
    try:
        main()
    finally:
        pass
