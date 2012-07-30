#!/usr/bin/env python
#
# (C) Legoktm, 2012 under the MIT License
#
# Automagically manages [[User:Legobot/Tasks]]
# Currently in alpha status
#
# Syntax: python tasksheet.py Legobot
# Just replace Legobot with the name of your bot

import sys
import re
import pywikibot
from legobot import *

REGEX = 'Revoked|Approved|Speedy|Denied|Withdrawn|Expired|TrialComplete|Trial|Status'


class UpdateTaskSheetRobot:  
    def __init__(self):
        self.bot = bot
        self.site = pywikibot.getSite()
        self.taskPage = pywikibot.Page(self.site, 'User:%s/Tasks' % self.bot)
        
    def parseCurrentTasks(self):
        if not self.taskPage.exists():
            return {}
        text = self.taskPage.get()
        lines = text.split('\n')
        data = {}
        for line in lines:
            if line == '{{BotTask/Top}}':
                continue
            if line == '|}':
                continue
            if line.startswith('{{BotTask|'):
                search = re.search('\|1=(\d|\d\d)\|2=(%s)\|3=(in|)active\|4=(.*?)}}' % REGEX, line)
                if search:
                    id = int(search.group(1))
                    d = {
                         'brfa_result': search.group(2),
                         'status': search.group(3) + 'active',
                         'details': search.group(4),
                    }
                    data[id] = d
        return data
    
    def mergeData(self, old, new):
        #Use old data as starting point
        final = old
        for key in new.keys():
            if not (key in old.keys()):
                #Add in all new data
                final[key] = new[key]
            else:
                #Merge old data
                if old[key]['brfa_result'] == new[key]['brfa_result']:
                    #only update details
                    final[key]['details'] = new[key]['details']
                else:
                    final[key] == new[key]
        return final

    def buildTemplate(self, info):
        pageContent = '{{BotTask/Top}}\n'
        key = 1
        while info.has_key(key):
            pageContent += '{{BotTask|1=%s|2=%s|3=%s|4=%s}}\n' % (key, info[key]['brfa_result'], info[key]['status'], info[key]['details'])
            key += 1
        pageContent += '|}'
        return pageContent
    
    def fetchNewData(self):
        data = {'USERNAME':self.bot}
        data['ID'] = 1
        info = {}
        keep_going = True
        while keep_going:
            if data['ID'] == 1:
                data['ID'] = ''
                brfa_page = pywikibot.Page(self.site, BRFA % data)
                data['ID'] = 1
            else:
                brfa_page = pywikibot.Page(self.site, BRFA % data)
            if not brfa_page.exists():
                keep_going = False
                continue
            task = Task(data['ID'], data['USERNAME'])
            brfa_result = task.brfaStatus()
            if brfa_result in ('op_needed', 'bag_needed','unknown'):
                brfa_result = 'Status'
            elif brfa_result == 'complete':
                brfa_result = 'TrialComplete'
            else:
                brfa_result = brfa_result.title()
            if brfa_result in ('Denied', 'Withdrawn', 'Expired'):
                status = 'inactive'
            else:
                status = 'active'
            details = task.functionSummary()
            t_data = {
                'brfa_result': brfa_result,
                'status': status,
                'details': details,
            }
            info[data['ID']] = t_data
            data['ID'] += 1
        return info
    
    def run(self):
        old = self.parseCurrentTasks()
        new = self.fetchNewData()
        final = self.mergeData(old, new)
        content = self.buildTemplate(final)
        if self.taskPage.exists():
            pywikibot.showDiff(self.taskPage.get(), content)
        self.taskPage.put(content, 'BOT: Updating list of tasks in userspace')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        bot = sys.argv[1]
    else:
        bot = 'Legobot'
    bot = UpdateTaskSheetRobot(bot)
    bot.run()