#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import time
import calendar
import urllib
import datetime
import pywikibot
import time


#constants
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = 'January|February|March|April|May|June|July|August|September|October|November|December'

class IndexerBot:
    
    def __init__(self):
        self.site = pywikibot.getSite()
    
    def fetchPages(self):
        """
        A generator for pages transcluding the template
        """
        #yield pages
        pass
        yield pywikibot.Page(self.site, 'User talk:Legoktm')
    
    def epochToMW(self, timestamp):
        """
        Converts a unix epoch time to a mediawiki timestamp
        """
        if type(timestamp) == type(''):
            return timestamp
        struct = time.gmtime(timestamp)
        return time.strftime('%H:%M, %d %B %Y', struct)
        
    
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
                    info['talkpage'] = page
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
                if not info.has_key['first_archive']:
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
        indexText = self.__buildIndex(data['parsed'], data['template'])
        indexPage = pywikibot.Page(self.site, info['target'])
        print 'Will edit %s' % indexPage.title()
        time.sleep(10)
        indexPage.put(indexText, 'BOT: Updating index (currently testing)')
    
    def __buildIndex(self, parsedData, template):
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
        print split
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
        indexText = ''
        indexText += templateData['lead']
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
        data = list()
        split = text.split('==')
        if text.startswith('=='): #no lead text
            key = 0
        else:
            key = 1
        while key < len(split):
            d = {}
            d['topic'] = split[key]
            d['link'] = '[[%s#%s]]' % (page.title(), urllib.quote(d['topic'].encode('utf-8')))
            content = split[key+1]
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
            key += 2
        return data
            
    def run(self):
        generator = self.fetchPages()
        for page in generator:
            print 'Operating on %s.' % page.title()
            instructions = self.parseInstructions(page)
            self.followInstructions(instructions)
            
if __name__ == "__main__":
    bot = IndexerBot()
    bot.run()
                    