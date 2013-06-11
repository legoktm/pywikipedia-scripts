#!/usr/bin/env python
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
import re
regex = re.compile('# \[\[(?P<source>.*?)\]\] to \[\[(?P<target>.*?)\]\]')
site = pywikibot.Site()
control = pywikibot.Page(site, 'User:BrownHairedGirl/Film lists for renaming')
text = control.get()
summary = 'Bot: renaming per [[WP:NCLIST]] and [[Talk:Bengali_films_of_2012#Requested_move|requested move]]'
errors = list()
for line in text.splitlines():
    if not line.startswith('#'):
        continue
    s= regex.search(line)
    if not s:
        print 'UHOH'
        print line
        errors.append(line)
        continue
    original = pywikibot.Page(site, s.group('source'))
    print '{source} --> {target}'.format(**s.groupdict())
    try:
        original.move(s.group('target'), summary)
    except:
        print 'didnt work.'
        errors.append(line)
print 'saving errors'
with open('errors.txt','w') as f:
    f.write('\n'.join(errors))
print 'done!'