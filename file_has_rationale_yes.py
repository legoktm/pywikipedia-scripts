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
import awb_gen_fixes


class FileHasRationaleYesBot(robot.Robot):
    def __init__(self):
        robot.Robot.__init__(self, task=22)
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/Logs/22'))
        self.cat = pywikibot.Category(self.site, "Category:Non-free images for NFUR review")
        self.gen = self.cat.articles(namespaces=[6], content=True)
        self.AWBGenFixes = awb_gen_fixes.AWBGenFixes(self.site)
        self.AWBGenFixes.load()
        self.AWBGenFixes.load_redirects(pywikibot.Page(self.site, 'User:Legoktm/AWB/TR'))
        self.stop_page = pywikibot.Page(self.site, 'User:Legobot/Stop/22')
    def run(self):
        #fetch copyright licenses
        cat = pywikibot.Category(self.site, 'Category:Wikipedia non-free file copyright tags')
        templates = cat.articles(namespaces=[10])
        self.licenses = [temp.title(withNamespace=False).lower() for temp in templates]
        cat2 = pywikibot.Category(self.site, 'Category:Non-free use rationale templates')
        nfur_temps = cat2.articles(namespaces=[10])
        self.NFURs = [temp.title(withNamespace=False).lower() for temp in nfur_temps]
        for page in self.gen:
            self.do_page(page)


    def check_page(self):
        text = self.stop_page.get(force=True)
        if text.lower() != 'run':
            raise Exception("Stop page disabled")
    def do_page(self, page):
        print page.title(asLink=True)
        if page.namespace() != 6:
            return
        text = page.get()
        if '<nowiki>' in text:
            print 'NOWIKI'
        #    return
        text, gen_fix_summary = self.AWBGenFixes.do_page(text)
        code = mwparserfromhell.parse(text)
        tag = False
        log = '* '
        summary = 'Bot: Updating license tag(s) with image has rationale=yes'
        for template in code.filter_templates(recursive=True):
            name = template.name.lower().strip()
            if name in self.NFURs:
                print name
                tag = True
        if tag:
            for template in code.filter_templates(recursive=True):
                if template.name.lower().strip() in self.licenses:
                    template.add('image has rationale', 'yes')
                    log += '[[:%s]]: Adding <code>|image has rationale=yes</code>' % page.title()
        else:
            print 'Skipping '+page.title(asLink=True)
            return
        if gen_fix_summary:
            summary += ', also dating ' + gen_fix_summary
        puttext = unicode(code).lstrip('\n')
        pywikibot.showDiff(text, puttext)
        self.output(log)
        self.check_page()
        try:
            page.put(puttext, summary)
        except pywikibot.exceptions.PageNotSaved:
            pass





if __name__ == "__main__":
    pywikibot.handleArgs()
    bot = FileHasRationaleYesBot()
    try:
        bot.run()
    finally:
        #bot.pushLog()
        pass