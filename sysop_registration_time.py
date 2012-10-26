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

CONTENT =''
import urllib
import datetime
import requests
UA = {'User-Agent':'User:Legobot'}
import pywikibot
site = pywikibot.Site()
def main():
    total = 0
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    zero = 0
    six = 0
    seven = 0
    eight = 0
    nine = 0
    ten = 0
    tw = 0
    ele = 0
    error = 0
    for user in site.allusers(group='sysop'):
        #print user
        if user['name'] in RENAMES.keys():
            user['name'] = RENAMES[user['name']]
        registration = user['registration']
        if not registration:
            error += 1
            continue
        elif not user['name']:
            error +=1
            continue
        reg = pywikibot.Timestamp.fromISOformat(registration)
        actual, stamp = fetch_actual(user['name'])
        if not actual:
            error +=1
            continue
        admin = pywikibot.Timestamp.fromISOformat(actual)
        if admin - reg > datetime.timedelta(days=12*365):
            tw += 1
        elif admin - reg > datetime.timedelta(days=11*365):
            ele += 1
        elif admin - reg > datetime.timedelta(days=10*365):
            ten += 1
        elif admin - reg > datetime.timedelta(days=9*365):
            nine += 1
        elif admin - reg > datetime.timedelta(days=8*365):
            eight += 1
        elif admin - reg > datetime.timedelta(days=7*365):
            seven += 1
        elif admin - reg > datetime.timedelta(days=6*365):
            six += 1
        elif admin - reg > datetime.timedelta(days=5*365):
            five += 1
        elif admin - reg > datetime.timedelta(days=4*365):
            four += 1
        elif admin - reg > datetime.timedelta(days=3*365):
            three += 1
        elif admin - reg > datetime.timedelta(days=2*365):
            two += 1
        elif admin - reg > datetime.timedelta(days=1*365):
            one += 1
        else:
            zero += 1
            print user['name']
            print stamp
            print user['registration']

        total += 1

    print 'Total: '+str(total)
    print '<1 year: '+str(zero)
    print '1 year: '+str(one)
    print '2 years: '+str(two)
    print '3 years: '+str(three)
    print '4 years: '+str(four)
    print '5 years: '+str(five)
    print '6 years: '+str(six)
    print '7 years: '+str(seven)
    print '8 years: '+str(eight)
    print '9 years: '+str(nine)
    print '10 years: '+str(ten)
    print '11: '+str(ele)
    print '12: '+str(tw)

    print 'Errors: '+str(error)


def fetch_actual(username):
    try:
        uname = urllib.quote_plus(username)
    except:
        #print 'Nothing found for %s' % username
        return False, None
    url = 'https://en.wikipedia.org/w/api.php?action=query&list=logevents&letype=rights&letitle=User:%s&format=json' % uname
    r = requests.get(url, headers=UA)
    for event in r.json['query']['logevents']:
        try:
            rights = event['rights']
        except KeyError:
            if '+sysop' in event['comment']:
                return event['timestamp'], event['timestamp']
            continue
        if ('sysop' in rights['new']) and not ('sysop' in rights['old']):
            return event['timestamp'], event['timestamp']
    #print 'Nothing found for %s' % username
    return False, None



#fetch_actual('Dennis Brown')

RENAMES = {
    'A Train':'Fernando Rizo',
    'Aaron Schulz':'Voice of All(MTG)',
    'Academic Challenger':None,
    'Adam Bishop':None,
    'Ahoerstemeier':None,
    'AlainV':None,
}

main()