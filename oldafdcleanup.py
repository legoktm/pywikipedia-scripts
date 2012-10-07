#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import sys
import re
import urllib
import pywikibot
import mwparserfromhell
from pywikibot import pagegenerators
site = pywikibot.Site()
pg = pywikibot.Page(site, 'User:Legobot/Oldafdfull')
gen = pagegenerators.LinkedPageGenerator(pg, content=True)
#gen = pagegenerators.SearchPageGenerator('Oldafdfull', namespaces=[1], total=5000)
MONTH_NAMES    = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = '|'.join(MONTH_NAMES)
TEMP_STRING = '<!-- From Template:Oldafdfull -->'
WTF_STRING = """<!-- From Template:Oldafdfull -->{| class="messagebox standard-talk" style="text-align:center;"
|-
|}"""

def type1(text):
    original = text
    borkens = ['((oldafdfull', '{\n{oldafdfull']
    type1 = False
    for b in borkens:
        if b in text:
            type1 = True
            break
    if type1:
        for item in borkens:
            text = text.replace(item, '{{oldafdfull')
        pywikibot.showDiff(original, text)
        if original != text:
            page.put(text, 'BOT: Fixing broken {{[[Template:oldafdfull|oldafdfull]]}}')
        return
    if not TEMP_STRING in text:
        #print 'no string'
        return
    key = text.find(TEMP_STRING) #+ len(TEMP_STRING)
    text_abbr = text[key:]
    final = text_abbr.find('|}') + 2
    template = text_abbr[:final]
    #key = text.find("{| class=\"messagebox standard-talk\"")
    #text_abbr = text[key:]
    #final = text_abbr.find('|}') + 2
    #template = text_abbr[:final]
    #if text[key+final:].startswith(TEMP_STRING):
    #    template = text_abbr[:final+len(TEMP_STRING)]
        #print template
        #quit()
    if '{{{date|}' in template:
        return
    elif '{{{date}}}' in template:
        return
    print page
    search = re.search('(\[\[|)(\d\d|\d)(th|st|rd|)(\s|/|-)(\d\d|\d|%s)(\]\]|)(\s|/|-)(\[\[|)(\d\d\d\d)' % MONTH_REGEX, template, re.IGNORECASE)
    if not search:
        search2 = re.search('\{\{\#if\:(.*?)\|(.*?)\|recently\}\}', text, re.IGNORECASE)
        if not search2:
            search3 = re.search('(%s)\s(\d|\d\d)(,|)\s(\d\d\d\d|\d\d)' % MONTH_REGEX, template, re.IGNORECASE)
            if not search3:
                search4 = re.search('(\[\[|)(%s)(\s|)(\d\d|\d|)(\]\]|)(,|) (\[\[|)(\d\d\d\d|\d\d)(\]\]|)' % MONTH_REGEX, template, re.IGNORECASE)
                if not search4:
                    search5 = re.search('(\d\d\d\d|\d\d)(\s|-|/)(\d\d|\d|%s)(\s|-|/)(\d\d|\d)' % MONTH_REGEX, template, re.IGNORECASE)
                    if not search5:
                        search6 = re.search('(\[\[|)(\d\d|\d)\s(%s)(\]\]|)(,|)\s(\[\[|)(\d\d\d\d)(\]\]|)' % MONTH_REGEX, template, re.IGNORECASE)
                        if not search6:
                            if template.strip() == '<':
                                return
                            print template
                            #d_string = raw_input('What is the date? ')
                            #return
                            #if d_string == 's':
                            #    return
                            #elif d_string == 'q':
                            if WTF_STRING in text:
                                return
                            print 'no date'
                        else:
                            d_string = search6.group(0)
                    else:
                        d_string = search5.group(0)
                else:
                    d_string = search4.group(0)
            else:
                d_string = search3.group(0)
        else:
            d_string = search2.group(1)
    else:
        day=int(search.group(2))
        month=search.group(5)
        if not month.title() in MONTH_NAMES:
            try:
                month=MONTH_NAMES[int(month)-1]
            except IndexError:
                try:
                    old_month = month
                    month=MONTH_NAMES[int(day)-1]
                    day=int(old_month)
                except IndexError:
                    print 'bad date'
                    return
        year=int(search.group(9))
        d_string = '%s %s %s' % (year, month, day)
    s2 = re.search("\[\[Wikipedia\:(Articles|Votes)[ _]for[ _]deletion/(.*?)(\||\]\])", template, re.IGNORECASE)
    if not s2:
        s2_v1 = re.search("\{\{votepage\|(.*?)\}\}", text, re.IGNORECASE)
        if not s2_v1:
            print 'no link'
            return
        else:
            link = urllib.unquote(s2_v1.group(1))
    else:
        link = urllib.unquote(s2.group(2))
    if link == '{{{votepage|{{PAGENAME}}}}}':
        link = '{{subst:PAGENAME}}'
    elif link == '{{PAGENAME}}':
        link = '{{subst:PAGENAME}}'
    elif link == '{{PAGENAME':
        link = '{{subst:PAGENAME}}'

    s3 = re.search("'''(.*?)'''", template)
    if not s3:
        s3_v1 = re.search('discussion\]\] was (.*?)\.', template, re.IGNORECASE)
        if not s3_v1:
            print 'no result'
            return
        else:
            result = s3_v1.group(1)
            print result
    else:
        result = s3.group(0)
    new_template = "{{oldafdfull|date=%s|result=%s|page=%s}}" % (d_string, result, link)
    newtext = text.replace(template, new_template)
    newtext = newtext.replace('<!-- From Template:Oldafdfull -->','')
    #pywikibot.showDiff(text, newtext)
    return newtext
pywikibot.handleArgs()
for page in gen:
    while page.isRedirectPage():
        page = page.getRedirectTarget()
    if not page.exists():
        continue
    #print page.title(asLink=True)
    newtext = text = page.get()
    savetext = False
    #try:
    while newtext:
        newtext = type1(newtext)
        if newtext:
            savetext = newtext
    if savetext:
        pywikibot.showDiff(text, savetext)
        page.put(savetext, 'BOT: un-substituting {{[[Template:oldafdfull|oldafdfull]]}}')
        #quit()
    #except:
    #    print 'Error on %s' % page.title(asLink=True)
