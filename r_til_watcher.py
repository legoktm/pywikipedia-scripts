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

import requests
import simplejson
import pywikibot


def fetch_reddit(subreddit='todayilearned'):
    url = 'http://reddit.com/r/%s/.json' % subreddit
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    json = simplejson.loads(r.text)
    return json


def filter_links(json):
    data = json['data']['children']
    links = []
    for link in data:
        d = link['data']
        if d['domain'] in ['en.wikipedia.org', 'wikipedia.org', 'en.m.wikipedia.org']:
            links.append(d['url'])
    return links


def build_table(links):
    text = '{{/Header}}\n'
    for link in links:
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
        name = name.replace('%20', ' ')
        name = name.replace('_', ' ')
        text += '*[[:%s]]\n' % name
        print 'Adding [[:%s]]' % name
    return text


def main():
    json = fetch_reddit()
    links = filter_links(json)
    table = build_table(links)
    report_page = pywikibot.Page(
        pywikibot.Site(), 'User:Legobot/Todayilearned')
    summary = 'Bot: Updating list of articles on front page of r/todayilearned'
    report_page.put(table, summary)

if __name__ == "__main__":
    main()
