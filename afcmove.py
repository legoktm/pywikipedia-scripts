#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(C) 2012, Legoktm, under the MIT License
Checks the recently moved pages list to see
if they were messed up AFC moves. If so, log them at [[Wikipedia:Articles for creation/Wrongly moved submissions]]
"""

import pywikibot
import pywikibot.data.api
import datetime
import os
site = pywikibot.getSite()

def MovedPagesGenerator(ts, old_ts):
  request = pywikibot.data.api.ListGenerator(site=site, listaction='logevents',letype='move', lestart=ts, leend=old_ts)
  for item in request:
    yield {'old':item['title'], 'new':item['move']['new_title'], 'user':item['user']}




def create_timestamp(old=False):
  now = datetime.datetime.now()
  if old:
    hour = now.hour-1
  else:
    hour = now.hour
  return '%s-%s-%sT%s:00:00Z' % (now.year, abs_zero(now.month), abs_zero(now.day), abs_zero(hour))

def abs_zero(input):
  if len(str(input)) == 1:
    return '0' + str(input)
  return str(input)

def main():
  #get page list
  ts = create_timestamp()
  old_ts = create_timestamp(old=True)
  gen = MovedPagesGenerator(ts, old_ts)
  logtext = ''
  for item in gen:
    log = False
    old = item['old']
    new = item['new']
    user = item['user']
    if new.startswith('Articles for creation/'):
      log = True
    if old.startswith('Wikipedia talk:Articles for creation/') and new.startswith('Wikipedia talk:'):
      log = True
    if old.startswith('Wikipedia:Articles for creation/') and new.startswith('Wikipedia:'):
      log = True
    if not log:
      try:
        print u'Skipping %s --> %s' % (old, new)
      except UnicodeEncodeError:
        continue
      continue
    print u'Will log %s --> %s' % (old, new)
    logtext += u'* [[%s]] --> [[%s]] by [[User:%s|]]\n' % (old, new, user)
  if logtext == u'':
    print u'Nothing was detected, won\'t update the log.'
    return
  p = pywikibot.Page(site, u'Wikipedia:Articles for creation/Wrongly moved submissions')
  current_text = p.get()
  newtext = current_text + '\n' + logtext
  p.put(newtext, u'BOT: Updating log')
    
    
if __name__ == "__main__":
  main()