#!/usr/bin/env python
from __future__ import unicode_literals
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
import re
import requests
import pywikibot

import robot
import urlregex

API_KEY = 'REMOVED'

class ShortURLBot(robot.Robot):

    def __init__(self):
        robot.Robot.__init__(self, task=24)
        self.match = urlregex.MATCH_URL
        self.key = API_KEY
        self.UA = {'User-agent':'Wikipedia User Bot - http://enwp.org/User:Legobot'}
        self.loggingEnabled(pywikibot.Page(self.site, 'User:Legobot/Logs/24'))
        self.error_file = 'bad_urls.txt'
        self.errors = []

    def expand_url(self, url, page):
        query = 'https://www.googleapis.com/urlshortener/v1/url?shortUrl=%s&key=%s' % (url, self.key)
        r = requests.get(query, headers=self.UA)
        if not r.ok:
            self.log_errors(url, 'UNKNOWN', page)
            return url
        if r.json['status'] != 'OK':
            self.log_errors(url, r.json['status'], page)
            return url
        long_url = r.json['longUrl']
        self.output('* Extracted [%s] on [[:%s]]' % (long_url, page.title))
        return long_url

    def do_page(self, page):
        newtext = text = page.get()
        count = 0
        for match in urlregex.MATCH_URL.finditer(text):
            url = match.group(0)
            if not url.startswith(('https://goo.gl', 'http://goo.gl', 'https://g.co', 'http://g.co')):
                continue
            new_url = self.expand_url(url, page)
            if new_url == url:
                continue
            newtext = newtext.replace(url, new_url)
        if newtext != text:
            page.put(newtext, 'BOT: Expanding short urls (%s)' % count, async=True)

    def run(self):
        for page in self.gen():
            self.do_page(page)


    def gen(self):
        for page in self.site.exturlusage('goo.gl', protocol='http', namespaces=):
            yield page
        for page in self.site.exturlusage('goo.gl', protocol='https'):
            yield page
        for page in self.site.exturlusage('g.co', protocol='http'):
            yield page
        for page in self.site.exturlusage('g.co', protocol='https'):
            yield page

    def log_errors(self, url, type, page):
        string = "<li><b>%s</b>: <a href=\"%s\">Target</a> on <a href=\"%s\">%s</a></li>" %(type, url, page.permalink(), page.title())
        self.errors.append(string)
        print "%s on %s on %s" %(type, url, page.title())

    def save_errors(self):
        all = '\n'.join(self.errors)
        all = '<html><body><ul>' + all + '</ul></body></html>'
        file = open(self.error_file, 'w')


if __name__ == "__main__":
    bot = ShortURLBot
    try:
        bot.run()
    finally:
        bot.save_errors()
        bot.pushLog()