#!/usr/bin/env python

# (C) Legoktm, 2012 under the MIT License
"""
Code state: alpha
Goal: A comprehensive helper script for User:Legobot
Built on top of the pywikibot framework
Current Requirements:
    Configuration page set up at 'User:Legobot/Configuration'
    pywikibot-rewrite framework installed
Currently supports:
    An on-wiki configuration subpage.
    
Usage:
import pywikibot
import robot
class TaskRobot(robot.Robot):
    def __init__(self):
       robot.Robot.__init__(self, task=1)
    def run(self):
        page = pywikibot.Page(self.site, 'Wikipedia:Sandbox')
        text = 'This is a test'
        msg = 'BOT: Edit summary'
        self.edit(page, text, msg)
if __name__ == "__main__":
    bot = TaskRobot()
    bot.run()

"""

import sys
import re
import time
import pywikibot

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
        self.loggingEnabled = False
    def setAction(self, text):
        self.summary = text
    
    def startLogging(self, logPage):
        self.loggingEnabled = True
        self.logPage = logPage
        self.logText = ''
    
    def pushLog(self, overwrite=False):
        if (not overwrite) and self.logPage.exists():
            old = self.logPage.get()
            self.logText = old + self.logText
        self.logPage.put(self.logText, 'BOT: Updating log')
        self.loggingEnabled = False
        self.logText = ''
        
    def output(self, text):
        #nothing fancy here yet, will be used later to implement better logging
        if self.loggingEnabled:
            self.logText += text
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
        search = re.search('%s: (.*?)\nenable(|d): (true|.*?)\n' % self.task, config)
        if not search:
            self.enabled = False
        else:
            self.enabled = (search.group(3).lower() == 'true')
        return self.enabled
    
    def quit(self):
        #something fancy to go here later
        sys.exit()
    
    
allTasks = ['afcmove', 'baronetcies', 'datebot', 'pui', 'vitalarticles']
#pseudocode
#for task in allTasks:
#    task.run()
