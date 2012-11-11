#!/usr/bin/env python
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

Code partially borrowed from afcmove.py
"""
import datetime

import pywikibot
site = pywikibot.Site()

def MovedPagesGenerator(ts, old_ts):
    request = pywikibot.data.api.ListGenerator(site=site, listaction='logevents', letype='move', lestart=ts, leend=old_ts, lelimit='max')
    for item in request:
        if item['ns'] == 0:
            yield {'old': item['title'], 'new': item['move']['new_title'], 'user': item['user'], 'comment':item['comment']}


def SubPageGenerator(name):
    request = pywikibot.data.api.ListGenerator(site=site, listaction='allpages', apprefix=name, apnamespace=1, aplimit='max')
    return [item['title'] for item in request]

def create_timestamp(old=False):
    now = datetime.datetime.utcnow()
    if old:
        now -= datetime.timedelta(days=1)
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
        cmt = item['comment']
        new_page = pywikibot.Page(site, new)
        if not new_page.toggleTalkPage().exists(): #skip if no talkpage exists
            continue
        subpages = SubPageGenerator(new+'/') #skip if no subpages
        if not subpages:
            continue
        summary = "Bot: Finishing move by [[User:%s]] (%s)" % (user, cmt)
        done = []
        for pg in subpages:
            wk_pg = pywikibot.Page(site, pg)
            if wk_pg.toggleTalkPage().exists(): #has a mainsapce page, therefore a false positive
                continue
            n_title = pg.replace(old, new)
            wk_pg.move(n_title, summary)
            done.append([pg, n_title])
        print u'Will log %s --> %s' % (old, new)
        logtext += u'* [[%s]] --> [[%s]] by [[User:%s|]]\n' % (old, new, user)
        for i in done:
            logtext += u'** [[%s]] --> [[%s]] finished by [[User:Legobot|]]\n' % (i[0], i[1])
    if not logtext:
        print u'Nothing was moved, won\'t update the log.'
        return
    p = pywikibot.Page(
        site, u'User:TAP Bot/Logs')
    current_text = p.get()
    newtext = current_text + '\n' + logtext
    p.put(newtext, u'BOT: Updating log')
