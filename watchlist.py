#!/usr/bin/python


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
