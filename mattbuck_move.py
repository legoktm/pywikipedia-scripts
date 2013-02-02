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
import pywikibot
import requests
import re
import csv
import mw
site = pywikibot.Site('commons','commons')
summary = 'Correcting numbering issues on behalf of [[User:mattbuck|mattbuck]]'
errors = list()
commons = mw.Wiki('http://commons.wikimedia.org/w/api.php')
#https://en.wikipedia.org/w/api.php?action=query&prop=info&intoken=move&titles=File:Wiki.png&format=jsonfm
import settings
commons.login(settings.username, settings.password)
params={'action':'query','prop':'info','intoken':'move','titles':'File:Wiki.png'}
x=commons.request(params)
key = x['query']['pages'].keys()[0]
MOVETOKEN = x['query']['pages'][key]['movetoken']
print MOVETOKEN

def move(original, target):
    params = {'action':'move',
              'from':original,
              'to':target,
              'reason':summary,
              'movetalk':'1',
              'noredirect':'1',
              'token':MOVETOKEN
    }
    x=commons.request(params, post=True)
    print x

def get_check_usage(file):
    print 'checking usage'
    url='http://toolserver.org/~daniel/WikiSense/CheckUsage.php'
    params = {'i':file,'w':'_100000','go':'Check Usage','r':'on', 'b':'0'}
    r=requests.get(url, params=params)
    if not r.ok:
        return False, r.text
    text=r.text
    data={None:[]}
    wiki=None
    for line in text.splitlines():
        if line.startswith('['):
            wiki=line[1:].split('\t')[0][:-1].strip() #lol
            data[wiki] = []
            continue
        image=line.split('\t')[0]
        data[wiki].append(image)
    return data


def gen():
    with open('filemoves.csv','r') as f:
        reader = csv.reader(f)
        for row in reader:
            yield row

class Move:
    def __init__(self):
        self.t=''
    def run(self):
        for row in gen():
            original = 'File:'+row[0]
            target = 'File:'+row[1]
            data=get_check_usage(row[0])
            #fmt
            self.t+="=\n[[:{0}]]\n".format(original)
            for s in data.keys():
                self.t+='=={0}==\n'.format(s)
                for val in data[s]:
                    self.t+='*[[:{0}]]\n'.format(val)
            print '{0} --> {1}'.format(original, target)
            #try:
            move(original, target)
            #except:
            #    print 'didnt work.'
            #    errors.append(row)
    def finish(self):
        with open('usage.txt','w') as f:
            f.write(t)
        print 'done with usage'

        with open('errors.txt','w') as f:
            f.write('\n'.join(errors))
        print 'done!'

try:
    bot=Move()
    bot.run()
finally:
    bot.finish()


