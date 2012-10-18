#!/usr/bin/env python
#
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
#
# Automagically manages [[User:Legobot/Tasks]]
# Currently in alpha status
#

import re
import pywikibot
import robot
REGEX = 'Revoked|Approved|Speedy|Denied|Withdrawn|Expired|TrialComplete|Trial|Status'
BRFA = 'Wikipedia:Bots/Requests for approval/%s %s'

class UpdateTaskSheetRobot(robot.Robot):

    def __init__(self, bot='Legobot'):
        robot.Robot.__init__(self, 0)
        self.bot = bot
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
                    t_id = int(search.group(1))
                    d = {
                         'brfa_result': search.group(2),
                         'status': search.group(3) + 'active',
                         'details': search.group(4),
                    }
                    data[t_id] = d
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
                    final[key] = new[key]
        return final

    def buildTemplate(self, info):
        pageContent = '{{BotTask/Top}}\n'
        key = 1
        while info.has_key(key):
            pageContent += '{{BotTask|1=%s|2=%s|3=%s|4=%s}}\n' % (key, info[key]['brfa_result'], info[key]['status'], info[key]['details'])
            key += 1
        pageContent += '|}'
        return pageContent
    
    def functionSummary(self, text):
        found = re.findall("'''Function Summary:''' (.*?)\n", text, re.IGNORECASE)
        try:
            real = found[0]
        except IndexError:
            try:
                found = re.findall("'''Function Overview:''' (.*?)\n", text, re.IGNORECASE)
                real = found[0][1]
            except IndexError:
                real = ''
        #clean up
        search = re.search('\|(.*?)=', real)
        if search:
            real = real.replace(search.group(0), '{{!}}%s=' % search.group(1))
        return real
    
    def fetchNewData(self):
        task = 1
        info = {}
        while True:
            if task == 1:
                task = ''
                brfa_page = pywikibot.Page(self.site, BRFA % (self.bot, task))
                task = 1
            else:
                brfa_page = pywikibot.Page(self.site, BRFA % (self.bot, task))
            if not brfa_page.exists():
                break
            brfa_text = brfa_page.get()
            print 'Fetching %s' % brfa_page.title(asLink=True)
            brfa_result = self.brfaStatus(brfa_text)
            details = self.functionSummary(brfa_text)
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
            t_data = {
                'brfa_result': brfa_result,
                'status': status,
                'details': details,
            }
            info[task] = t_data
            task += 1
        return info
    
    def brfaStatus(self, text):
        text = text.lower()
        if '{{botrevoked}}' in text:
            stat = 'revoked'
        elif '{{botapproved' in text:
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
        elif '{{bottrial' in text:
            stat = 'trial'
        else:
            stat = 'unknown'
        return stat
    
    def run(self):
        old = self.parseCurrentTasks()
        new = self.fetchNewData()
        final = self.mergeData(old, new)
        content = self.buildTemplate(final)
        if self.taskPage.exists():
            pywikibot.showDiff(self.taskPage.get(), content)
        self.taskPage.put(content, 'BOT: Updating list of tasks in userspace')

if __name__ == "__main__":
    for username in ['Legobot', 'Legobot II', 'Legobot III', 'Hockeybot']:
        bot = UpdateTaskSheetRobot(bot=username)
        bot.run()