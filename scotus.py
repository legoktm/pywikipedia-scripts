#!/usr/bin/env python
# -*- coding: utf-8 -

# (C) Legoktm 2012 under the MIT License
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=505208009#Create_a_lot_of_unpunctuated_redirects for details

import re
import pywikibot

CASE = re.compile('(.*?)\sv.\s(.*)')
REDIR_TEXT = '#REDIRECT [[%s]]\n{{R from modification}}'

class RedirectBot:
    
    def __init__(self):
        self.site = pywikibot.getSite()
        self.logText = ''
    
    def log(self, text):
        self.logText += text + '\n'
        print text
        
    def process_page(self, page):
        if page.isRedirectPage():
            self.log('* Skipping [[%s]] since it is a redirect.' % page.title())
            return
        elif page.namespace() != 0:
            self.log('* Skipping [[:%s]] since it is not in the mainspace.' % page.title())
            return
        match = re.search(CASE, page.title())
        if not match:
            self.log('* Error: [[:%s]] did not match the case regex.' % page.title())
            return
        redir_title = page.title().replace(' v. ', ' v ')
        redir = pywikibot.Page(self.site, redir_title)
        if redir.exists():
            self.log('* Error: [[:%s]] already exists. Skipping.' % redir.title())
            return
        text = REDIR_TEXT % page.title()
        redir.put(text, 'BOT: Creating redirect for alternate punctuation')
        self.log('* Success: [[:%s]] points to [[:%s]].' % (redir.title(), page.title()))
        
    
    def run(self):
        page = pywikibot.Page(self.site, 'Category:United States Supreme Court cases')
        category = pywikibot.Category(page)
        gen = pywikibot.pagegenerators.CategorizedPageGenerator(category, recurse=True)
        for page in gen:
            self.process_page(page)
    
    def putLog(self):
        logPage = pywikibot.Page(self.site, 'User:Legobot/SCOTUS')
        if logPage.exists():
            oldtext = logPage.get()
        else:
            oldtext = ''
        newtext = oldtext + self.logText
        logPage.put(newtext, 'BOT: Updating log of redirects created')


if __name__ == "__main__":
    bot = RedirectBot()
    try:
        bot.run()
    finally:
        bot.putLog()