#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# (C) Legoktm 2008-2009, rewritten in 2012 for the rewrite branch
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
