#!/usr/bin/python
# -*- coding: utf-8  -*-
#
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
#
import sys
sys.path.append('/home/legoktm/wikipedia/')

import pywikibot
import re

class Robot:
    def __init__(self):
        self.site = pywikibot.getSite()
        self.db = {}
        self.page = pywikibot.Page(self.site, 'Wikipedia:Vital articles')
    
    def pagelist(self):
        gen = self.page.linkedPages(namespaces=0)
        return gen
    def __inlist(self, search, check_list):
        for cat in check_list:
            if search in cat:
                return True
        return False
    def process_page(self, page):
        talk = page.toggleTalkPage()
        #check if FA or GA based on categories....
        cats = page.categories()
        t_cats = talk.categories()
        t_cats_list = []
        for t_cat in t_cats:
            t_cats_list.append(t_cat.title())
        self.db[page.title()] = {}
        self.db[page.title()]['class'] = None
        self.db[page.title()]['other'] = None        
        for cat in cats:
            if 'Featured articles' in cat.title():
                self.db[page.title()]['class'] = 'FA'
                return
            elif 'Good articles' in cat.title():
                self.db[page.title()]['class'] = 'GA'
        if not self.db[page.title()]['class']:
            #Use talk page template detection
            #Automatically assume the highest class possible

            if self.__inlist('B-Class', t_cats_list):
                self.db[page.title()]['class'] = 'B'
            elif self.__inlist('C-Class', t_cats_list):
                self.db[page.title()]['class'] = 'C'
            elif self.__inlist('Start-Class', t_cats_list):
                self.db[page.title()]['class'] = 'Start'
            else: #no class could be found
                self.db[page.title()]['class'] = 'Stub' #assume the lowest class possible
        #Check for a DGA, DFA
        if self.__inlist('Former good article nominees', t_cats_list):
            self.db[page.title()]['other'] = 'DGA'
        if self.__inlist('Wikipedia former featured articles', t_cats_list) or self.__inlist('Wikipedia featured article candidates (contested)', t_cats_list):
            self.db[page.title()]['other'] = 'DFA'
        #done!
        print 'Finished processing %s, it is a %s-class and other is %s.' %(page.title(), self.db[page.title()]['class'], str(self.db[page.title()]['other']))
    
    def update_VA(self):
        state = editted = self.page.get()
        for title in self.db.keys():
            templates = '{{Icon|%s}}' %(self.db[title]['class'])
            if not self.db[title]['other']:
                templates += ' {{Icon|%s}}' %(self.db[title]['other'])
            re.sub('# (.*?) \[\[%s\]\]' %(title), '# %s \[\[%s\]\]' %(templates, title), editted)
        pywikibot.showDiff(state, editted)

        print 'DIFFERENCE: %s' %str(len(editted)-len(state))

        self.page.put(editted, 'Bot: Updating Vital Articles')

    def run(self):
        generator = self.pagelist()
        for page in generator:
            self.process_page(page)
        self.update_VA()

if __name__ == '__main__':
    robot = Robot()
    robot.run()
