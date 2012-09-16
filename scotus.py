#!/usr/bin/env python
# -*- coding: utf-8 -

# (C) Legoktm 2012 under the MIT License
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