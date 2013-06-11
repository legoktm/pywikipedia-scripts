#!/usr/bin/env python
# -*- coding: utf-8  -*-
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

"""
This script is a clone of [[en:User:SmackBot]]
Syntax: python datebot.py
"""

import os
import re
import datetime

import pywikibot
from pywikibot import pagegenerators

# Define global constants
logfile = "datebot-errors.log"
site=pywikibot.getSite()

def checktalk():
    page = pywikibot.Page(site,'User:Legobot/Stop')
    try:
        wikitext = page.get()
    except:
        raise Exception, "Error: Cannot acess stop page"
    if wikitext.lower() != 'run':
        raise Exception, "Error: Runpage disabled"
def log_error(page,disp_only=False):
    """
    Logging an error on a page due to any reason
    page should be the wiki.Page object
    disp_only should be true when only wanting to view the list, not add anything to it.
        Then page should be just set to 0 (ex use: log_error(page=0,disp_only=True) )
    """
    try:
        if not disp_only:
            print 'Logging error on ' + page.title()
            if os.path.isfile(logfile):
                f1 = open(logfile, 'r')
                old = f1.read()
                f1.close()
            else:
                old = ""
            new = old + '\n' + page.title(asLink=True)
            f2 = open(logfile, 'w')
            f2.write(new)
            f2.close()
        else:
            if os.path.isfile(logfile):
                f1 = open(logfile, 'r')
                txt = f1.read()
                f1.close()
            else:
                txt = "Log is non-existent."    
            print txt
    except UnicodeEncodeError:
        return #fail silently
    except UnicodeDecodeError:
        return #fail silently
def process_article(page):
    month_name = datetime.datetime.utcnow().strftime('%B')
    year = str(datetime.datetime.utcnow().year)
    try:
        wikitext = state1 = page.get()
    except pywikibot.exceptions.IsRedirectPage:
        log_error(page)
        return
    # Fix Casing (Reduces the number of possible expressions)
    wikitext = re.compile(r'\{\{\s*(template:|)fact', re.IGNORECASE).sub(r'{{Citation needed', wikitext)
    # Fix some redirects
    wikitext = re.compile(r'\{\{\s*(template:|)cn\}\}', re.IGNORECASE).sub(r'{{Citation needed}}', wikitext)
    wikitext = re.compile(r'\{\{\s*(template:|)citation needed', re.IGNORECASE).sub(r'{{Citation needed', wikitext)
    wikitext = re.compile(r'\{\{\s*(template:|)proveit', re.IGNORECASE).sub(r'{{Citation needed', wikitext)
    wikitext = re.compile(r'\{\{\s*(template:|)sourceme', re.IGNORECASE).sub(r'{{Citation needed', wikitext)
    wikitext = re.compile(r'\{\{\s*(template:|)fct', re.IGNORECASE).sub(r'{{Citation needed', wikitext)
    # State point.  Count any changes as needing an update if they're after this line
    state0 = wikitext
    
    # Date the tags
    wikitext = re.compile(r'\{\{\s*citation needed\}\}', re.IGNORECASE).sub(r'{{Citation needed|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*wikify\}\}', re.IGNORECASE).sub(r'{{Wikify|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*orphan\}\}', re.IGNORECASE).sub(r'{{Orphan|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*uncategorized\}\}', re.IGNORECASE).sub(r'{{Uncategorized|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*uncatstub\}\}', re.IGNORECASE).sub(r'{{Uncatstub|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*cleanup\}\}', re.IGNORECASE).sub(r'{{Cleanup|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*unreferenced\}\}', re.IGNORECASE).sub(r'{{Unreferenced|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*importance\}\}', re.IGNORECASE).sub(r'{{importance|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*Expand\}\}', re.IGNORECASE).sub(r'{{Expand|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
#    wikitext = re.compile(r'\{\{\s*merge(.*?)\}\}', re.IGNORECASE).sub(r'{{Merge\\1|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*copyedit\}\}', re.IGNORECASE).sub(r'{{Copyedit|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*refimprove\}\}', re.IGNORECASE).sub(r'{{Refimprove|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = re.compile(r'\{\{\s*primary sources\}\}', re.IGNORECASE).sub(r'{{Primary sources|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
    wikitext = wikitext.replace('{{subst:CURRENTMONTHNAME}}', month_name)
    wikitext = wikitext.replace('{{subst:CURRENTYEAR}}', year)
    EditMsg = "[[WP:BOT|BOT]]: Date maintenance tags"
    if state1 != state0:
        EditMsg += " and general fixes"
    EditMsg += '. Is this a mistake? [[User:Legobot/Run|Stop me!]]'
    # If the text has changed at all since the state point, upload it
    if wikitext != state0:
        print 'Editing ' + page.title()
        print 'WRITE:    Adding %s bytes.' % str(len(wikitext)-len(state1))
        try:
            page.put_async(wikitext, EditMsg)
        except:
            log_error(page)
#        except KeyboardInterrupt:
#            quit()
#        except:
#            print 'ERROR:    Except raised while writing.'
    else:
        print 'Skipping ' + page.title() + ' due to no changes made after state point.'

def docat(cat2):
    category = pywikibot.Category(pywikibot.Page(site, 'Category:'+cat2))
    gen = pagegenerators.CategorizedPageGenerator(category)
    for page in gen:
        if page.namespace() == 0:
            try:
                process_article(page)
            except UnicodeEncodeError:
                log_error(page)
                pass
            checktalk()
        else:
            print 'Skipping %s because it is not in the mainspace' %(page.title())
    print 'Done with Category:%s' %(cat2)
def main():
    docat(u"Articles with unsourced statements")
    docat(u"Articles that need to be wikified")
    docat(u"Orphaned articles")
    docat(u"Category needed")
    docat(u"Uncategorized stubs")
    docat(u"Wikipedia cleanup")
    docat(u"Articles lacking sources")
    docat(u"Articles to be expanded")
    docat(u"Articles with topics of unclear notability")
#    docat(u"Articles to be merged")
    docat(u"Wikipedia articles needing copy edit")
    docat(u"Articles needing additional references")
    docat(u"Articles lacking reliable references")
    print 'Done'
    
if __name__ == "__main__":
    main() #run it
    log_error(page=0,disp_only=True) #view error log
