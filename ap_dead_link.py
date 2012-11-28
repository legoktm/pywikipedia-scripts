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

LOG = '==~~~~~=='

class DeadLinkTaggerBot:
    def __init__(self, domain):
        self.site = pywikibot.Site()
        self.AWB = awb_gen_fixes.AWBGenFixes(self.site)
        self.tag = '{{dead link|date=%s|bot=Legobot}}' % datetime.datetime.today().strftime('%B %Y')
        self.domain = domain
        self.simulate = False
        if self.domain.startswith('*.'):
            self.clean = self.domain[2:]
        else:
            self.clean = self.domain
        self.matching = re.compile('https?://(www\.)?(.*?)'+re.escape(self.clean))

    def process_page(self, page):
        text = page.get()
        text, blah = self.AWB.do_page(text, date=False)
        code = mwparserfromhell.parse(text)
        urls = []
        for m in urlregex.MATCH_URL.finditer(unicode(code)):
            u = m.group(0)
            if self.matching.search(u):
                urls.append(u)
            else:
                pass
                #print 'Did not match: '+u
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
                    elif 'wayback' in tag.group(0).lower():
                        urls.remove(url)
                    elif 'webcite' in tag.group(0).lower():
                        urls.remove(url)
                    else:
                        code = unicode(code).replace(tag.group(0), '<ref'+tag.group(1)+'>'+tag.group(2)+self.tag+'</ref>')
                        urls.remove(url)
                if loop1:
                    loop1 = False
                    break
        if urls:
            print 'STILL HAVE THESE LEFT: '+', '.join(urls)

        pywikibot.showDiff(text, unicode(code))
        if text != unicode(code):
            if self.simulate:
                print 'Not editing, just simulating.'
                return None
            page.put(unicode(code), 'Bot: Tagging %s links with {{dead link}}' %self.domain)
            return True
        else:
            return None
    #process_page(pywikibot.Page(SITE, 'American International Group'))

    def gen(self):
        for page in self.site.exturlusage(self.domain, protocol='http', namespaces=[0]):
            yield page
        for page in self.site.exturlusage(self.domain, protocol='https', namespaces=[0]):
            yield page

    def run(self):
        for arg in pywikibot.handleArgs():
            if arg == '--sim':
                self.simulate = True
        self.AWB.load()
        for page in self.gen():
            print page
            res = self.process_page(page)
            print '--------'

if __name__ == "__main__":
    bot = DeadLinkTaggerBot('*.btinternet.com')
    bot.run()