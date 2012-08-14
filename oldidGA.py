#!/usr/bin/env python
# -*- coding: utf-8 -

# (C) Legoktm 2012 under the MIT License
# See https://en.wikipedia.org/wiki/Wikipedia:Bot_requests/Archive_49#Bot_request_for_adding_oldid_parameters_to_good_articles
import time
import re
import pywikibot
import robot

class OldidGABot(robot.Robot):
    def __init__(self):
       robot.Robot.__init__(self, task=18)
    def run(self):
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/GA'))
        page = pywikibot.Page(self.site, 'Category:Good articles without an oldid')
        category = pywikibot.Category(page)
        gen = pywikibot.pagegenerators.CategorizedPageGenerator(category)
        for page in gen:
            self.process_page(page)
        
    def process_page(self, page):
        talk_page = page
        page = talk_page.toggleTalkPage()
        #find the edit where {{good article}] was added
        foundOldid = False
        oldid = None
        real_oldid = None
        while not foundOldid:
            hist = page.fullVersionHistory(total=10, startid=oldid)
            for revision in hist:
                if re.search('\{\{(good|ga) article\}\}', revision[3], re.IGNORECASE):
                    oldid = revision[0]
                else:
                    #current oldid is the right one
                    foundOldid = True
                    break
        #add the oldid in the template
        self.output('Working on %s' % talk_page.title())
        oldtext = talk_page.get()
        search = re.search('\{\{GA\|(.*?)\}\}', oldtext)
        newtext = oldtext.replace(search.group(0), '{{GA|%s|oldid=%s}}' % (search.group(1), oldid))
        pywikibot.showDiff(oldtext, newtext)
        time.sleep(10)
        talk_page.put(newtext, 'BOT: Adding |oldid=%s to {{[[Template:GA|GA]]}}' % oldid)
        
                
            
if __name__ == "__main__":
    bot = OldidGABot()
    bot.run()
