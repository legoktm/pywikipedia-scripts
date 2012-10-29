#!/usr/bin/env python
from __future__ import unicode_literals
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

CONVERT_AMPM = {'AM':'a.m.', 'PM':'p.m.'}

import re
import datetime

import requests
import bs4
import pywikibot
import mwparserfromhell
SITE = pywikibot.Site()
HEADERS = {'User-Agent':'HurricaneInfoUpdaterBot - http://enwp.org/User:Legobot'}
COMMENT_THINGY = "<!-- SAME DAY, EDT AND UTC: TIME EDT (TIME UTC) DATE. DIFFERENT DAYS, EDT AND UTC: TIME EDT DATE EDT (TIME UTC DATE UTC) ///NOTICE THE DATE UTC INSIDE THE PARENTHESIS NOT OUTSIDE-->"
class Hurricane:
    """
    A class which should represent each storm
    """
    def __init__(self, url, wikipage):
        """
        @param wikipage Wikipedia page of storm
        @type wikipage pywikibot.Page
        @param url  url to the NHC report
        @type url   unicode
        """
        self.url = url
        self.wikipage = wikipage

    def fetch_info(self):
        r = requests.get(self.url, headers=HEADERS)
        if not r.ok:
            raise
        soup = bs4.BeautifulSoup(r.text)
        self.NHC_report = soup.body.pre.string

    def parse_info(self):
        for line in self.NHC_report.splitlines():
            if line.startswith('LOCATION...'):
                self.LOCATION = {'latc':line[11:15], 'latd':line[15],
                                 'lonc':line[17:21], 'lond':line[21]}
            elif line.startswith('ABOUT'):
                self.ABOUT = line
            elif line.startswith('PRESENT MOVEMENT'):
                self.MOVEMENT = self.parse_movement(line)
            elif line.startswith('MINIMUM CENTRAL PRESSURE'):
                self.PRESSURE = self.parse_pressure(line)
            elif line.startswith('MAXIMUM SUSTAINED WINDS'):
                if not hasattr(self, 'WINDS'):
                    self.WINDS = self.parse_wind(line)
                    self.CATEGORY = self.determine_category(self.WINDS['mph'])
            elif line.startswith('SUMMARY') and 'UTC' in line:
                if not hasattr(self, 'UTC_TIMESTAMP'):
                    self.UTC_TIMESTAMP = self.format_timestamp(self.parse_timestamp(line))+ COMMENT_THINGY

    def parse_movement(self, line):
        if 'STATIONARY' in line:
            return 'STATIONARY'
        line=line[19:]
        match = re.match('(\w{1,3}) OR (\d{1,3}) DEGREES AT (\d{1,3}) MPH...(\d{1,3}) KM/H', line)
        d = {
            'direction':match.group(1),
            'degrees':match.group(2),
            'mph':match.group(3),
            'kmh':match.group(4),
        }
        d['knots'] = self.kmhtkt(int(d['kmh']))
        return d

    def kmhtkt(self, kmh):
        """
        Convert km/h --> knots
        """
        constant = float(1.852)
        return float(kmh)/constant

    def format_movement(self, data):
        if type(data) == str:
            return 'Stationary'
        data['knots'] = int(self.kmhtkt(data['kmh']))
        return '%(direction)s at %(knots)s kt (%(mph)s mph; %(kmh)s km/h)' % data

    def parse_pressure(self, line):
        line=line[27:]
        s=line.split('...')
        mb = s[0].split(' ')[0]
        inch = s[1].split(' ')[0]
        return {'mbar':mb,'inch':inch}

    def format_pressure(self, data):
        return '%(mbar)s [[mbar]] ([[hPa]]; %(inch)s [[inHg]])' % data

    def parse_wind(self, line):
        line=line[26:]
        find = line.find('MPH')
        mph = int(line[:find-1])
        find2 = line.find('KM/H')
        kmh = int(line[find+6:find2-1])
        return {'mph':mph, 'kmh':kmh}

    def format_wind(self, data):
        return '%(mph)s mph (%(kmh)s km/h)' % data

    def determine_category(self, mph):
        if mph <= 38:
            return 'depression'
        elif mph <= 73:
            return 'storm'
        elif mph <= 95:
            return 'cat1'
        elif mph <= 110:
            return 'cat2'
        elif mph <= 129:
            return 'cat3'
        elif mph <= 156:
            return 'cat4'
        else:
            return 'cat5'
    def parse_timestamp(self, line):
        print line
        find = line.find('UTC')
        time = line[find-5:find-1]
        day = datetime.date.today()
        dt = datetime.datetime(day.year, day.month, day.day, int(time[:2]), int(time[2:]))
        self.TIMESTAMP = dt
        return dt

    def format_timestamp(self, dt):
        AST = dt - datetime.timedelta(hours=4)
        AST_AMPM = CONVERT_AMPM[AST.strftime('%p')]
        AST_HR = str(int(AST.strftime('%I')))
        DATE = dt.strftime('%B %d')
        AST_DATE = AST.strftime('%B %d')
        UTC_TIME = dt.strftime('%H%M')
        if AST_DATE == DATE:
            return AST_HR + ' ' + AST_AMPM + ' [[Eastern Daylight Time|EDT]] (' + UTC_TIME + ' [[Coordinated Universal Time|UTC]]) ' + DATE
        else:
            return AST_HR + ' ' + AST_AMPM + ' ' + AST_DATE + ' [[Eastern Daylight Time|EDT]] (' + UTC_TIME + ' '+ DATE + ' [[Coordinated Universal Time|UTC]])'



    def update(self, push=True):
        self.fetch_info()
        self.parse_info()
        print self.LOCATION
        print self.CATEGORY
        print self.ABOUT
        print self.MOVEMENT
        print self.PRESSURE
        print self.WINDS
        #print self.UTC_TIMESTAMP
        #actually update crap
        #return
        text = self.wikipage.get()
        code = mwparserfromhell.parse(text)
        main = pywikibot.Page(self.wikipage.site, '2012 Atlantic hurricane season')
        main_text = main.get()
        main_code = mwparserfromhell.parse(main_text)
        for template in code.filter_templates():
            name = template.name.lower().strip()
            if name == 'Infobox hurricane current'.lower():
                if template.get('name').value.strip() == 'Hurricane Sandy':
                    template.get('time').value = self.UTC_TIMESTAMP
                    template.get('category').value = self.CATEGORY
                    template.get('gusts').value = self.format_wind(self.WINDS)
                    template.get('lat').value = self.LOCATION['latc']
                    template.get(1).value = self.LOCATION['latd']
                    template.get('lon').value = self.LOCATION['lonc']
                    template.get(2).value = self.LOCATION['lond']
                    template.get('movement').value = self.format_movement(self.MOVEMENT)
                    template.get('pressure').value = self.format_pressure(self.PRESSURE)
        pywikibot.showDiff(text, unicode(code))
        if push:
            self.wikipage.put(unicode(code), 'Bot: Updating hurricane infobox. Errors? [[User talk:Legoktm|report them!]]')




def main():
    pg = pywikibot.Page(SITE, 'User:Legobot/Current hurricanes')
    text = pg.get()
    go=False
    for line in text.splitlines():
        if go:
            split = line.split('||')
            if len(split) == 2:
                storm = Hurricane(split[0], pywikibot.Page(SITE, split[1]))
                storm.update(push=True)
            elif len(split) == 3:
                storm1 = Hurricane(split[0], pywikibot.Page(SITE, split[2]))
                if split[1]:
                    storm2 = Hurricane(split[1], pywikibot.Page(SITE, split[2]))
                else:
                    storm1.update(push=True)
                    continue
                storm1.update(push=False)
                storm2.update(push=False)
                if storm1.TIMESTAMP > storm2.TIMESTAMP:
                    print 'Updating storm1'
                    storm1.update(push=True)
                else:
                    print 'Updating storm2'
                    storm2.update(push=True)
        if '<pre>' in line:
            go=True

if __name__ == "__main__":
    main()