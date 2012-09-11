#!/usr/bin/env python
# -*- coding: utf-8 -

# (C) Legoktm 2012 under the MIT License
# See https://en.wikipedia.org/wiki/Wikipedia:Bot_requests/Archive_49#help_in_populating_Category:Transport_infrastructure_by_year_of_completion

import pywikibot
import robot

TRANSPORT_TEXT = """
{{10years|%(century)s|Transport infrastructure completed in|%(year)s|Transport infrastructure by year of completion}}

[[Category:Transport infrastructure by year of completion|%(year)s]]

[[Category:Infrastructure completed in %(year)s]]

[[Category:%(year)s in transport|Infrastructure]]
"""


ALL_CATS = [
        'Category:Airports established in %(year)s',
        'Category:Bridges completed in %(year)s',
        'Category:Roads opened in %(year)s',
        'Category:Lighthouses completed in %(year)s',
        'Category:Railway lines opened in %(year)s',
        'Category:Railway stations opened in %(year)s',
        ]

class TransportCatBot(robot.Robot):
    def __init__(self):
       robot.Robot.__init__(self, task=19)
       self.startLogging(pywikibot.Page(self.site, 'User:Legobot/Transport infrastructure categories'))
       self.start_trial(40)
    def run(self):
        d = {'year':1800, 'century':'19th'}
        while d['year'] <= 2012:
            if d['year'] == 1900:
                d['century'] == '20th'
            elif d['year'] == 2000:
                d['century'] == '21st'
            self.do_cat(d)
            d['year'] += 1
    def do_cat(self, d):
        cat = pywikibot.Category(self.site, 'Category:Transport infrastructure completed in %(year)s' % d)
        if cat.exists():
            subcats = list(cat.subcategories())
        else:
            subcats = []
        good_to_go = False
        shouldhave = []
        for c in ALL_CATS:
            real = pywikibot.Category(self.site, c % d)
            if real.exists():
                good_to_go = True
                if not (real in subcats):
                    shouldhave.append(real)
        if not good_to_go:
            return
        if not cat.exists():
            self.edit(cat, TRANSPORT_TEXT % d, 'BOT: Creating Transport infrastructure by year category')
            self.output('\n* creating [[:%s]]' % cat.title())
        
        

        for i in shouldhave:
            t= i.get()
            n=pywikibot.replaceCategoryLinks(t, [cat],addOnly=True)
            self.edit(i, n, 'BOT: Adding [[:%s]]' % cat.title())
            self.output('\n*adding [[:%s]] to [[:%s]]' % (cat.title(), i.title()))
if __name__ == "__main__":
    bot = TransportCatBot()
    try:
        bot.run()
    finally:
        bot.pushLog()
