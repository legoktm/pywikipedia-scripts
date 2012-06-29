#!/usr/bin/python
#
# (C) 2012, Legoktm, under the MIT License
# Checks the new pages list to see whether it should have been made in the userspace, and if so, moves it.
#
import sys

import pywikibot
from pywikibot import pagegenerators
site = pywikibot.getSite()



def trial_count():
  try:
    f = open('trial.txt', 'r')
    i = int(f.read())
    f.close()
  except:
    i = 0
  if i == 10:
    print 'Completed trial already! Quitting.'
    sys.exit()
  i += 1
  f = open('trial.txt', 'w')
  f.write(str(i))
  f.close()


def main():
  #get page list
  gen = pagegenerators.NewpagesPageGenerator(total=100)
  for page in gen:
    creator = page.getVersionHistory(reverseOrder=True, total=1)[0][2]
    if page.title().startswith(creator + '/'):
      old = page.title()
      new = 'User:' + page.title()
      #verify that we haven't touched the page yet
      history = page.getVersionHistory()
      for item in history:
        if item[2] == u'Legobot':
          print 'We have already touched %s. Skipping!' %(page.title())
          continue
      trial_count()
      page.move(new, reason='BOT: Moving accidentally created subpage into userspace')
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

  