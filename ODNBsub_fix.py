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
import re

import pywikibot
import mwparserfromhell

import urlregex
import awb_gen_fixes
SITE = pywikibot.Site()
AWB = awb_gen_fixes.AWBGenFixes(SITE)
AWB.load()

LOG = '==~~~~~=='
TEMPLATES = ['ODNBsub', 'OEDsub']
def process_page(page):
    text = page.get()
    text, blah = AWB.do_page(text, date=False)
    state = text
    #find ref tags
    for tag in re.finditer(r'<ref(.*?)>(.*?)</ref>', text):
        for template in mwparserfromhell.parse(tag.group(2)).filter_templates():
            name = template.name.lower().strip()
            former = unicode(template)
            if name.startswith('cite'):
                if template.has_param('format'):
                    has = False
                    for sub_template in template.get('format').value.filter_templates():
                        name = sub_template.name.strip()
                        if name in TEMPLATES:
                            has = True
                            template.remove('format')
                    if has:
                        text = text.replace(former, unicode(template)+' {{ODNBsub}}')
        #else:
            #code = unicode(code).replace(tag.group(0), '<ref'+tag.group(1)+'>'+tag.group(2)'{{ODNBsub}}</ref>')
            #urls.remove(url)

    pywikibot.showDiff(state, text)
    if text != state:
        page.put(unicode(text), 'Bot: Adjusting placement of {{[[Template:ODNBsub|ODNBsub]]}}')
        return True
    else:
        return None

def gen():
    page = pywikibot.Page(SITE, 'Template:ODNBsub')
    for c in page.getReferences(onlyTemplateInclusion=True,namespaces=[0], content=True):
        yield c
count = 0
try:
    for page in gen():
    #for page in [pywikibot.Page(SITE, 'Bayeux Tapestry')]:
        print page
        res = process_page(page)
        print '--------'
        if res:
            LOG += '\n* '+page.title(asLink=True)
            count += 1
finally:
    print 'COUNTED: %s' % count
    if count > 0:
        log_page = pywikibot.Page(SITE, 'User:Legobot/Logs/25')
        LOG = log_page.text + LOG
        log_page.put(LOG, 'Bot: Updating userspace log')