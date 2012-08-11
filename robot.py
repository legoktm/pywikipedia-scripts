#!/usr/bin/env python

# (C) Legoktm, 2012 under the MIT License
#
# Status: pre-alpha
# Goal: Second attempt at building a comprehensive helper script for User:Legobot
# Built on top of the pywikibot framework
#

import sys
import pywikibot
import re

#use pywikibot.config to get username
CONFIGURATION_PAGE = 'User:Legobot/Configuration'
BRFA = 'Wikipedia:Bots/Requests for approval/%s %s'


class Robot:
    
    def __init__(self, task):
        self.site = pywikibot.getSite()
        self.trial = False
        self.trial_counter = 0
        self.trial_max = 0
        self.summary = None
        self.task = task
        self.site = pywikibot.getSite()
    
    def setAction(self, text):
        self.summary = text
    
    def output(self, text):
        #nothing fancy here yet, will be used later to implement better logging
        print text
    
            
        
    def edit(self, page, text, summary=False, async=False, force = False, minorEdit=False):
        if not self.isEnabled() and not force:
            self.output('Run-page is disabled. Quitting.')
            self.quit()
        if not summary:
            summary = self.summary
        if async:
            page.put_async(text, summary, minorEdit=minorEdit)
        else:
            page.put(text, summary, minorEdit=minorEdit)
        if self.trial:
            self.trial_action()
        
    def trial_action(self):
        self.trial_counter += 1
        if self.trial_counter >= self.trial_max:
            print 'Finished trial, quitting now.'
            self.quit()
    
    def start_trial(self, count):
        self.trial = True
        self.trial_max = count
    
    def isEnabled(self):
        if self.task == 0: #override for non-filed tasks
            self.enabled = True
            return self.enabled
        page = pywikibot.Page(self.site, CONFIGURATION_PAGE)
        try:
            config = page.get()
        except pywikibot.exceptions.NoPage:
            self.enabled = False
            return self.enabled
        config = config.lower()
        search = re.search('%s: (.*?)\nenable: (true|.*?)\n' % self.task, config)
        if not search:
            self.enabled = False
        else:
            self.enabled = (search.group(2).lower() == 'true')
        return self.enabled
    
    def quit(self):
        #something fancy to go here later
        sys.exit()
    
    
allTasks = ['afcmove', 'baronetcies', 'datebot', 'pui', 'vitalarticles']
#pseudocode
#for task in allTasks:
#    task.run()
