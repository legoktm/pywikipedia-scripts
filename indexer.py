#!/usr/bin/env python
#-*- coding: utf-8 -*-
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

import sys
import os
import re
import time
import calendar
import urllib
import datetime
import sqlite3
import threading
import Queue
import pywikibot




#constants
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = '|'.join(month for month in MONTH_NAMES)
SITE = pywikibot.getSite()
LOG_TEXT = ''
#errors
class GeneralError(Exception):
    """
    General base class error
    """

class NoMask(GeneralError):
    """
    No mask set in the template
    """

class NoTarget(GeneralError):
    """
    No target set in the template
    """

class NotAllowedToEditPage(GeneralError):
    """
    The safe string has not been added to the page
    """

def initialize_db():
    if os.path.isfile('indexerbot.db'):
        return
    conn = sqlite3.connect('indexerbot.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE cache(pagename TEXT, revid INT)')
    conn.commit()
    conn.close()

initialize_db()




class ProcessThread(threading.Thread):
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        
        
    def fetchPage(self, page):
        """
        Checks if we need to fetch the page again from the wiki
        Or whether the cached version is good enough
        If it needs to update, it will also update the cache
        
        Returns a boolean value, False if no update is required, True if needed.
        """
        self.conn = sqlite3.connect('indexerbot.db')
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT revid FROM cache WHERE pagename=?", [page.title()])
        rows = self.cur.fetchall()
        latestRev = page.latestRevision()
        if rows:
            revid = rows[0][0]
            print 'revid: %s, latestRev: %s' % (revid, latestRev)
            if revid == latestRev:
                self.conn.close()
                return False
            else:
                self.cur.execute("UPDATE cache SET revid=? WHERE pagename=?", [latestRev, page.title()])
        else:
            print '%s added to db.' % page.title()
            self.cur.execute("INSERT INTO cache VALUES (?, ?)", [page.title(), latestRev])
        self.conn.commit()
        self.conn.close()
        return True
    
    def clean(self, text):
        """various cleaning functions to simplify parsing bad text"""
        
        #first lets eliminate any whitespace in the front
        text = self.__findFront(text)
        # clean up when people do |indehere=<yes>
        search = re.search('(.*?)=\<(#|yes|no|month|year|.*?)\>', text)
        if search:
            front = search.group(1) + '='
            if search.group(2) in ['#', 'month', 'year']:
                pass
            elif search.group(2) in ['yes', 'no'] :
                text = search.group(2)
            else:
                text = search.group(2)
            text = front + text
        #remove wikilinks from everything
        search = re.search('\[\[(.*?)\]\]', text)
        if search:
            text = text.replace(search.group(0), search.group(1))
        return text
                
        
    
    def parseInstructions(self, page):
        """
        Parses the index template for all of the parameters
        """
        text = page.get()
        #print 'Parsing instructions for [[%s]].' % page.title()
        key = text.find('{{User:HBC Archive Indexerbot/OptIn')
        data = text[key:].split('}}')[0][36:] #kinda scared about hardcoding so much
        #remove any comments (apparently users do this)
        clean = pywikibot.removeDisabledParts(data)
        info = {}
        info['mask'] = []
        info['talkpage'] = page
        for param in clean.split('|'):
            param = self.clean(param)
            if param.startswith('target='):
                target = self.clean(param[7:])
                if target.startswith('/'):
                    target = page.title() + target
                info['target'] = target
            elif param.startswith('mask='):
                mask = self.clean(param[5:])
                if mask.startswith('/'):
                    mask = page.title() + mask
                info['mask'].append(mask)
            elif param.startswith('indexhere='):
                value = param[10:]
                if self.clean(value.lower()) == 'yes':
                    info['indexhere'] = True
                else:
                    info['indexhere'] = False
            elif param.startswith('template='):
                info['template'] = self.clean(param[9:].replace('\n',''))
            elif param.startswith('leading_zeros='):
                try:
                    info['leading_zeros'] = int(self.clean(param[14:]))
                except ValueError:
                    pass
            elif param.startswith('first_archive='):
                info['first_archive'] = self.clean(param[14:])
        #set default values if not already set
        for key in info.keys():
            if type(info[key]) == type(u''):
                if info[key].isspace() or (not info[key]):
                    del info[key]
        
        if not info.has_key('leading_zeros'):
            info['leading_zeros'] = 0
        if not info.has_key('indexhere'):
            info['indexhere'] = False
        if not info.has_key('template'):
            info['template'] = 'User:HBC Archive Indexerbot/default template'
        if info['template'] == 'template location':
            info['template'] = 'User:HBC Archive Indexerbot/default template'
        return info

    def __findFront(self, item):
        while item.startswith(' '):
            item = item[1:]
        return item


    def epochToMW(self, timestamp):
        """
        Converts a unix epoch time to a mediawiki timestamp
        """
        if type(timestamp) == type(''):
            return timestamp
        struct = time.gmtime(timestamp)
        return time.strftime('%H:%M, %d %B %Y', struct)
        
    def mwToEpoch(self, timestamp):
        """
        Converts a mediawiki timestamp to unix epoch time
        """
        try:
            return time.strptime(timestamp, '%H:%M, %d %B %Y')
        except ValueError:
            try:
                return time.strptime(timestamp, '%H:%M:%S, %d %B %Y') # Some users (ex: Pathoschild) include seconds in their signature
            except ValueError:
                return None #srsly wtf?
    
    def humanReadable(self, seconds):
        return str(datetime.timedelta(seconds=seconds))
    
    def __findFront(self, item):
        while item.startswith(' '):
            item = item[1:]
        return item
    
    def __prefixNumber(self, num, leading):
        """
        Prefixes "num" with %leading zeroes.
        """
        leading = int(leading)
        num = str(num)
        while leading != 0:
            num = '0' + num
            leading -= 1
        return num
        
    def followInstructions(self, info):
        #verify all required parameters are there
        if not info.has_key('mask'):
            raise NoMask
        if not info.has_key('target'):
            raise NoTarget
        #verify we can edit the target, otherwise just skip it
        #hopefully this will save processing time
        indexPage = pywikibot.Page(SITE, info['target'])
        try:
            indexPageOldText = indexPage.get()
        except pywikibot.exceptions.IsRedirectPage:
            indexPage = indexPage.getRedirectTarget()
            indexPageOldText = indexPage.get()
        except pywikibot.exceptions.NoPage:
            raise NotAllowedToEditPage
        if not self.__okToEdit(indexPageOldText):
            raise NotAllowedToEditPage
        #looks good, lets go
        data = {}
        #first process the mask
        data['archives'] = list()
        for mask in info['mask']:
            if '<#>' in mask:
                key = 1
                keep_going = True
                #numerical archive
                while keep_going:
                    archive_num = self.__prefixNumber(key, info['leading_zeros'])
                    title = mask.replace('<#>', archive_num)
                    page = pywikibot.Page(SITE, title)
                    key += 1
                    if page.exists():
                        data['archives'].append(page)
                    else:
                        keep_going = False
            elif '<month>' in mask:
                if not info.has_key('first_archive'):
                    raise NoMask
                #grab the month and year out of the first archive
                regex = mask.replace('<month>', '(%s)' % MONTH_REGEX).replace('<year>', '(\d\d\d\d)')
                match = re.search(regex, info['first_archive'])
                month = match.group(1)
                year = int(match.group(2))
                keep_going = True
                while keep_going:
                    title = mask.replace('<month>', month).replace('<year>', str(year))
                    page = pywikibot.Page(SITE, title)
                    if page.exists():
                        data['archives'].append(page)
                        month, year = self.__nextMonth(month, year)
                    else:
                        keep_going = False
            else: #assume the mask is the page
                if ('<' in mask) or ('>' in mask):
                    print 'ERRORERROR: Did not parse %s properly.' % mask
                    continue
                page = pywikibot.Page(SITE, mask)
                if page.exists():
                    data['archives'].append(page)
        if info['indexhere']:
            data['archives'].append(info['talkpage'])
        #finished the mask processing!
        #now verify the template exists
        template = pywikibot.Page(SITE, info['template'])
        if not template.exists():
            #fallback on the default template
            template = pywikibot.Page(SITE, 'User:HBC Archive Indexerbot/default template')
        data['template'] = template.get()
        #finished the template part    
        #lets parse all of the archives now
        data['parsed'] = list()
        update_required = False
        caching_only = '--buildcache' in sys.argv
        for page in data['archives']:
            updated = self.fetchPage(page)
            if updated:
                update_required = True
                if not caching_only:
                    break
        if caching_only:
            return
        global LOG_TEXT
        if not update_required:
            LOG_TEXT += '* [[%s]] did not require an update.\n' % info['talkpage'].title()
            return
        for page in data['archives']:
            parsed = self.parseArchive(page)
            data['parsed'].extend(parsed)
        #build the index      
        indexText = self.__buildIndex(data['parsed'], data['template'], info)
        if self.__verifyUpdate(indexPageOldText, indexText):
            print '>>>Will edit %s' % indexPage.title()
            #pywikibot.showDiff(indexPageOldText, indexText)
            indexPage.put_async(indexText, 'BOT: Updating index (Trial [[Wikipedia:Bots/Requests for approval/Legobot 15|BRFA]])')
            LOG_TEXT += '* Successfully indexed [[%s]] to [[%s]].\n' % (info['talkpage'].title(), indexPage.title())
        else:
            print '>>>Won\'t edit %s' % indexPage.title()
            LOG_TEXT += '* Skipped indexing [[%s]] to [[%s]] since no update was needed.\n' % (info['talkpage'].title(), indexPage.title())

    
    def __cleanLinks(self, link):
        link = link.encode('utf-8')
        #[[piped|links]] --> links
        search = re.search('\[\[(.*?)\|(.*?)\]\]', link)
        while search:
            link = link.replace(search.group(0), search.group(2))
            search = re.search('\[\[(.*?)\|(.*?)\]\]', link)
        #[[wikilinks]] --> wikilinks
        search = re.search('\[\[(.*?)\]\]', link)
        while search:
            link = link.replace(search.group(0), search.group(1))
            search = re.search('\[\[(.*?)\]\]', link)
        #'''bold''' --> bold
        #''italics'' --> italics
        search = re.search("('''|'')(.*?)('''|'')", link)
        while search:
            link = link.replace(search.group(0), search.group(2))
            search = re.search("('''|'')(.*?)('''|'')", link)
        
        link = urllib.quote(link)
        return link
    
    def __okToEdit(self, text):
        return bool(re.search('<!-- (HBC Archive Indexerbot|Legobot) can blank this -->', text))
    
    def __buildIndex(self, parsedData, template, info):
        """
        Reads the template and creates the index for it
        """
        #first lets read the template
        #print 'Building the index.' 
        templateData = {}
        key = template.find('<nowiki>')
        lastKey = template.find('</nowiki>')
        importantStuff = template[key+8:lastKey]
        split = re.split('<!--\s', importantStuff)
        for item in split:
            if item.startswith('HEADER'):
                templateData['header'] = item[11:]
            elif item.startswith('ROW'):
                templateData['row'] = item[8:]
            elif item.startswith('ALT ROW'):
                templateData['altrow'] = item[12:]
            elif item.startswith('FOOTER'):
                templateData['footer'] = item[11:]
            elif item.startswith('END'):
                templateData['end'] = item[8:]
            elif item.startswith('LEAD'):
                templateData['lead'] = item[9:]
        if not templateData.has_key('altrow'):
            templateData['altrow'] = templateData['row']
        if not templateData.has_key('lead'):
            templateData['lead'] = ''
        if not templateData.has_key('end'):
            templateData['end'] = ''
        #print templateData
        #finished reading the template
        indexText = '<!-- Legobot can blank this -->'
        indexText += templateData['lead']
        reportInfo = 'Report generated based on a request from [[%s]]. It matches the following masks: ' % info['talkpage'].title()
        for mask in info['mask']:
            reportInfo += '%s, ' % mask
        reportInfo += '\n<br />\nIt was generated at ~~~~~ by [[User:Legobot|Legobot]].\n'
        indexText += reportInfo
        indexText += templateData['header']
        alt = False
        for item in parsedData:
            if alt:
                rowText = templateData['altrow']
                alt = False
            else:
                rowText = templateData['row']
                alt = True
            rowText = rowText.replace('%%topic%%', item['topic'])
            rowText = rowText.replace('%%replies%%', str(item['replies']))
            rowText = rowText.replace('%%link%%', item['link'])
            rowText = rowText.replace('%%first%%', item['first'])
            rowText = rowText.replace('%%firstepoch%%', str(item['firstepoch']))
            rowText = rowText.replace('%%last%%', item['last'])
            rowText = rowText.replace('%%lastepoch%%', str(item['lastepoch']))
            rowText = rowText.replace('%%duration%%', item['duration'])
            rowText = rowText.replace('%%durationsecs%%', str(item['durationsecs']))
            indexText += rowText
        indexText += templateData['footer']
        indexText += templateData['end']
        return indexText

    def __verifyUpdate(self, old, new):
        """
        Verifies than an update is needed, and we won't be just updating the timestamp
        """
        old2 = re.sub('generated at (.*?) by', 'generated at ~~~~~ by', old)
        new = new[:len(new)-2] # for some reason when getting the page text, the last linebreak is cutoff?
        return old2 != new
        
    def __nextMonth(self, month, year):
        """
        Returns what the next month should be
        If December --> January, then it ups the year as well
        """
        
        index = MONTH_NAMES.index(month)
        if index == 11:
            new_index = 0
            year += 1
        else:
            new_index = index + 1
        new_month = MONTH_NAMES[new_index]
        return new_month, year
        
    def splitIntoThreads(self, text):
        """
        Inspired/Copied by/from pywikipedia/archivebot.py
        """
        lines = text.split('\n')
        found = False
        threads = list()
        curThread = {}
        for line in lines:
            threadHeader = re.search('^== *([^=].*?) *== *$',line)
            if threadHeader:
                found = True
                if curThread:
                    threads.append(curThread)
                    curThread = {}
                curThread['topic'] = threadHeader.group(1)
                curThread['content'] = ''
            else:
                if found:
                    curThread['content'] += line + '\n'
        if curThread:
            threads.append(curThread)
        return threads
        
    def parseArchive(self, page):
        """
        Parses each individual archive
        Returns a list of dicts of the following info:
            topic - The heading
            replies - estimated count (simply finds how many instances of "(UTC)" are present
            link - link to that section
            first - first comment
            firstepoch - first comment (epoch)
            last - last comment
            lastepoch - last comment (epoch)
            duration - last-first (human readable)
            durationsecs - last-first (seconds)
        
        """
        try:
            text = page.get()
        except pywikibot.exceptions.IsRedirectPage:
            redir_page = page.getRedirectTarget()
            text = redir_page.get()
        print 'Parsing %s.' % page.title()
        threads = self.splitIntoThreads(text)
        data = list()
        for thread in threads:
            d = {}
            d['topic'] = thread['topic']
            while d['topic'].startswith(' '):
                d['topic'] = d['topic'][1:]
            d['link'] = '[[%s#%s]]' % (page.title(), self.__cleanLinks(d['topic']))
            content = thread['content']
            d['content'] = content
            #hackish way of finding replies
            found = re.findall('\(UTC\)', content)
            d['replies'] = len(found)
            #find all the timestamps
            ts = re.finditer('(\d\d:\d\d|\d\d:\d\d:\d\d), (\d\d) (%s) (\d\d\d\d)' % MONTH_REGEX, content)
            epochs = list()
            for stamp in ts:
                mw = stamp.group(0)
                parsed = self.mwToEpoch(mw)
                if parsed:
                    epochs.append(calendar.timegm(parsed))
            earliest = 999999999999999999
            last = 0
            for item in epochs:
                if item < earliest:
                    earliest = item
                if item > last:
                    last = item
            if earliest == 999999999999999999:
                earliest = 'Unknown'
                d['duration'] = 'Unknown'
                d['durationsecs'] = 'Unknown'
            if last == 0:
                last = 'Unknown'
                d['duration'] = 'Unknown'
                d['durationsecs'] = 'Unknown'
                
            d['first'] = self.epochToMW(earliest)
            d['firstepoch'] = earliest
            d['last'] = self.epochToMW(last)
            d['lastepoch'] = last
            if not d.has_key('duration'):
                d['duration'] = self.humanReadable(last - earliest)
                d['durationsecs'] = last - earliest
            data.append(d)
        return data
            
    def run(self):
        while True:
            page = self.queue.get()
            instructions = self.parseInstructions(page)
            global LOG_TEXT
            try:
                print '>>>Beginning to operate on [[%s]].' % page.title()
                self.followInstructions(instructions)
            except NoMask:
                LOG_TEXT += '* ERROR: No mask specified on [[%s]]\n' % page.title()
            except NoTarget:
                LOG_TEXT += '* ERROR: No target specified on [[%s]]\n' % page.title()
            except NotAllowedToEditPage:
                LOG_TEXT += '* ERROR: Safe string has not been added for [[%s]]\n' % page.title()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception, e:
                LOG_TEXT += 'general error: %s\noccurred on %s' % (e, page.title())
            #except:
            #    LOG_TEXT += '* UNKNOWN ERROR: occured on [[%s]]\n.' % page.title()
            print '>>>Finished operating on [[%s]].' % page.title()
            self.queue.task_done()


if __name__ == "__main__":
    try:
        startQueue = Queue.Queue()
        template = pywikibot.Page(SITE, 'User:HBC Archive Indexerbot/OptIn')
        gen = pywikibot.pagegenerators.ReferringPageGenerator(template, onlyTemplateInclusion = True, content = True)
        for page in gen:
            startQueue.put(page)
        #startQueue.put(pywikibot.Page(SITE, 'Talk:The Doon School'))
    
        for i in range(10):
            p = ProcessThread(startQueue)
            p.setDaemon(True)
            p.start()
        startQueue.join()
        #logPage = pywikibot.Page(SITE, 'User:Legobot/Archive Log')
        #logPage.put(LOG_TEXT, 'Bot: Updating log')
    finally:
        f = open('error_log.txt', 'w')
        f.write(LOG_TEXT)
        f.close()
    
    
    

                    