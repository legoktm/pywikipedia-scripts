#!/usr/bin/env python
#-*- coding: utf-8 -*-


"""
(C) Legoktm, 2012 under the MIT License
helper functions for indexer2.py
"""
import re
import urllib
import time
import calendar
import datetime
import pywikibot
SITE = pywikibot.getSite()
LOG_TEXT = ''
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
MONTH_REGEX = '|'.join(month for month in MONTH_NAMES)



def parseInstructions(page):
    """
    Parses the index template for all of the parameters
    """
    text = page.get()
    #print 'Parsing instructions for [[%s]].' % page.title()
    key = text.find('{{User:HBC Archive Indexerbot/OptIn')
    data = text[key:].split('}}')[0][36:] #kinda scared about hardcoding so much
    #remove any comments (apparently users do this)
    cleaned = pywikibot.removeDisabledParts(data)
    info = {}
    info['mask'] = []
    info['talkpage'] = page.title()
    for param in cleaned.split('|'):
        param = clean(param)
        if param.startswith('target='):
            target = clean(param[7:])
            if target.startswith('/'):
                target = page.title() + target
            info['target'] = target
        elif param.startswith('mask='):
            mask = clean(param[5:])
            if mask.startswith('/'):
                mask = page.title() + mask
            info['mask'].append(mask)
        elif param.startswith('indexhere='):
            value = param[10:]
            if clean(value.lower()) == 'yes':
                info['indexhere'] = True
            else:
                info['indexhere'] = False
        elif param.startswith('template='):
            info['template'] = clean(param[9:].replace('\n',''))
        elif param.startswith('leading_zeros='):
            try:
                info['leading_zeros'] = int(clean(param[14:]))
            except ValueError:
                pass
        elif param.startswith('first_archive='):
            info['first_archive'] = clean(param[14:])
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
def clean(text):
    """various cleaning functions to simplify parsing bad text"""
    
    #first lets eliminate any whitespace in the front
    text = __findFront(text)
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


def __findFront(item):
    while item.startswith(' '):
        item = item[1:]
    return item

def __prefixNumber(num, leading):
    """
    Prefixes "num" with %leading zeroes.
    """
    leading = int(leading)
    num = str(num)
    while leading != 0:
        num = '0' + num
        leading -= 1
    return num

def __nextMonth(month, year):
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


def getNextMask(current, pattern, leading_zeroes=0):
    if '<#>' in pattern:
        regex = pattern.replace('<#>', '(\d+)')
        key = int(re.search(regex, current).group(1))
        archive_num = __prefixNumber(key+1, leading_zeroes)
        return pattern.replace('<#>', archive_num)
    if '<month>' in pattern:
        regex = pattern.replace('<month>', '(%s)' % MONTH_REGEX).replace('<year>', '(\d\d\d\d)')
        match = re.search(regex, current)
        month, year = __nextMonth(match.group(1), int(match.group(2)))
        return pattern.replace('<month>', month).replace('<year>', str(year))
        
        
        
        
        
def getMasks(info):
    data = list()
    for mask in info['mask']:
        if '<#>' in mask:
            key = 1
            keep_going = True
            #numerical archive
            while keep_going:
                archive_num = __prefixNumber(key, info['leading_zeros'])
                title = mask.replace('<#>', archive_num)
                page = pywikibot.Page(SITE, title)
                key += 1
                if page.exists():
                    data.append(page)
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
                    data.append(page)
                    month, year = __nextMonth(month, year)
                else:
                    keep_going = False
        else: #assume the mask is the page
            if ('<' in mask) or ('>' in mask):
                print 'ERRORERROR: Did not parse %s properly.' % mask
                continue
            page = pywikibot.Page(SITE, mask)
            if page.exists():
                data.append(page)
    if info['indexhere']:
        data.append(pywikibot.Page(SITE, info['talkpage']))
    return data



def followInstructions(info):
    #verify all required parameters are there
    if not info.has_key('mask') or not info.has_key('target'):
        return '* [[:%s]] has an incorrectly configured template.' % info['talkpage']
    #verify we can edit the target, otherwise just skip it
    #hopefully this will save processing time
    indexPage = pywikibot.Page(SITE, info['target'])
    talkPage = pywikibot.Page(SITE, info['talkpage'])
    try:
        indexPageOldText = indexPage.get()
    except pywikibot.exceptions.IsRedirectPage:
        indexPage = indexPage.getRedirectTarget()
        indexPageOldText = indexPage.get()
    except pywikibot.exceptions.NoPage:
        return '* [[:%s]] does not have the safe string.' % info['talkpage']
    if not __okToEdit(indexPageOldText):
        return '* [[:%s]] does not have the safe string.' % info['talkpage']
    edittime = pywikibot.Timestamp.fromISOformat(indexPage.editTime())
    twelvehr = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    if twelvehr < edittime:
        print 'Edited %s less than 12 hours ago. skipping.' % indexPage.title()
        return
    #looks good, lets go
    data = {}
    #first process the mask
    masks = getMasks(info)
    data['archives'] = masks
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
    for page in data['archives']:
        parsed = parseArchive(page)
        data['parsed'].extend(parsed)
    #build the index      
    indexText = __buildIndex(data['parsed'], data['template'], info)
    print '>>>Will edit %s' % indexPage.title()
    #pywikibot.showDiff(indexPageOldText, indexText)
    indexPage.put_async(indexText, 'BOT: Updating index (Trial [[Wikipedia:Bots/Requests for approval/Legobot 15|BRFA]])')
    return '* Successfully indexed [[%s]] to [[%s]].\n' % (talkPage.title(), indexPage.title())

def __okToEdit(text):
    return bool(re.search('<!-- (HBC Archive Indexerbot|Legobot) can blank this -->', text))


def __buildIndex(parsedData, template, info):
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
    reportInfo = 'Report generated based on a request from [[%s]]. It matches the following masks: ' % pywikibot.Page(SITE, info['talkpage']).title()
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


def parseArchive(page):
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
    threads = splitIntoThreads(text)
    data = list()
    for thread in threads:
        d = {}
        d['topic'] = thread['topic']
        while d['topic'].startswith(' '):
            d['topic'] = d['topic'][1:]
        d['link'] = '[[%s#%s]]' % (page.title(), __cleanLinks(d['topic']))
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
            parsed = mwToEpoch(mw)
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
            
        d['first'] = epochToMW(earliest)
        d['firstepoch'] = earliest
        d['last'] = epochToMW(last)
        d['lastepoch'] = last
        if not d.has_key('duration'):
            d['duration'] = humanReadable(last - earliest)
            d['durationsecs'] = last - earliest
        data.append(d)
    return data

def splitIntoThreads(text):
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

def __cleanLinks(link):
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


def epochToMW(timestamp):
    """
    Converts a unix epoch time to a mediawiki timestamp
    """
    if type(timestamp) == type(''):
        return timestamp
    struct = time.gmtime(timestamp)
    return time.strftime('%H:%M, %d %B %Y', struct)
    
def mwToEpoch(timestamp):
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


def humanReadable(seconds):
    return str(datetime.timedelta(seconds=seconds))

