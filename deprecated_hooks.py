#!/usr/bin/env python3

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site('mediawiki', 'mediawiki')
wd = site.data_repository()

mw = {
    '1.12.0': 'Q21683747',
    '1.14.0': 'Q21683746',
    '1.16.0': 'Q21683640',
    '1.17.0': 'Q21683638',
    '1.18.0': 'Q21683639',
    '1.19.0': 'Q21683641',
    '1.20.0': 'Q21683642',
    '1.21.0': 'Q21683643',
    '1.22.0': 'Q21683645',
    '1.23.0': 'Q21683646',
    '1.24.0': 'Q21683648',
    '1.25.0': 'Q21683649',
    '1.26.0': 'Q21683659',
    '1.27.0': 'Q21683650',
}

def normalize_version(ver):
    ver = ver.split(' ')[0]
    if len(ver.split('.')) == 2:
        ver += '.0'
    return ver

gen = pagegenerators.PrefixingPageGenerator('Manual:Hooks/', site=site, content=True, includeredirects=False)
for page in gen:
    if len(page.title().split('/')) > 2:
        #print('Skipping %s because it has 2+ subpage parts' % page.title())
        continue

    code = mwparserfromhell.parse(page.text)
    dep = None
    for temp in code.filter_templates():
        if temp.name == 'TNT' and temp.get(1).value.strip() == 'MediaWikiHook':
            if temp.has('deprecated'):
                dep = str(temp.get('deprecated').value).strip()
                break
        elif temp.name == 'TNT' and temp.get(1).value.strip() == 'Deprecated':
            dep = str(temp.get('2').value).strip()

    if dep:
        dep = normalize_version(dep)
        print('%s: %s' % (page.title(), dep))
    else:
        continue
    if dep not in mw:
        print('%s doesnt have a Wikidata item' % dep)
        continue
    item = pywikibot.ItemPage.fromPage(page)
    item.get()
    if 'P2379' in item.claims:
        print('Already marked as deprecated, skipping...')
        continue
    claim = pywikibot.Claim(wd, 'P2379')
    claim.setTarget(pywikibot.ItemPage(wd, mw[dep]))
    item.addClaim(claim)
    print('Added claim!')
