#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2012 Legoktm, Earwig

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
Checks the recently moved pages list to see
if they were messed up AFC moves. If so, log them at [[Wikipedia:Articles for creation/Wrongly moved submissions]]
"""

import pywikibot
import pywikibot.data.api
import datetime
import legobot
task = legobot.Task(13, 'Legobot')
task.begin()
site = pywikibot.getSite()


def MovedPagesGenerator(ts, old_ts):
    request = pywikibot.data.api.ListGenerator(site=site, listaction='logevents', letype='move', lestart=ts, leend=old_ts)
    for item in request:
        yield {'old': item['title'], 'new': item['move']['new_title'], 'user': item['user']}


def create_timestamp(old=False):
    now = datetime.datetime.utcnow()
    if old:
        now -= datetime.timedelta(hours=1)
    return now.strftime('%Y-%m-%dT%H:00:00Z')


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
        if old.startswith('Wikipedia talk:Articles for creation/'):
            if new.startswith('Wikipedia talk:') and not new.startswith('Wikipedia talk:Articles for creation/'):
                log = True
        if old.startswith('Wikipedia:Articles for creation/'):
            if new.startswith('Wikipedia:') and not new.startswith('Wikipedia:Articles for creation/'):
                log = True
        if not log:
            try:
                print u'Skipping %s --> %s' % (old, new)
            except UnicodeEncodeError:
                pass
            continue
        print u'Will log %s --> %s' % (old, new)
        logtext += u'* [[%s]] --> [[%s]] by [[User:%s|]]\n' % (old, new, user)
    if not logtext:
        print u'Nothing was detected, won\'t update the log.'
        return
    p = pywikibot.Page(
        site, u'Wikipedia:Articles for creation/Wrongly moved submissions')
    current_text = p.get()
    newtext = current_text + '\n' + logtext
    p.put(newtext, u'BOT: Updating log')


if __name__ == "__main__":
    main()
