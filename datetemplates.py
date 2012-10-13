#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import awb_gen_fixes
#import robot

class DateBot():
    def __init__(self):
        #robot.Robot.__init__(self, task=23)
        self.site = pywikibot.Site()
        self.AWB = awb_gen_fixes.AWBGenFixes(self.site)
        self.stop_page = pywikibot.Page(self.site, 'User:Legobot/Stop/II 2')
        self.summary_end = '. Errors? [[User:Legobot/Stop/II 2|stop me]]'
    def run(self):
        self.AWB.load()
        #gen = pywikibot.pagegenerators.CategorizedPageGenerator(cat, content=True)
        for page in self.gen():
            self.do_page(page)

    def check_run_page(self):
        text = self.stop_page.get(force=True)
        if text.lower() != 'run':
            raise Exception("Stop page disabled")

    def gen(self):
        cat = pywikibot.Category(self.site, 'Category:Wikipedia maintenance categories sorted by month')
        for subcat in cat.subcategories():
            for page in subcat.articles(content=True, namespaces=[0]):
                yield page
    def do_page(self, page):
        print page
        text = page.get()
        if self.AWB.in_use(text):
            return
        newtext, msg = self.AWB.do_page(text)
        if not msg:
            return
        try:
            self.check_run_page()
            page.put(unicode(newtext), 'BOT: Dating templates: '+msg+self.summary_end)
        except pywikibot.exceptions.PageNotSaved:
            pass
        except pywikibot.exceptions.LockedPage:
            pass



if __name__ == "__main__":
    bot = DateBot()
    bot.run()