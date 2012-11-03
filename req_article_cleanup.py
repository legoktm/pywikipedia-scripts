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
import pywikibot
import mwparserfromhell
import tagger
site = pywikibot.Site()
TagBot = tagger.TaggerBot('WikiProject Requested articles')
TagBot.init()

def gen():
    page = pywikibot.Page(site, 'Wikipedia:Requested articles')
    links = page.linkedPages(namespaces=[4])
    for pg in links:
        if pg.title().startswith('Wikipedia:Requested articles/'):
            yield pg


def parse_page(page):
    print page
    content = page.get()
    lines = content.splitlines()
    delete_these = list()
    for item in lines:
        try:
            if parse_line(item):
                delete_these.append(item)
        except pywikibot.exceptions.InvalidTitle:
            pass
    for l in delete_these:
        del lines[lines.index(l)]
    newtext = '\n'.join(lines)
    pywikibot.showDiff(content, newtext)
    page.put(newtext, 'Bot: removing completed requests. Want to help? Join the [[Wikipedia:WikiProject Requested articles/Backlog Drive|WikiProject Requested articles Backlog Drive]] today!')
    quit()


def parse_line(line):
    if line.isspace():
        return
    elif line.startswith('=='):
        return
    name = None
    code = mwparserfromhell.parse(line)
    for template in code.filter_templates():
        if template.name.lower().strip() == 'req':
            name = template.get(1).value
            break
    if not name:
        #find the first wikilink and check it
        key1 = line.find('[[')
        if key1 == -1:
            #no links???
            return
        p1 = line[key1+2]
        key2 = p1.find(']]')
        if key2 == -1:
            #no ending????
            return
        p2 = p1[:key2]
        name = p2.split('|')[0] #fix piped links
    pg = pywikibot.Page(site, name)
    print pg
    if pg.exists():
        if (not pg.isRedirectPage()) and (not pg.isDisambig()):
            #IT EXISTS
            print pg.title()+' exists!'
            talk = pg.toggleTalkPage()
            TagBot.tag_page(talk)
            return True
    #print pg.title()+' doesn\'t exist :('



if __name__ == "__main__":
    for page in gen():
        parse_page(page)
    #parse_page(pywikibot.Page(site, 'Wikipedia:Requested articles/Applied arts and sciences/Medicine'))
