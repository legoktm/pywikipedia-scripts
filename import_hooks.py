#!/usr/bin/env python3


import functools
import glob
import json
import pywikibot
import os
import sys

site = pywikibot.Site('mediawiki', 'mediawiki')
wd = site.data_repository()
if len(sys.argv) > 1:
    resume = sys.argv[1]
else:
    resume = ''


extensions = glob.glob(os.path.expanduser('~/projects/vagrant/mediawiki/extensions/*/extension.json'))


@functools.lru_cache()
def hook_item(name):
    hp = pywikibot.Page(site, 'Manual:Hooks/' + name)
    if hp.exists():
        try:
            item = pywikibot.ItemPage.fromPage(hp)
        except pywikibot.NoPage:
            return None
        return item

    return None

for extension in sorted(extensions):
    with open(extension) as f:
        data = json.load(f)
    name = data['name']
    if name < resume:
        print('Skipping %s' % name)
        continue
    print('Processing %s...' % name)
    if 'url' in data and data['url'].startswith('https://www.mediawiki.org/wiki/Extension:'):
        pg_name = data['url'].split('Extension:')[1]
    else:
        pg_name = name
    pg = pywikibot.Page(site, 'Extension:' + pg_name)
    if not pg.exists():
        print('Cannot find page for %s' % name)
        continue
    if pg.isRedirectPage():
        print('Following redirect... %s -> %s' % (pg.title(), pg.getRedirectTarget().title()))
        pg = pg.getRedirectTarget()
    try:
        item = pywikibot.ItemPage.fromPage(pg)
    except pywikibot.NoPage:
        print('No Wikidata item for page. Skipping')
        continue
    if 'Hooks' not in data:
        print('No hooks in %s' % name)
        continue
    hooks = list(data['Hooks'])
    item.get()
    if 'P2377' in item.claims:
        for claim in item.claims['P2377']:
            target = claim.getTarget()
            label = target.get()['labels']['en']
            label = label.split('/')[-1]
            if label in hooks:
                print('Skipping %s, already on item' % label)
                hooks.remove(label)
    for hook in hooks:
        hi = hook_item(hook)
        if hi:
            c = pywikibot.Claim(wd, 'P2377')
            c.setTarget(hi)
            print('Adding claim to %s (%s): %s --> %s (%s)' %(name, item.getID(), c.getID(), hook, hi.getID()))
            item.addClaim(c)
    print('Done!')
