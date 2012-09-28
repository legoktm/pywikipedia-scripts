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
        robot.Robot.__init__(self, task=21)
        self.startLogging(pywikibot.Page(self.site, 'User:Legoktm/Logs/20'))
        self.template = 'has-NFUR'
        self.t_p = pywikibot.Page(self.site, 'Template:'+self.template)
        self.gen = pywikibot.pagegenerators.ReferringPageGenerator(self.t_p, onlyTemplateInclusion=True)
    def run(self):
        #fetch copyright licenses
        self.summary = 'Bot: Removing {{has-NFUR}} per [[Wikipedia:Templates_for_discussion/Log/2012_September_16#Template:Has-NFUR|TFD]]'

        all = pywikibot.Page(self.site, 'Wikipedia:File copyright tags/Non-free')
        text = all.get()
        code = mwparserfromhell.parse(text)
        self.licenses = []
        #fetch redirects for Non-free use rationale and Non-free image rationale
        self.nfur = 'Non-free use rationale'
        nfur_p = pywikibot.Page(self.site, 'Template:'+self.nfur)
        self.nfir = 'Non-free image rationale'
        nfir_p = pywikibot.Page(self.site, 'Template:'+self.nfir)
        all = list(nfur_p.getReferences(redirectsOnly=True))
        self.nfurs = [page.title(withNamespace=False).lower() for page in all]
        self.nfurs.append(self.nfur.lower())
        all2 = list(nfir_p.getReferences(redirectsOnly=True))
        self.nfirs = [page.title(withNamespace=False).lower() for page in all2]
        self.nfirs.append(self.nfir.lower())

        for template in code.filter_templates():
            if template.name == 'tl':
                self.licenses.append(template.get(1).value.lower())

        for page in self.gen:
            self.do_page(page)

    def do_page(self, page):
        text = page.get()
        code = mwparserfromhell.parse(text)
        tag = False
        log = '* Removing from [[:%s]]' % page.title()
        for template in code.filter_templates():
            print template
            name = template.name.lower().strip()
            if name == self.template.lower():
                code.replace(template, '')
            elif name in self.nfurs:
                template.name = self.nfur
                tag = True
            elif name in self.nfirs:
                template.name = self.nfir
                tag = True
        if tag:
            for template in code.filter_templates():
                if template.name.lower().strip() in self.licenses:
                    template.add('image has rational', 'yes')
                    log += ', adding <code>|image has rational=yes</code>'


        pywikibot.showDiff(text, unicode(code))
        self.output(log)
        page.put(unicode(code), self.summary)





if __name__ == "__main__":
    bot = EnforceTFD()
    try:
        bot.run()
    finally:
        bot.pushLog()
