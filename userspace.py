#!/usr/bin/python

"""
(C) 2012, Legoktm, under the MIT License
Checks the new pages list to see whether
it should have been made in the userspace, and if so, moves it.
"""

import robot

import pywikibot


class UserspaceWatcher(robot.Robot):
    
    def __init__(self):
        robot.Robot.__init__(self, task=14)
        self.start_trial(100)
    
    def fetch_pages(self):
        return pywikibot.pagegenerators.NewpagesPageGenerator(total=100)
    
    
    def run(self):
        gen = self.fetch_pages()
        for page in gen:
            creator = page.getVersionHistory(reverseOrder=True, total=1)[0][2]
            if page.title().startswith(creator + '/'):
                old = page.title()
                new = 'User:' + page.title()
                #verify that we haven't touched the page yet
                history = page.getVersionHistory()
                goOn = True
                for item in history:
                    if item[2] == u'Legobot':
                        self.output('We have already touched %s. Skipping!' % page.title())
                        goOn = False
                        break
                if not goOn:
                    continue
                page.move(new, reason='BOT: Moving accidentally created subpage into userspace')
                #Leave a talk-page notice
                talk = pywikibot.Page(self.site, 'User talk:' + creator)
                notice = '{{subst:User:Legobot/userfy move|1=%s|2=%s}} ~~~~' % (old, new)
                existing = talk.get()
                talk.put(existing+notice, 'Bot moved [[%s]] to [[%s]]' % (old, new), minorEdit=False)
                self.trial_action()
            else:
                self.output('Skipping %s' % page.title(asLink=True))
                continue

if __name__ == "__main__":
    bot = UserspaceWatcher()
    bot.run()

    