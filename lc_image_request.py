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
SITE = pywikibot.Site()
FIX_THESE = ['Technology', 'Society', 'Science', 'History', 'Arts']
SUMMARY = 'Robot - Speedily moving category Wikipedia requested photographs of %s to [[Category:Wikipedia requested photographs of %s]] per [[WP:CFDS|CFDS]].'

def supergen():
    cat = pywikibot.Category(SITE, 'Category:Wikipedia requested photographs of Technology')
    for page in cat.articles():
        yield page
    cat = pywikibot.Category(SITE, 'Category:Wikipedia requested photographs of Society')
    for page in cat.articles():
        yield page
    cat = pywikibot.Category(SITE, 'Category:Wikipedia requested photographs of Science')
    for page in cat.articles():
        yield page
    cat = pywikibot.Category(SITE, 'Category:Wikipedia requested photographs of History')
    for page in cat.articles():
        yield page
    cat = pywikibot.Category(SITE, 'Category:Wikipedia requested photographs of Arts')
    for page in cat.articles():
        yield page


def fetch_redirects():
    temp = pywikibot.Page(SITE, 'Template:Image requested')
    all = [page.title(withNamespace=False).lower() for page in temp.getReferences(redirectsOnly=True)]
    all.append(temp.title(withNamespace=False).lower())
    return all

def do_page(page, redirs):
    print page
    text = page.get()
    code = mwparserfromhell.parse(text)
    summary = None
    for template in code.filter_templates(recursive=True):
        if template.name.lower() in redirs:
            template.name = 'Image requested'
            if template.has_param(1):
                val = template.get(1).value
                if val.strip() in FIX_THESE:
                    new_val = val.lower()
                    template.remove(1)
                    template.add(1, new_val)
                    summary = SUMMARY % (val, new_val)
            if template.has_param(2):
                val = template.get(2).value
                if val.strip() in FIX_THESE:
                    new_val = val.lower()
                    template.remove(2)
                    template.add(2, new_val)
                    summary = SUMMARY % (val, new_val)
            if template.has_param(3):
                val = template.get(3).value
                if val.strip() in FIX_THESE:
                    new_val = val.lower()
                    template.remove(3)
                    template.add(3, new_val)
                    summary = SUMMARY % (val, new_val)


    pywikibot.showDiff(text, unicode(code))
    if summary:
        page.put(unicode(code), summary)

def main():
    gen = supergen()
    redirs = fetch_redirects()
    for page in gen:
        do_page(page, redirs)

if __name__ == "__main__":
    main()

