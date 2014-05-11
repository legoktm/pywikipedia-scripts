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
from __future__ import unicode_literals

try:
    import pywikibot
except ImportError:
    import wikipedia as pywikibot
try:
    from pywikibot import pagegenerators
except ImportError:
    import pagegenerators


site = pywikibot.getSite()


def run(gen):
    text = ''
    for temp in gen:
        t = temp.title(withNamespace=False)
        item = [page.title(withNamespace=False) for page in temp.getReferences(redirectsOnly=True, namespaces=[10])]
        if not item:
            continue
        statement = ', '.join('{{tl|'+title+'}}' for title in item)
        text += '* '+statement + " → '''{{tl|%s}}'''\n" % temp.title(withNamespace=False)
    return text


def gen(*args):
    args = list(args)
    args.append('-namespace:10')
    gen = pagegenerators.GeneratorFactory()
    #gen.filterNamespaces(10)
    for arg in pywikibot.handleArgs(*args):
        if arg.startswith('-cat:'):
            print '== [[:%s]] == ' % arg[5:]
        elif arg.startswith('-catr:'):
            print '== [[:%s]] == ' % arg[6:]
        gen.handleArg(arg)
    return gen.getCombinedGenerator()

text = ''
text += run(gen('-cat:Category:Non-free use rationale templates'))
text += run(gen('-cat:Category:Wikipedia non-free file copyright tags'))
text += run(gen('-cat:Category:File namespace templates'))
text += run(gen('-cat:Category:File maintenance templates'))
text += run(gen('-cat:Category:Marker templates'))
text += run(gen('-cat:Category:Restriction tags'))
print text
pywikibot.Page(pywikibot.Site(), 'User:Legoktm/AWB/TR').put(text, 'Updating list of redirects')