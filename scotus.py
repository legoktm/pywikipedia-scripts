#!/usr/bin/env python
# -*- coding: utf-8 -

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
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=505208009#Create_a_lot_of_unpunctuated_redirects for details
from __future__ import unicode_literals
import sys
import re
import pywikibot
import robot


CASE = re.compile('(.*?)\sv.\s(.*)')
REDIR_TEXT = '#REDIRECT [[%s]]\n{{R from modification}}'

class RedirectBot(robot.Robot):
    
    def __init__(self):
        robot.Robot.__init__(self, task=17)
        self.setAction('BOT: Creating redirect for alternate punctuation')
    
        
    def process_page(self, page):
        if page.isRedirectPage():
            self.output('* Skipping [[%s]] since it is a redirect.' % page.title(),debug=True)
            return
        elif page.namespace() != 0:
            self.output('* Skipping [[:%s]] since it is not in the mainspace.' % page.title(),debug=True)
            return
        if not re.search(CASE, page.title()):
            self.output('* Error: [[:%s]] did not match the case regex.' % page.title(),debug=True)
            return
        redir_title = page.title().replace(' v. ', ' v ')
        redir = pywikibot.Page(self.site, redir_title)
        if redir.exists():
            if not redir.getCreator() == 'Legobot':
                self.output('* Error: [[:%s]] already exists. Skipping.' % redir.title(),debug=True)
            return
        text = REDIR_TEXT % page.title()
        self.edit(redir, text, async=True)
        self.output('* Success: [[:%s]] points to [[:%s]].' % (redir.title(), page.title()))
        
    
    def run(self):
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/SCOTUS'))
        page = pywikibot.Page(self.site, 'Category:United States Supreme Court cases')
        category = pywikibot.Category(page)
        gen = pywikibot.pagegenerators.CategorizedPageGenerator(category, recurse=True)
        for page in gen:
            self.process_page(page)
    

if __name__ == "__main__":
    bot = RedirectBot()
    try:
        bot.run()
    finally:
        bot.pushLog()