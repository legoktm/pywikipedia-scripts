#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2008-2012 Legoktm

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
import mwparserfromhell
from BeautifulSoup import BeautifulSoup

FIREFOX_HEADERS = {'Content-Length':'0',
                   'Accept-Language':'en-us,en;q=0.5',
                   'Accept-Encoding':'gzip, deflate',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0',
                   'Connection':'keep-alive',
                   'Referer':'http://en.wikipedia.org',
                   }
MONTH_NAMES    = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

CITE_WEB = ['cite web', 'web', 'web reference', 'web-reference', 'weblink', 'c web', 'cit web', 'cita web', 'citar web', 'cite blog', 'cite tweet',
            'cite url,', 'cite web.', 'cite webpage', 'cite website', 'cite website article', 'cite-web', 'citeweb', 'cw', 'lien web',
            'web citation', 'web cite',]
CITE_NEWS = ['cite news', 'cit news', 'cite article', 'citenewsauthor', 'cite new', 'cite news-q', 'cite news2', 'cite newspaper', 'cite-news',
             'citenews', 'cute news']
DEAD_LINK = ['dead link', '404', 'badlink', 'broken link', 'brokenlink', 'dl', 'dead', 'dead cite', 'dead page', 'dead-link',
             'deadcite', 'deadlink', 'link broken', 'linkbroken']
CITE_TEMPLATES = CITE_WEB
CITE_TEMPLATES.extend(CITE_NEWS)


def is_up(url):
    r = requests.get(url, headers=FIREFOX_HEADERS)
    print r.status_code
    if r.status_code == 404:
        return False
    #return str(r.status_code).startswith(('2','3','411')) #should be a 2xx or 3xx response
    return r.ok

def verify_archive(url):
    #<p class="code">Redirecting to...</p>
    r = requests.get(url)
    if not r.ok:
        return False
    if '<p class="code">Redirecting to...</p>' in r.text:
        return False
    return True

def archive_page(url):
    print 'Searching for %s' % url
    ai_url = 'http://wayback.archive.org/web/*/'+url
    r = requests.get(ai_url, headers=FIREFOX_HEADERS)
    if not r.ok:
        return
    soup = BeautifulSoup(r.text)
    tags = soup.findAll("a")
    for t in tags:
        #print t
        if not t.has_key('title'):
            continue
        elif 'snapshot' in t['title']:
            print 'RETURNING %s' % t['href']
            if verify_archive(t['href']):
                print 'Verification was a success.'
                return t['href']
            else:
                print 'Failed to verify archive. Continuing'
                continue
    #webbrowser.open(ai_url)
    #sys.exit(1)



def page_f(pg):
    count = 0
    text = pg.get()
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates(recursive=True):
        if template.name.lower().strip() in CITE_TEMPLATES:
            url = template.get('url').value.strip()
            if 'msnbc.com' in url:
                continue
            isup = is_up(url)
            if isup:
                continue
            if template.has_param('archiveurl'):
                #if template.has_param('deadurl'):
                #    if template.get('deadurl').value.strip() == 'no':
                #        template.remove('deadurl')
                #        template.add('deadurl', 'yes')
                #        continue
                continue
            #find it on archive.org
            ai_url = archive_page(url)
            if not ai_url:
                print 'Not found. :('
                continue
            raw_date = ai_url[27:27+14]
            year = int(raw_date[:4])
            day = int(raw_date[6:8])
            month_num = int(raw_date[4:6])
            month = MONTH_NAMES[month_num-1]
            template.add('archiveurl', ai_url)
            template.add('deadurl', 'yes')
            template.add('archivedate', '%s %s %s' % (day, month, year))
            count += 1

    #lets remove all the {{dead link}} now
    code = unicode(code)
    for tag in re.finditer(r'<ref(.*?)>(.*?)</ref>', code):
        p = mwparserfromhell.parse(tag.group(2))
        for template in p.filter_templates():
            set = False
            if template.name.lower().strip() in CITE_TEMPLATES:
                if template.has_param('archiveurl'):
                    set = True
            elif template.name.lower().strip() in DEAD_LINK:
                if set:
                    del p.nodes[p.nodes.index(unicode(template))]
                    code = code.replace(tag.group(2), unicode(p))
    if text != code:
        print 'No changes made on %s' % pg.title(asLink=True)
        return
    pywikibot.showDiff(text, unicode(code))
    if raw_input('Save?').lower() == 'y':
        pg.put(unicode(code), 'Manually-assisted archive url fetching.')

if __name__ == "__main__":
    s=pywikibot.Site()
    #p=pywikibot.Page(s,'Tyler Thigpen')
    cat = pywikibot.Category(s, 'Category:Articles with dead external links from March 2008')
    for p in cat.articles(namespaces=[0]):
        page_f(p)
