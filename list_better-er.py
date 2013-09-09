import mwparserfromhell

bad = """
* one line

* two lines

== header ==
* one line
* two line

* three line
"""


def fix_text(text):
    code = mwparserfromhell.parse(text)
    newtext = ''
    for x in code.nodes:
        flag = False
        #print repr(x)
        index = code.nodes.index(x)
        if index != 0 and isinstance(x, mwparserfromhell.nodes.text.Text):
            if x.endswith('\n\n'):
                if isinstance(code.nodes[index-1], mwparserfromhell.nodes.tag.Tag) and str(code.nodes[index-1]) == '*':
                    if len(code.nodes) >= index + 1:
                        if isinstance(code.nodes[index+1], mwparserfromhell.nodes.tag.Tag) and str(code.nodes[index+1]) == '*':
                            #print 'trimming'
                            flag = True
                            newtext += unicode(x)[:-1]
        if not flag:
            newtext += unicode(x)
    return newtext
