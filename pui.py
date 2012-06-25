#!/usr/bin/python
# -*- coding: utf-8  -*
#$ -m ae
 
#
# (C) Legoktm 2008-2012, MIT License
# Originally written for Pywikipedia, converted over to rewrite branch.
# 
 
import re
import pywikibot

site=pywikibot.getSite()
page = pywikibot.Page(site,'Wikipedia:Possibly unfree files')
wikitext = page.get()
wikitext = re.compile(r'\n==New listings==', re.IGNORECASE).sub(r'\n*[[/{{subst:#time:Y F j|-14 days}}]]\n==New listings==', wikitext)
EditMsg = 'Adding new day to holding cell'
page.put(wikitext,EditMsg)
