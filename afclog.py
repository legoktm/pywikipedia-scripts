#!/usr/bin/env python
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

import time
import pywikibot
import robot


class AFCLogger(robot.Robot):

    def __init__(self):
        robot.Robot.__init__(self, task=0)

    def parseArgs(self):
        for arg in self.args:
            pass

    def getStatus(self, page):
        pending = False
        denied = False
        if not page.exists():
            return 'deleted'
        if page.namespace() == 0:
            return 'approved'
        text = page.get()
        if '{{AFC submission||'.lower() in text.lower():
            pending = True
        if '{{AFC submission|d|'.lower() in text.lower():
            denied = True
        if pending and denied:
            return 're-submit'
        if pending:
            return 'pending'
        if denied:
            return 'denied'
        return 'unknown'

    def wrapTemplate(self, page):
        if page.namespace() == 1:
            page = page.toggleTalkPage()
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        else:
            page = page
        status = self.getStatus(page)
        title = page.title(asLink=True)
        top = None
        bottom = None
        if status == 'approved':
            top = '{{afc-c|a}}'
            bottom = '{{afc-c|b}}'
            return 'approved', page
        elif status in ['re-submit', 'pending']:
            top = ''
            bottom = ''
            return 'pending', page
        elif status == 'deleted':
            top = '<!--'
            botom = '-->'
        elif status == 'denied':
            top = '{{afc-c|d}}'
            bottom = '{{afc-c|b}}'
            return 'denied', page
        else:
            #status == 'unknown'?
            top = ''
            bottom = ''
            return 'unknown', page
        header = '= %s =\n' % title
        if not bottom.endswith('\n'):
            bottom += '\n'
        transclude = '[[%s]]' % page.title()
        return header + top + transclude + bottom

    def run(self):
        page = pywikibot.Page(
            self.site, 'Category:AfC submissions by date/12 September 2012')
        category = pywikibot.Category(page)
        gen = pywikibot.pagegenerators.CategorizedPageGenerator(category)
        approved = '==Accepted==\n'
        pending = '==Pending==\n'
        denied = '==Denied==\n'
        unknown = '==Unknown==\n'
        for page in gen:
            print page
            new, page2 = self.wrapTemplate(page)
            text = '* %s\n' % page2.title(asLink=True)
            exec "%s += text" % new
        full = approved + pending + denied + unknown
        pg = pywikibot.Page(self.site, 'User:Legobot/AFC/2012-09-12')
        pg.put(full, 'Bot: Updating AFC log')

if __name__ == "__main__":
    bot = AFCLogger()
    bot.run()
