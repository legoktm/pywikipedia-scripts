#!/usr/bin/env python

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
        if d['domain'] in ['en.wikipedia.org', 'wikipedia.org']:
            links.append(d['url'])
    return links


def build_table(links):
    text = '{{/Header}}\n'
    for link in links:
        if '/wiki/' in link:
            f = link.find('/wiki/')
            name = link[f + 6:]
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
