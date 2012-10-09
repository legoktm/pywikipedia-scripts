#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import pywikibot
import mwparserfromhell

class AWBGenFixes():
    def __init__(self, site):
        #robot.Robot.__init__(self, task=23)
        self.site = site
        self.date_these = []
        self.redirects = {}

    def load(self, tr=None, dt=None):
        self.load_templates(dt=dt)
        self.load_redirects(tr=tr)

    def load_templates(self, dt=None):
        if dt:
            page = dt
        else:
            page = pywikibot.Page(self.site, 'Wikipedia:AutoWikiBrowser/Dated templates')
        text = page.get()
        code = mwparserfromhell.parse(text)
        for temp in code.filter_templates():
            if temp.name.lower() == 'tl':
                self.date_these.append(temp.get(1).value.lower())

    def load_redirects(self, tr=None):
        if tr:
            page = tr
        else:
            page = pywikibot.Page(self.site, 'Wikipedia:AutoWikiBrowser/Template redirects')
        text = page.get()
        for line in text.splitlines():
            if not '→' in line:
                continue
            split = line.split('→')
            if len(split) != 2:
                continue
            code1=mwparserfromhell.parse(split[0])
            code2=mwparserfromhell.parse(split[1])
            destination = code2.filter_templates()[0].get(1).value #ehhhh
            for temp in code1.filter_templates():
                if temp.name.lower() == 'tl':
                    name = temp.get(1).value
                    self.redirects[name.lower()] = destination
                    self.redirects[destination.lower()] = destination

    def do_page(self, text):
        code = mwparserfromhell.parse(text)
        summary= {}
        for temp in code.filter_templates(recursive=True):
            if temp.name.lower() in self.redirects.keys():
                temp.name = self.redirects[temp.name.lower()]
                if temp.name.lower() in self.date_these:
                    if not temp.has_param('date'):
                        temp.add('date','{{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}')
                        if temp.name.lower() in summary.keys():
                            summary[temp.name.lower()] += 1
                        else:
                            summary[temp.name.lower()] = 1
        msg = ', '.join('{{%s}} (%s)' % (item, summary[item]) for item in summary.keys())
        return unicode(code), msg


