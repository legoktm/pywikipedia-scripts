#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import time
import calendar
import urllib
import datetime
import pywikibot


#constants
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = 'January|February|March|April|May|June|July|August|September|October|November|December'

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

class IndexerBot:
    
    def __init__(self):
        self.site = pywikibot.getSite()
        self.logText = '\n'
    
    def fetchPages(self):
        """
        A generator for pages transcluding the template
        """
        #yield pages
        pass
        yield pywikibot.Page(self.site, 'User talk:Legoktm')
        #template = pywikibot.Page(self.site, 'User:HBC Archive Indexerbot/OptIn')
        #gen = pywikibot.pagegenerators.ReferringPageGenerator(template, onlyTemplateInclusion = True)
        #return gen
    
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
            return time.strptime(timestamp, '%H:%M:%S, %d %B %Y') # Some users (ex: Pathoschild) include seconds in their signature
    
    def humanReadable(self, seconds):
        return str(datetime.timedelta(seconds=seconds))
    
    def parseInstructions(self, page):
        """
        Parses the index template for all of the parameters
        """
        text = page.get()
        print 'Parsing instructions'
        key = text.find('{{User:HBC Archive Indexerbot/OptIn')
        data = text[key:].split('}}')[0][36:] #kinda scared about hardcoding so much
        info = {}
        info['talkpage'] = page
        for param in data.split('|'):
            if param.startswith('target='):
                info['target'] = param[7:]
            elif param.startswith('mask='):
                if info.has_key('mask'):
                    info['mask'].append(param[5:])
                else:
                    info['mask'] = [param[5:]]
            elif param.startswith('indexhere='):
                value = param[10:]
                if value.lower() == 'yes':
                    info['indexhere'] = True
                else:
                    info['indexhere'] = False
            elif param.startswith('template='):
                info['template'] = param[9:]
            elif param.startswith('leading_zeros='):
                info['leading_zeros'] = int(param[14:])
            elif param.startswith('first_archive='):
                info['first_archive'] = param[14:]
        #set default values if not already set
        if not info.has_key('leading_zeros'):
            info['leading_zeros'] = 0
        if not info.has_key('indexhere'):
            info['indexhere'] = False
        if not info.has_key('template'):
            info['template'] = 'User:HBC Archive Indexerbot/default template'
        return info
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
        indexPage = pywikibot.Page(self.site, info['target'])
        indexPageOldText = indexPage.get()
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
                    page = pywikibot.Page(self.site, title)
                    key += 1
                    if page.exists():
                        data['archives'].append(page)
                    else:
                        keep_going = False
            elif '<month>' in mask:
                if not info.has_key('first_archive'):
                    raise InvalidMask
                #grab the month and year out of the first archive
                regex = mask.replace('<month>', '(%s)' % MONTH_REGEX).replace('<year>', '(\d\d\d\d)')
                match = re.search(regex, info['first_archive'])
                month = match.group(1)
                year = int(match.group(2))
                keep_going = True
                while keep_going:
                    title = mask.replace('<month>', month).replace('<year>', str(year))
                    page = pywikibot.Page(self.site, title)
                    if page.exists():
                        data['archives'].append(page)
                        month, year = self.__nextMonth(month, year)
                    else:
                        keep_going = False
            else: #assume the mask is the page
                page = pywikibot.Page(self.site, mask)
                if page.exists():
                    data['archives'].append(page)
        if info['indexhere']:
            data['archives'].append(info['talkpage'])
        #finished the mask processing!
        #now verify the template exists
        template = pywikibot.Page(self.site, info['template'])
        if not template.exists():
            #fallback on the default template
            template = pywikibot.Page(self.site, 'User:HBC Archive Indexerbot/default template')
        data['template'] = template.get()
        #finished the template part    
        #lets parse all of the archives now
        data['parsed'] = list()
        for page in data['archives']:
            parsed = self.parseArchive(page)
            data['parsed'].extend(parsed)
        #build the index      
        indexText = self.__buildIndex(data['parsed'], data['template'], info)
        if self.__verifyUpdate(indexPageOldText, indexText):
            print 'Will edit %s' % indexPage.title()
            #pywikibot.showDiff(indexPageOldText, indexText)
            indexPage.put(indexText, 'BOT: Updating index (currently testing)')
            self.logText += '* Successfully indexed [[%s]] to [[%s]].' % (info['talkpage'].title(), indexPage.title())
        else:
            print 'Won\'t edit %s' % indexPage.title()
            self.logText += '* Skipped indexing [[%s]] to [[%s]] since no update was needed.' % (info['talkpage'].title(), indexPage.title())

    
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
        print 'Building the index'
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
        indexText = '<!-- HBC Archive Indexerbot can blank this -->'
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
        text = page.get()
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
            ts = re.finditer('(\d\d:\d\d), (\d\d) (%s) (\d\d\d\d)' % MONTH_REGEX, content)
            epochs = list()
            for stamp in ts:
                mw = stamp.group(0)
                parsed = time.strptime(mw, '%H:%M, %d %B %Y')
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
        generator = self.fetchPages()
        for page in generator:
            print 'Operating on %s.' % page.title()
            instructions = self.parseInstructions(page)
            try:
                self.followInstructions(instructions)
                self.logText += '* Processed [[%s]].' % page.title()
            except NoMask:
                self.logText += '* ERROR: No mask specified on [[%s]]' % page.title()
            except NoTarget:
                self.logText += '* ERROR: No target specified on [[%s]]' % page.title()
            except NotAllowedToEditPage:
                self.logText += '* ERROR: Safe string has not been added for [[%s]]' % page.title()

        logPage = pywikibot.Page(self.site, 'User:Legobot/Archive Log')
        logPage.put(self.logText, 'Bot: Updating log')
            
if __name__ == "__main__":
    bot = IndexerBot()
    bot.run()
                    