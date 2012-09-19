#!/usr/bin/env python

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
