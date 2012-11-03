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
import datetime
import pywikibot
import mwparserfromhell

import urlregex
import awb_gen_fixes
SITE = pywikibot.Site()
AWB = awb_gen_fixes.AWBGenFixes(SITE)
AWB.load()

LOG = '==~~~~~=='

TAG = '{{dead link|date=%s|bot=Legobot}}' % datetime.datetime.today().strftime('%B %Y')
def process_page(page):
    text = page.get()
    text, blah = AWB.do_page(text, date=False)
    code = mwparserfromhell.parse(text)
    urls = []
    for m in urlregex.MATCH_URL.finditer(unicode(code)):
        u = m.group(0)
        if u.startswith(('http://ap.google', 'https://ap.google')):
            urls.append(u)
    """
    buffer = unicode(code)
    for template in code.filter_templates():
        for url in urls:
            if url in template:
                if template.has_param('archiveurl'):
                    urls.remove(url)
                else:
                    buffer = buffer.replace(unicode(template), unicode(template)+TAG)
                    urls.remove(url)
    code = buffer
    """
    #find ref tags
    loop1= False
    for tag in re.finditer(r'<ref(.*?)>(.*?)</ref>', unicode(code)):
        for url in urls:
            if url in tag.group(2):
                for template in mwparserfromhell.parse(tag.group(2)).filter_templates():
                    if template.has_param('archiveurl'):
                        try:
                            urls.remove(url)
                        except ValueError:
                            pass
                        loop1 = True
                if loop1:
                    break
                if 'dead link' in tag.group(0).lower():
                    urls.remove(url)
                else:
                    code = unicode(code).replace(tag.group(0), '<ref'+tag.group(1)+'>'+tag.group(2)+TAG+'</ref>')
                    urls.remove(url)
            if loop1:
                loop1 = False
                break
    if urls:
        print 'STILL HAVE THESE LEFT: '+', '.join(urls)

    pywikibot.showDiff(text, unicode(code))
    if text != unicode(code):
        page.put(unicode(code), 'Bot: Tagging ap.google.* links with {{dead link}}')
        return True
    else:
        return None
#process_page(pywikibot.Page(SITE, 'American International Group'))

def gen():
    for page in SITE.exturlusage('ap.google.com', protocol='http', namespaces=[0]):
        yield page
    for page in SITE.exturlusage('ap.google.com', protocol='https', namespaces=[0]):
        yield page

try:

    for page in gen():
        print page
        res = process_page(page)
        print '--------'
finally:
    pass
    #log_page = pywikibot.Page(SITE, 'User:Legobot/Logs/23')
    #log_page.put(LOG, 'Bot: Updating userspace log')