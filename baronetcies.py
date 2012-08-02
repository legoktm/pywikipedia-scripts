#!/usr/bin/env python
#
# (C) Legoktm, 2012 under the MIT License
#
# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=504648019#Baronetcy_articles
#
# Will mass move all non-redirect articles to their lower-case variants

import pywikibot

site = pywikibot.getSite()
REASON = 'BOT: Moving %s to %s per [[Talk:Abdy_Baronets#Requested_move|RM]]'

def do_page(page):
    old_title = page.title()
    if page.isRedirect():
        print 'Skipping %s, it\'s a redirect' % page.title()
        return
    if not 'Baronets' in old_title:
        print 'Skipping %s, doesnt contain \'Baronets\' in it.'
    new_title = old_title.replace('Baronets', 'baronets')
    edit_summary = REASON % (old_title, new_title)
    print 'Moving: %s --> %s' % old_title, new_title
    page.move(new_title, reason=edit_summary, movetalkpage=True)
    
        

def main():
    cat = pywikibot.Category(pywikibot.Page(site, 'Category:Baronetcies'))
    gen = pywikibot.pagenerators.CategorizedPageGenerator(cat)
    for page in gen:
        do_page(page)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
    