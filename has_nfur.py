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
import mwparserfromhell
import robot


class EnforceTFD(robot.Robot):
    def __init__(self):
        self.count = 0
        robot.Robot.__init__(self, task=21)
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/Logs/20'))
        self.template = 'has-NFUR'
        self.t_p = pywikibot.Page(self.site, 'Template:'+self.template)
        self.gen = pywikibot.pagegenerators.ReferringPageGenerator(self.t_p, onlyTemplateInclusion=True)
    def run(self):
        #fetch copyright licenses
        self.summary = 'Bot: Removing {{has-NFUR}} per [[Wikipedia:Templates_for_discussion/Log/2012_September_16#Template:Has-NFUR|TFD]]'
        self.licenses = []
        cat = pywikibot.Category(self.site, 'Category:Wikipedia non-free file copyright tags')
        templates = cat.articles(namespaces=[10])
        for temp in templates:
            self.licenses.append(temp.title(withNamespace=False).lower())
        cat2 = pywikibot.Category(self.site, 'Category:Non-free use rationale templates')
        templates = cat.articles(namespaces=[10])
        self.NFURs = {}
        for temp in templates:
            t=temp.title(withNamespace=False)
            redirs = [page.title(withNamespace=False).lower() for page in temp.getReferences(redirectsOnly=True)]
            redirs.append(t.lower())
            self.NFURs[t] = redirs
        for page in self.gen:
            self.do_page(page)

    def do_page(self, page):
        print page.title(asLink=True)
        if page.namespace() != 6:
            return
        text = page.get()
        if '<nowiki>' in text:
            print 'NOWIKI'
        #    return
        code = mwparserfromhell.parse(text)
        tag = False
        log = '* Removing from [[:%s]]' % page.title()
        for template in code.filter_templates(recursive=True):
            name = template.name.lower().strip()
            if name == self.template.lower():
                code.replace(template, '')
            for temp in self.NFURs.keys():
                if name in self.NFURs[temp]:
                    template.name = temp
                    tag = True
        if tag:
            for template in code.filter_templates(recursive=True):
                if template.name.lower().strip() in self.licenses:
                    template.add('file has rationale', 'yes')
                    log += ', adding <code>|file has rationale=yes</code>'

        puttext = unicode(code).lstrip('\n')
        pywikibot.showDiff(text, puttext)
        self.output(log)
        page.put(puttext, self.summary)





if __name__ == "__main__":
    bot = EnforceTFD()
    try:
        bot.run()
    finally:
        #bot.pushLog()
        pass