#!/usr/bin/env python
from __future__ import unicode_literals

import pywikibot
import mwparserfromhell


def player(name):
    print name
    text = name.get()
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.lower() == 'Infobox MLB player'.lower():
            if not template.has_param('team'):
                return 'retired'
            if not template.has_param('statyear'):
                return 'retired'
            return template.get('statyear').value.strip()
    return 'retired'

def main():
    site = pywikibot.Site()
    temp = pywikibot.Page(site, 'Template:Infobox MLB player')
    gen = pywikibot.pagegenerators.ReferringPageGenerator(temp, onlyTemplateInclusion = True, content = True, total=10000)
    master_text = """{| class="sortable"
|-
! name
! date
|-"""
    for page in gen:
        time = player(page)
        if time == 'retired':
            continue
        text = "\n|%s\n|%s\n|-" % (page.title(asLink=True), time)
        print text
        master_text += text
    master_text += '\n|}'
    pg = pywikibot.Page(site, 'User:Legobot/Baseball')
    #print master_text
    pg.put(master_text, 'Bot: Updating list')

if __name__ == "__main__":
    main()