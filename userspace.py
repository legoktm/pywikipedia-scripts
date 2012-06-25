#!/usr/bin/python
#
# (C) 2012, Legoktm, under the MIT License
# Checks the new pages list to see whether it should have been made in the userspace, and if so, moves it.
#

import pywikibot
from pywikibot import pagegenerators
site = pywikibot.getSite()

def main():
  #get page list
  gen = pagegenerators.NewpagesPageGenerator(total=100)
  for page in gen:
    creator = page.getVersionHistory(reverseOrder=True, total=1)[0][2]
    if page.title().startswith(creator + '/'):
      old = page.title()
      new = 'User:' + page.title()
      page.move(new, reason='Moving accidentally created subpage into userspace')
      #delete newly created redirect
      #Apparently bots can move pages without creating redirects so this part isnt needed...
#      oldpage = pywikibot.Page(site, old)
#      oldpage.put('{{db-r2}}', 'BOT: Nominating for deletion per [[WP:CSD#R2|CSD]]')
      #Leave a talk-page notice
      talk = pywikibot.Page(site, 'User talk:' + creator)
      notice = '{{subst:User:Legobot/userfy move|1=%s|2=%s}} ~~~~' %(old, new)
      existing = talk.get()
      talk.put(existing+notice, 'Bot moved [[%s]] to [[%s]]' %(old, new), minorEdit=False)
    else:
      print 'Skipping %s' %page.title(asLink=True)
      continue

if __name__ == "__main__":
  main()

  