#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(C) 2012, Legoktm, under the MIT License
Checks the recently moved pages list to see
if they were messed up AFC moves. If so, log them at [[Wikipedia:Articles for creation/Wrongly moved submissions]]
"""

import pywikibot
import pywikibot.data.api
site = pywikibot.getSite()

def MovedPagesGenerator(total=100):
  request = pywikibot.data.api.Request(site=site, action='query',list='logevents',letype='move',lelimit=total)
  data = request.submit()
  for item in data['query']['logevents']:
    yield {'old':item['title'], 'new':item['move']['new_title'], 'user':item['user']}

def main():
  #get page list
  gen = MovedPagesGenerator(total=100)
  logtext = ''
  for item in gen:
    log = False
    old = item['old']
    new = item['new']
    user = item['user']
    if old.startswith('Articles for creation/'):
      print 'Will log %s --> %s' % (old, new)
      log = True
    if old.startswith('Wikipedia talk:Articles for creation/') and new.startswith('Wikipedia talk:'):
      print 'Will log %s --> %s' % (old, new)
      log = True
    if old.startswith('Wikipedia:Articles for creation/') and new.startswith('Wikipedia:'):
      print 'Will log %s --> %s' % (old, new)
      log = True
    if not log:
      print 'Skipping %s --> %s' % (old, new)
      continue
    logtext += '* [[%s]] --> [[%s]] by [[User:%s|]]\n' % (old, new, user)
  if logtext == '':
    print 'Nothing was detected, won\'t update the log.'
    return
  p = pywikibot.Page(site, 'Wikipedia:Articles for creation/Wrongly moved submissions')
  current_text = p.get()
  newtext = current_text + logtext
  p.put(newtext, 'BOT: Updating log')
    
    
if __name__ == "__main__":
  main()