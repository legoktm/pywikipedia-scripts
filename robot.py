#!/usr/bin/env python

# (C) Legoktm, 2012 under the MIT License
"""
Code state: alpha
Goal: A comprehensive helper script for User:Legobot
Built on top of the pywikibot framework
Current Requirements:
    Configuration page set up at 'User:USERNAME/Configuration'
    pywikibot-rewrite framework installed
Currently supports:
    An on-wiki configuration subpage. (can be set to check every XX amount of edits)
    On-wiki logging
    Local logging
    
Usage:
import pywikibot
import robot
class TaskRobot(robot.Robot):
    def __init__(self):
       robot.Robot.__init__(self, task=1)
       self.startLogging(pywikibot.Page(self.site, 'User:Example/Log'))
    def run(self):
        page = pywikibot.Page(self.site, 'Wikipedia:Sandbox')
        text = 'This is a test'
        msg = 'BOT: Edit summary'
        self.edit(page, text, msg)
if __name__ == "__main__":
    bot = TaskRobot()
    try:
        bot.run()
    finally:
        bot.pushLog()

"""
from __future__ import unicode_literals
import sys
import os
import re
import time
import pywikibot

CONFIGURATION_PAGE = 'User:%s/Configuration'
CHECK_CONFIG_PAGE_EVERY = 10 #edits
LOG_PATH = os.path.expanduser('~/public_html/%s/')

class Robot:
    
    def __init__(self, task):
        self.site = pywikibot.getSite()
        self.trial = False
        self.trial_counter = 0
        self.trial_max = 0
        self.summary = None
        self.username = self.site.username()
        self.CONFIGURATION_PAGE = CONFIGURATION_PAGE % self.username
        self.task = task
        self.site = pywikibot.getSite()
        self.loggingEnabled = False
        self.counter = 0
        self.CHECK_CONFIG_PAGE_EVERY = CHECK_CONFIG_PAGE_EVERY
        self.args = pywikibot.handleArgs()
    def setAction(self, text):
        self.summary = text
    
    def startLogging(self, logPage):
        self.loggingEnabled = True
        self.localLog = False
        self.logPage = logPage
        self.logText = ''
        self.filled_path = LOG_PATH % (self.username.lower())
        if os.path.isdir(self.filled_path):
            self.localLog = True
            self.logFile = self.filled_path + '%s.log' % str(self.task)
    
    def pushLog(self, overwrite=False,header=True):
        if not self.logText:
            return
        #first do all local logging, then try on-wiki
        if header:
            mid = '\n==~~~~~==\n'
        else:
            mid = '\n'
        try:
            if self.localLog:
                if not overwrite and os.path.isfile(self.logFile):
                    f = open(self.logFile, 'r')
                    old = f.read()
                    logText = old + mid+ self.logText
                    f.close()
                else:
                    logText = self.logText
                f = open(self.logFile, 'w')
                f.write(logText)
                f.close()
        except UnicodeEncodeError:
            pass
            
        if (not overwrite) and self.logPage.exists():
            old = self.logPage.get()
            logText = old + mid + self.logText
        else:
            logText = self.logText
        self.logPage.put(logText, 'BOT: Updating log')
        self.loggingEnabled = False
        self.logText = ''
        
    def output(self, text,debug=False):
        if self.loggingEnabled and not debug:
            self.logText += text
            if (not text.endswith('\n')) or (not text.startswith('\n')):
                self.logText += '\n'
        pywikibot.output(text)
    
            
        
    def edit(self, page, text, summary=False, async=False, force = False, minorEdit=False):
        if not force:
            if self.counter >= self.CHECK_CONFIG_PAGE_EVERY:
                if not self.isEnabled():
                    self.output('Run-page is disabled. Quitting.')
                    self.quit(1)
                else:
                    self.counter = 0
            else:
                self.counter += 1
        if not summary:
            summary = self.summary
        page.put(text, summary, minorEdit=minorEdit,async=async)
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
        page = pywikibot.Page(self.site, self.CONFIGURATION_PAGE)
        try:
            config = page.get()
        except pywikibot.exceptions.NoPage:
            self.enabled = False
            return self.enabled
        config = config.lower()
        if 'enable: all' in config: #be careful...
            self.enabled = True
            return self.enabled
        search = re.search('%s: (.*?)\nenable(|d): (true|.*?)\n' % self.task, config)
        if not search:
            self.enabled = False
        else:
            self.enabled = (search.group(3) == 'true')
        return self.enabled
    
    def quit(self, status=0):
        #something fancy to go here later
        if self.loggingEnabled:
            self.pushLog()
        sys.exit(status)
    
