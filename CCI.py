#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Legoktm

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
import re
import difflib
TABLE = re.compile(r'(?ims)^{\|.*?^\|}|<table>.*?</table>')
TITLE = re.compile('\* \[\[:(.*?)\]\]:')
DIF = re.compile('\{\{dif\|(\d*?)\|\(\+\d*?\)\}\}')
import pywikibot
from pywikibot.data import api

enwp = pywikibot.Site('en', 'wikipedia')

def fetch_content(title, revid):
    print 'Fetching https://en.wikipedia.org/?diff=' + str(revid)
    #action=query&prop=revisions&titles=Boxing%20at%20the%201992%20Summer%20Olympics&rvprop=content&rvstartid=34348314&rvlimit=2&format=jsonfm
    params = {'action': 'query',
              'prop': 'revisions',
              'titles': title,
              'rvprop': 'content',
              'rvstartid': revid,
              'rvlimit': 2,
              }
    req = api.Request(site=enwp, **params)
    data = req.submit()
    data = data['query']['pages'].values()[0]
    if not 'revisions' in data:
        return {'old': 'a', 'new': 'b'}
    d = {}
    try:
        d['new'] = data['revisions'][0]['*']
    except KeyError:
        #revdel
        print 'Revdel\'d. Or something.'
        d['new'] = 'aksdjfhskdfhd'  # lol
    if len(data['revisions']) == 2:
        try:
            d['old'] = data['revisions'][1]['*']
        except KeyError:
            print 'Revdel\'d. Or something.'
            d['old'] = 'lol'  # sbm
    else:
        d['old'] = ''
    return d

def are_different(old, new):
    #Returns True if different, False if the same
    if not old and new:
        return True
    old = TABLE.sub('', old)
    #print old
    new = TABLE.sub('', new)
    #print new
    #print '---'
    for line in difflib.ndiff(old.splitlines(), new.splitlines()):
        if line.startswith(' '):
            continue
        elif line[1:].isspace():
            continue
        return True
    #print '---'
    return False

def parse_cci_page(page):
    newtext = text = page.get()
    for line in text.splitlines():
        if line.startswith('**') or not line.startswith('* '):
            continue
        if '{{n}}' in line.lower() or '{{y}}' in line.lower():
            #already checked
            continue
        title = TITLE.search(line).group(1)
        print title
        p = pywikibot.Page(enwp, title)
        if p.isRedirectPage():
            title = p.getRedirectTarget().title()
        to_remove = list()
        checked = 0
        for revid in DIF.finditer(line):
            checked += 1
            r = revid.group(1)
            c = fetch_content(title, r)
            if not are_different(c['old'], c['new']):
                print 'These diffs are exactly the same.'
                to_remove.append(r)
        if to_remove:
            if len(to_remove) == checked:
                #we removed all the diffs, just remove the entire line
                newtext = newtext.replace(line+'\n', '')
            else:
                for r in to_remove:
                    newtext = re.sub('\{\{dif\|%s\|\(\+\d*?\)\}\}' % r, '', newtext)
    page.put(newtext, 'Bot: Removing diffs that only edited tables.')



def test():
    c = fetch_content("1999 World Championships in Athletics – Women's hammer throw", 274257091)
    print are_different(c['old'], c['new'])
    c = fetch_content("Mexico at the 1988 Summer Olympics", 38004542)
    print are_different(c['old'], c['new'])

def main():
    pg = pywikibot.Page(enwp, 'Wikipedia:Contributor copyright investigations/Darius Dhlomo 9')
    parse_cci_page(pg)

main()