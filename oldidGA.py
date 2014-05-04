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
from __future__ import unicode_literals
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
        gen = category.articles()
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
            self.site.loadrevisions(page, getText=True, rvdir=False,
                                    step=10, total=10, startid=oldid)
            hist = page.fullVersionHistory(total=10)  # This should fetch nothing...
            for revision in hist:
                if re.search('\{\{(good|ga) article\}\}', revision[3], re.IGNORECASE):
                    oldid = revision[0]
                else:
                    #current oldid is the right one
                    foundOldid = True
                    break
        #add the oldid in the template
        if not oldid:
            self.output('* ERROR: Could not find oldid for [[%s]]' % talk_page.title())
            return
        self.output('* Adding |oldid=%s to [[%s]]' % (oldid, talk_page.title()))
        oldtext = talk_page.get()
        search = re.search('\{\{GA\s?\|(.*?)\}\}', oldtext)
        newtext = oldtext.replace(search.group(0), '{{GA|%s|oldid=%s}}' % (search.group(1), oldid))
        pywikibot.showDiff(oldtext, newtext)
        talk_page.put(newtext, 'BOT: Adding |oldid=%s to {{[[Template:GA|GA]]}}' % oldid)


if __name__ == "__main__":
    bot = OldidGABot()
    try:
        bot.run()
    finally:
        bot.pushLog()
