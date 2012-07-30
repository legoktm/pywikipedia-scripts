#!/usr/bin/env python
#
# (C) Legoktm, 2012 under the MIT License
#
# A helper class for managing bot tasks for [[User:Legobot]]
# Currently in alpha status

import sys
import re
import pywikibot
import couchdb

#CONSTANTS
#USERNAME = 'Legobot'
USERPAGE = 'User:%(USERNAME)s'
TALKPAGE = 'User talk:%(USERNAME)s'
TASKS = 'User:%(USERNAME)s/Tasks'
STOPPAGE = 'User:%(USERNAME)s/%(ID)s/Stop'
BRFA = 'Wikipedia:Bots/Requests for approval/%(USERNAME)s %(ID)s'
        


class Task:
    def __init__(self, id, bot):
        self.id = id
        self.bot = bot
        self.data = {
            'USERNAME': self.bot,
            'ID': self.id,
        }
        self.task_enabled = False # Whether that task is turned on
        self.running = False # Whether the task is actively running
        self.approved = False # Whether the task has been approved by BAG
        self.status = 'stasis'
        self.db_name = 'wp_%(USERNAME)s_task%(ID)d' % self.data
        self.couch = couchdb.Server()
        self.site = pywikibot.getSite()
        #CACHES
        self.brfa_page = None
    
    def storage(self):
        return self.data
    
    def initDB(self):
        if not self.couch.__contains__(self.db_name):
            self.db = self.couch.create(self.db_name)
        else:
            self.db = self.couch[self.db_name]
    
    def isEnabled(self):
        page = pywikibot.Page(self.site, STOPPAGE % self.data)
        text = page.get().lower()
        return text == 'run'
    
    def __getbrfaPage(self, force = False):
        if self.brfa_page and (not force):
            return self.brfa_page
        else:
            if self.data['ID'] == 1:
                self.data['ID'] = ''
                title = BRFA % self.data
                self.data['ID'] = 1
            else:
                title = BRFA % self.data
            page = pywikibot.Page(self.site, title)
            self.brfa_page = page.get()
            return self.brfa_page
    def brfaStatus(self, force = False):
        text = self.__getbrfaPage(force = force).lower()
        if '{{botrevoked}}' in text:
            stat = 'revoked'
        elif '{{botapproved}}' in text:
            stat = 'approved'
        elif '{{botspeedy}}' in text:
            stat = 'speedy'
        elif '{{botdenied}}' in text:
            stat = 'denied'
        elif '{{botwithdrawn}}' in text:
            stat = 'withdrawn'
        elif '{{botexpired}}' in text:
            stat = 'expired'
        elif '{{operatorassistanceneeded}}' in text:
            stat = 'op_needed'
        elif '{{bagassistanceneeded}}' in text:
            stat = 'bag_needed'
        elif '{{bottrialcomplete}}' in text:
            stat = 'complete'
        elif '{{bottrial}}' in text:
            stat = 'trial'
        else:
            stat = 'unknown'
        if stat in ('approved', 'speedy'):
            self.approved = True
        return stat
    def isApproved(self):
        self.brfaStatus()
        return self.approved
    
    def functionSummary(self, force = False):
        text = self.__getbrfaPage(force = force)
        found = re.findall("'''Function Summary:''' (.*?)\n", text)
        try:
            return found[0]
        except IndexError:
            try:
                found = re.findall("'''Function (o|O)verview:''' (.*?)\n", text)
                return found[0][1]
            except IndexError:
                return ''
    
    def initTrial(self, edits):
        """
        Initializes the trial, makes it easy to stay within trial limits
        TODO: add date support
        """
        self.trial = True
        self.max_edits = edits
        self.cur_edits = 0
        self.status = 'trial'
    
    def trialAction(self):
        """
        Simply when you want to add a counter to the trial and check your actions
        """
        self.cur_edits += 1
        if self.cur_edits >= self.max_edits:
            print '>>>Trial completed. Exiting.'
            pywikibot.stopme()
            sys.exit()
    
    def begin(self):
        print '>>>Running task #%(ID)s under %(USERNAME)s' % self.data
        if self.trial:
            print '>>>Begining trial of %s edits.' % self.max_edits
        elif not self.isApproved():
            print '>>>WARNING: This bot is not approved yet'
        
        
        
        
if __name__ == "__main__":
    pass
        