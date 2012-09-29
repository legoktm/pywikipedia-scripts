#!/usr/bin/env python
"""
Copyright (C) 2012 Legoktm

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

from __future__ import unicode_literals

import time
import requests
import simplejson

import pywikibot
import mwparserfromhell

SITE = pywikibot.Site()
def fetch_reddit(subreddit='todayilearned'):
    url = 'http://reddit.com/r/%s/.json' % subreddit
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        return {}
    json = simplejson.loads(r.text)
    return json


def filter_links(json):
    data = json['data']['children']
    links = []
    for link in data:
        d = link['data']
        if d['domain'] in ['en.wikipedia.org', 'wikipedia.org', 'en.m.wikipedia.org']:
            links.append((d['url'], d['created_utc'], d['permalink']))
    return links

def convert_time(secs):
    struct = time.gmtime(secs)
    return time.strftime('%d %B %Y', struct)

def parse_links(links):
    for link, stamp, rlink in links:
        if '/wiki/' in link:
            f = link.find('/wiki/')
            name = link[f + 6:]
            if '?' in name:
                name = name.split('?')[0]
        elif '/index.php' in link:
            f = link.find('title=')
            name = link[f + 6:]
            if '&' in name:
                name = name.split('&')[0]
        else:
            continue
        name = name.split('#')[0]
        name = name.replace('%20', ' ')
        name = name.replace('_', ' ')
        date = convert_time(stamp)
        reddit = 'http://reddit.com' + rlink
        yield name, date, reddit


def main():
    json = fetch_reddit()
    links = filter_links(json)
    gen = parse_links(links)
    for title, date, rlink in gen:
        do_page(title, date, rlink)

def do_page(title, date, rlink):
    """
    @param title: Title of the page
    @param date: String for template
    @param rlink: Reddit permalink
    """
    pg = pywikibot.Page(SITE, title)
    if not pg.exists():
        return
    while pg.isRedirectPage():
        pg = pg.getRedirectTarget()
    if pg.namespace() != 0:
        return
    talk = pg.toggleTalkPage()
    print talk
    text = talk.get()
    summary = 'BOT: Updating {{high traffic}} with reddit post on %s' % date
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.lower() == 'High traffic'.lower():
            count = 1
            s = 'site'
            while template.has_param(s):
                if template.get(s).value == rlink:
                    #already in the template
                    return
                count += 1
                s ='site%s' % count
            if count == 1:
                u = 'url'
                d = 'date'
            else:
                u = 'url%s' % count
                d = 'date%s' % count
            template.add(s, 'Reddit')
            template.add(u, rlink)
            template.add(d, date)
            pywikibot.showDiff(text, unicode(code))
            talk.put(unicode(code), summary)
            return

    #Doesn't exist already, lets create a new template and insert it in right before the first header
    index = 0
    splitlines = text.splitlines()
    for line in splitlines:
        if line.strip().startswith('=='):
            index = splitlines.index(line)
            break
    newlines = splitlines[:index-1]
    template = '{{High traffic|date=%s|site=Reddit|url=%s}}' % (date, rlink)
    newlines.append(template)
    newlines.extend(splitlines[index:])
    final = '\n'.join(newlines)
    pywikibot.showDiff(text, final)
    talk.put(final, summary)

if __name__ == "__main__":
    main()