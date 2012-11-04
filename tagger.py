#!/usr/bin/env python
from __future__ import unicode_literals
# A comprehensive and full-fledged WikiProject tagger.
# (C) 2012, Legoktm under the MIT License

"""
Process: (adapted from [[User:Xenobot Mk V/process]])

Four levels of tagging:

"simple": Tag with WikiProject. Nothing else is done.

"inherit": Tag with WikiProject, inherit class if they all agree. Don't assess on a conflict.

"conservative": Tag with WikiProject, only assess if more than one rating is available, and they all agree.

"liberal": Tag with WikiProject, assess using the most used rating, or higher one if a tie
"""

"""
Input fields:

Category to operate on (non-recursive)
WP Tag to add in format of 'WikiProject Biography'
Level of tagging
"""
import sys
import time
import operator
try:
    import couchdb
    couchdb = False #ignore it
except ImportError:
    couchdb = False

import pywikibot
from pywikibot import pagegenerators
import mwparserfromhell
import robot

class TaggerBot(robot.Robot):
    def __init__(self, template):
        robot.Robot.__init__(self, task=7)
        self.errorlist = list()
        self.successlist = list()
        self.template = template
        self.level = 'liberal'
        self.markauto = True
        self.checkPage = pywikibot.Page(self.site, 'User:Legobot/Tagger/Run')
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/Tagger/%s' % self.template))
        if couchdb:
            self.couch = couchdb.Server()
            if not self.couch.__contains__('Projects'):
                self.db = self.couch.create('WPTagger')
            else:
                self.db = self.couch['WPTagger']



    def pause(self):
        #run this before making an edit
        content = self.checkPage.get().strip().lower()
        while content != 'go':
            if content == 'kill':
                self.kill()
            time.sleep(300)
            content = self.checkPage.get().strip().lower()
    
    def kill(self):
        self.checkPage.put('killed', 'Bot: Killing WP-Tagger.')
        sys.exit(0)

    def init(self):
        """
        Code block of stuff that needs to be done before bot can run
        """
        c = mwparserfromhell.parse('{{tlx|1=%s|2=class=}}' % self.template)
        if self.markauto:
            c.filter_templates()[0].add('3', 'auto=yes')
        self.output("""* Starting WikiProject run for [[Wikipedia:%s]]
* Resolution level: %s
* Applying template: %s\n""" % (self.template, self.level, unicode(c)))
        self.load_stub_templates()
        #fetch template redirects
        t_p = pywikibot.Page(self.site, 'Template:'+self.template)
        self.redirects = [page.title(withNamespace=False).lower() for page in t_p.getReferences(redirectsOnly=True)]


    def run(self):
        factory = pagegenerators.GeneratorFactory()
        for arg in pywikibot.handleArgs():
            factory.handleArg(arg)
        gen = factory.getCombinedGenerator()
        for page in gen:
            if not page.isTalkPage():
                page = page.toggleTalkPage()
            self.tag_page(page)
    
    def tag_page(self, page):
        if page.isRedirectPage():
            self.errorlist.append(page)
            return
        if not page.exists():
            text = ""
        else:
            text = page.get()
        code = mwparserfromhell.parse(text)
        append=False
        has_shell = False #has the WPBS or others
        shell_name = None
        shells = ['WPBS','WikiProjectBannerShell','WikiProjectBanners','WPB']
        for t in code.filter_templates(recursive=True):
            #expand redirects
            if t.name.startswith('#'):
                continue
            if t.name in shells:
                has_shell = True
                shell_name = t.name
                continue
            if t.name.lower().strip() in self.redirects:
                t.name = self.template
            if t.name.lower().strip() == self.template.lower():
                if t.has_param('class') or (self.level == 'simple'):
                    self.errorlist.append(page)
                    self.output('* Skipping [[:%s]], already assessed.' % page.title())
                    return
                else:
                    append=True
                    t.name = self.template
        #ok lets tag the page
        if self.level != 'simple':
            clas = self.determineClass(code, page)
        else:
            clas = None
        if clas:
            std_class = self.standardizeClass(clas)
        else:
            std_class = 'Unknown'
        if append and clas:
            for template in code.filter_templates(recursive=True):
                if template.name == self.template:
                    if template.has_param('class',ignore_empty=False):
                        template.get('class').value = std_class
                    else:
                        template.add('class', std_class)
                    if self.markauto:
                        template.add('auto', 'yes')
                    break
            #pywikibot.showDiff(text, unicode(code))
            self.output('* [[%s]] --> "%s-class"' % (page.title(), std_class))
            page.put(unicode(code), 'Bot: Auto-assessing a class of "%s-class"' % std_class)
            return True
        if append and not clas:
            self.output('* Unable to parse a class from [[:%s]]' % page.title())
            return
        TEMP = mwparserfromhell.parse('{{%s}}' % self.template)
        if clas:
            TEMP.filter_templates()[0].add('class', clas)
            if self.markauto:
                TEMP.filter_templates()[0].add('auto', 'yes')
        if has_shell: #shell yes, no class
            for template in code.filter_templates():
                if template.name == shell_name:
                    current = unicode(template.get(1).value)
                    current += '\n'+unicode(TEMP)
                    template.get(1).value = current.strip()
                    break
        else:
            index = 0
            splitlines = text.splitlines()
            for line in splitlines:
                if line.strip().startswith('=='):
                    index = splitlines.index(line)
                    break
            newlines = splitlines[:index-1]
            newlines.append(unicode(TEMP))
            newlines.extend(splitlines[index:])
            code = '\n'.join(newlines)
        if clas:
            summary = 'Bot: Auto-assessing using "%s"' % unicode(TEMP)
        else:
            summary = 'Bot: Auto-tagging with {{%s}}' % self.template
        #pywikibot.showDiff(text, unicode(code))
        page.put(unicode(code), summary)
        self.output('* [[:%s]] --> "%s-class"' % (page.title(), std_class))
        return True

        
    
    def standardizeClass(self, value):
        value = value.lower().strip()
        d={
           'fa':'FA',
           'a':'A',
           'ga':'GA',
           'b':'B',
           'c':'C',
           'stub':'Stub',
           'start':'Start',
           'list':'List',
           'disambig':'Disambig',
           'portal':'Portal',
           'template':'Template',
           'redirect':'Redirect',
           'category':'Category',
           'cat':'Category',
        }
        return d[value]
    
    def valueClass(self, value):
        value = value.lower().strip()
        d = {
             'fa':10,
             'a':9,
             'ga':8,
             'b':7,
             'c':6,
             'list':5,
             'stub':4,
             'start':3,
             'disambig':2,
             'portal':1,
             'template':0,
             'redirect':-1,
             'category':-2,
        }
        if not d.has_key(value):
            print 'ERROR MISSING %s-class' % value
            return 0
        return d[value]

    def determineClass(self, code, page):
        if page.toggleTalkPage().isRedirectPage():
            return 'redirect'
        if page.namespace() == 101:
            return 'portal'
        elif page.namespace() == 15:
            return 'category'
        elif page.namespace() == 11:
            return 'template'


        if self.level == 'simple':
            return None
        found = list()
        stub = False
        code = mwparserfromhell.parse(pywikibot.removeDisabledParts(unicode(code))) #wtf
        for template in code.filter_templates(recursive=True):
            if template.has_param('class'):
                found.append(template.get('class').value.strip())
            if (template.name.lower() in self.stub_templates) and (not stub):
                stub = True
        #check for auto=stub

        if not found:
            if stub:
                return 'stub'
            return None
        if (self.level == 'conservative') and (len(found) == 1):
            if stub:
                return 'stub'
            return None
        if found.count(found[0]) == len(found): #verifies that all values are equal
            return found[0]
        if self.level in ['inherit', 'conservative']:
            if stub:
                return 'stub'
            return None
        #can only be 'liberal'
        d={}
        for value in found:
            value = value.lower().strip()
            if not d.has_key(value):
                d[value] = 1
            else:
                d[value] += 1
        #top = d.keys()[d.values().index(max(d.values()))]
        sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=True)
        top = sorted_d[0][1]
        top_value = sorted_d[0][0]
        key=1
        print sorted_d
        if len(sorted_d) == 1:
            return top_value
        while top == sorted_d[key][1]:
            if self.valueClass(top_value) <= self.valueClass(sorted_d[key][0]):
                top_value = sorted_d[key][0]
            key += 1
            if len(sorted_d) >= key:
                break
        return top_value

    def load_stub_templates(self):
        self.stub_templates = []
        st = pywikibot.Page(self.site, 'Wikipedia:WikiProject Stub sorting/Stub types')
        text = st.get()
        code = mwparserfromhell.parse(text)
        for template in code.filter_templates():
            if template.name.startswith('Wikipedia:WikiProject Stub sorting/Stub types/'):
                st_page = pywikibot.Page(self.site, unicode(template.name))
                text = st_page.get()
                code = mwparserfromhell.parse(text)
                for template in code.filter_templates():
                    if template.name.lower() == 'tl':
                        self.stub_templates.append(unicode(template.get(1).value).lower())


            
        
if __name__ == "__main__":
    bot = TaggerBot(raw_input("What template would you like to add? No Template: prefix. "))
    try:
        bot.run()
    finally:
        #pass
        bot.pushLog()
