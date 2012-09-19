#!/usr/bin/python
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


"""
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

    