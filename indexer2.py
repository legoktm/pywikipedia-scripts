#!/usr/bin/env python
#-*- coding: utf-8 -*-
#from __future__ import unicode_literals

import sys
import os
import time
import calendar
import datetime
import sqlite3
try:
    import simplejson
except ImportError:
    import json as simplejson
import pywikibot
from pywikibot.data import api
import robot
import index_help

"""
(C) Legoktm, 2012 under the MIT License

"""



#constants
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = '|'.join(month for month in MONTH_NAMES)



class IndexBot(robot.Robot):
    
    def __init__(self):
        robot.Robot.__init__(self, task=15)
        self.template = pywikibot.Page(self.site, 'User:HBC Archive Indexerbot/OptIn')
        self.db = 'index2.db'
        self.startLogging(pywikibot.Page(self.site, 'User:Legobot/Archive Indexer Log'))
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        
    def begin_databases(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE instructions(talkpage TEXT, instructions TEXT, revid INT)")
        cur.execute("CREATE TABLE watchlist(talkpage TEXT, archive TEXT, revid INT)")
        self.conn.commit()
        
    def buildInstructionDB(self, gen=None, update=False):
        if not gen:
            gen = pywikibot.pagegenerators.ReferringPageGenerator(self.template, onlyTemplateInclusion = True, content = True)
        cur = self.conn.cursor()
        for page in gen:
            try:
                print u'Getting/saving data for [[%s]].' % page.title()
            except UnicodeEncodeError:
                pass
            instructions = index_help.parseInstructions(page)
            dumped = simplejson.dumps(instructions)
            revid = page.latestRevision()
            if update:
                cur.execute("UPDATE instructions SET revid=?, instructions=? WHERE talkpage=?", (revid, dumped, page.title()))
            else:
                page.watch()
                cur.execute("INSERT INTO instructions VALUES(?,?,?)", (page.title(), dumped, revid))
        self.conn.commit()
    
    
    def updateInstructionDB(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM instructions")
        rows = cur.fetchall()
        currentList = [row['talkpage'] for row in rows]
        newList = list()
        updateList = list()
        gen = pywikibot.pagegenerators.ReferringPageGenerator(self.template, onlyTemplateInclusion = True, content = True)
        for page in gen:
            if not (page.title() in currentList):
                try:
                    print u'%s is a new page.' % page.title()
                except UnicodeEncodeError:
                    pass
                newList.append(page)
                continue
            if page.latestRevision() != rows[currentList.index(page.title())]['revid']:
                try:
                    print u'%s needs to be updated.' % page.title()
                except UnicodeEncodeError:
                    pass
                updateList.append(page)
        self.output('* New pages: %s' % len(newList))
        self.output('* Updated pages: %s' % len(updateList))
        if newList:
            self.buildInstructionDB(newList)
        if updateList:
            self.buildInstructionDB(updateList, update=True)
    
    def fetchWatchlist(self):
        days = 1
        page = None
        for arg in self.args:
            if arg.startswith('--days'):
                try:
                    days = int(arg[7:])
                except ValueError:
                    pass
            if arg.startswith('--page'):
                try:
                    page = pywikibot.Page(self.site, arg[7:])
                except:
                    pass
        dayago = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        dayago = dayago.strftime('%Y-%m-%dT%H:00:00Z')
        namespaces = [1,3,5,7,9,11,13,15,101,109]
        if page:
            q = [page]
        else:
            q = api.ListGenerator(listaction='watchlist', wlstart=dayago)
            q.set_namespace(namespaces)
        queue = list()
        for item in q:
            if page:
                title = page.title()
            else:
                title = item['title']
            if not (title in queue):
                queue.append(pywikibot.Page(self.site, title))
        cur = self.conn.cursor()
        for page in queue:
            try:
                self.do_page(page, cur)
            except:
                pass
    def do_page(self, page, cur):
        cur.execute("SELECT instructions FROM instructions WHERE talkpage=?", (page.title(),))
        try:
            info = cur.fetchone()['instructions']
        except TypeError, e:
            print u'Skipping %s since it isn\'t in the database.' % page.title()
            page.watch(unwatch=True)
            return
        info = simplejson.loads(info)
        try:
            text = index_help.followInstructions(info)
        except Exception, e:
            self.output('* Unknown error on %s.' % page.title())
            return
        if text:
            self.output(text)
        
        
            
def main():
    build = not os.path.isfile('index2.db')
    bot = IndexBot()
    if build:
        bot.begin_databases()
        bot.buildInstructionDB()
    bot.updateInstructionDB()
    try:
        bot.fetchWatchlist()
    finally:
        bot.pushLog(overwrite=True)
       
                
if __name__ == "__main__":
    main()
        


    