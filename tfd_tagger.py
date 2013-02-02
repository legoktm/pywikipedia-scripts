import pywikibot as p
with open('list.txt','r') as f:
	t=f.read()
tag = '{{Template for discussion/dated|page={{subst:PAGENAME}}|link=Wikipedia:Templates for discussion/Log/2012 December 5#Unused_template:.2A.2Fmeta.2Fshortname.2C_template:.2A.2Fmeta.2Fcolor.2C_template:.2A.2Fmeta.2Fabbr}}'
summary = 'Tagging for [[Wikipedia:Templates_for_discussion/Log/2012_December_5#Unused_template:.2A.2Fmeta.2Fshortname.2C_template:.2A.2Fmeta.2Fcolor.2C_template:.2A.2Fmeta.2Fabbr|TfD discussion]]'
def tagp(page):
	text= stable =page.get()
	if 'Template for discussion/dated'.lower() in text.lower():
		print 'already tagged, skipping'
		return
	text=text.replace('<noinclude>','<noinclude>\n'+tag)
	if not '<noinclude>' in text.lower():
		text+='\n'+tag
	p.showDiff(stable,text)
	page.put(text, summary)
site=p.Site()
for line in t.splitlines():
	if line.isspace() or (not line):
		continue
	try:
		g=p.Page(site, line.strip().encode('utf-8'))
	except UnicodeDecodeError:
		print line + '!!!!!!!!!!!!!!'
	print g
	tagp(g)
