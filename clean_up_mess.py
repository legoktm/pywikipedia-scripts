#!/usr/bin/env python

import pywikibot
from pywikibot.data import api

site = pywikibot.Site()

reason = '[[WP:CSD#U2|U2]]: Userpage or subpage of a nonexistent user'


def user_does_not_exist(name):
    req = api.Request(action='query', list='users', ususers=name)
    data = req.submit()
    return 'missing' in data['query']['users'][0]

countok = 0
countbad = 0

gen = site.newpages(showBot=True, namespaces=[3], returndict=True, user='EdwardsBot')
for page, pagedict in gen:
    username = page.title(withNamespace=False)
    if user_does_not_exist(username):
        print page
        page.delete(reason, prompt=False)
        countbad += 1
    else:
        countok += 1

print 'BAD: {0}'.format(countbad)
print 'OK: {0}'.format(countok)
