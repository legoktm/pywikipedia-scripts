#!/usr/bin/python
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
from pywikibot import pagegenerators

site = pywikibot.getSite()


def process(category):
	text = ''
	category = pywikibot.Category(category)
	gen = pagegenerators.SubCategoriesPageGenerator(category, recurse = True)
	for subcat in gen:
		print 'Processing %s' %(subcat.title())
		pagegen = pagegenerators.CategorizedPageGenerator(subcat)
		text += '\n==[[:%s]]==' %(subcat.title())
		for page in pagegen:
			text += '\n*%s' %(page.title(asLink = True))
	return text
		

def generate(category, page):
	category = pywikibot.Page(site, category)
	text = process(category)
	page = pywikibot.Page(site, page)
	page.put(text, 'Updating Watchlist')

def main():
	generate('Category:Canadian football', 'User:Legobot/Sandbox')


if __name__ == "__main__":
	main()
