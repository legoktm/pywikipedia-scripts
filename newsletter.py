#!/usr/bin/python
#
# (C) 2012, Legoktm under the MIT License
# Utilizes the rewrite branch of Pywikipedia
# Automatically puts a message on a list of pages

import re
import pywikibot

#Set default pages
# .css pages are picked since they can only be edited by myself or an admin.
list = 'User:Legoktm/spamlist.css'
message = 'User:Legoktm/message.css'
summary = 'User:Legoktm/summary.css'
site = pywikibot.getSite()

def main():
    spamlist = pywikibot.Page(site, list).get()
    text = pywikibot.Page(site, message).get()
    editMsg = pywikibot.Page(site, summary).get()
    #Parse the list    
    list = re.compile(r'\[\[(.*?)\]\]', re.IGNORECASE).sub(r'\1', spamlist)
    for title in list:
        pg = pywikbot.Page(site, title)
        pg.put(text, editMsg, minorEdit=False)


if __name__ == "__main__":
    main()
