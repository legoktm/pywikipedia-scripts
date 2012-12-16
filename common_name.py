#!/usr/bin/env python
"""
Copyright (C) 2012 Legoktm, Riley Huntley

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
import wikipedia as pywikibot
import re
regex = re.compile('# \[\[(?P<source>.*?)\]\] to \[\[(?P<target>.*?)\]\]')
site = pywikibot.getSite()
template = pywikibot.Page(site, 'Template:Italic title')
all = [p.title(withNamespace=False).lower() for p in template.getReferences(redirectsOnly=True)]
t_regex = re.compile('\{\{'+'|'.join(all)+'\}\}', flags=re.IGNORECASE)
control = pywikibot.Page(site, 'User:Italic title bot/Common name for renaming')
text = control.get()
summary = 'Robot: Renaming scientific name to common name per [[WP:COMMONAME]]'
errors = list()
for line in text.splitlines():
    if not line.startswith('#'):
        continue
    s= regex.search(line)
    if not s:
        print 'Uh Oh'
        print line
        errors.append(line)
        continue
    original = pywikibot.Page(site, s.group('source'))
    print '{source} --> {target}'.format(**s.groupdict())
    try:
        original.move(s.group('target'), summary)
        moved = True
    except:
        print 'Didn\'t work.'
        errors.append(line)
        moved = False
    if moved:
        continue
    #remove the template
    page = pywikibot.Page(site, s.group('target'))
    text = page.get()
    newtext = t_regex.sub('', text).strip()
    pywikibot.showDiff(text, newtext)
    page.put(newtext, 'Bot: Removing {{italic title}}')
print 'Saving errors'
with open('errors.txt','w') as f:
    f.write('\n'.join(errors))
print 'Done!'
