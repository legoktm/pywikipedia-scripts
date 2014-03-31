#!/usr/bin/env python
from __future__ import unicode_literals

import datetime
import mwparserfromhell
import pywikibot
import re

site = pywikibot.Site('en', 'wikipedia')

GA_SUBPAGES = ['Agriculture, food and drink', 'Art and architecture', 'Engineering and technology',
               'Geography and places', 'History', 'Language and literature', 'Mathematics', 'Music', 'Natural sciences',
               'Philosophy and religion', 'Social sciences and society', 'Sports and recreation',
               'Media and drama', 'Warfare', 'Video games']

ARTICLE_HISTORY = ['Article History', 'Article milestones', 'ArticleHistory', 'Articlehistory', 'Article milestones']


def get_facs_to_handle(promoted=True):
    monthyear = datetime.datetime.utcnow().strftime('%B %Y')
    if promoted:
        prefix = 'Featured log'
    else:
        prefix = 'Archived nominations'
    monthpage = pywikibot.Page(site, 'Wikipedia:Featured article candidates/' + prefix + '/' + monthyear)
    data = {}
    # FIXME: HAAAAAAAAAAAACK
    # Assumes that log will have <100 edits
    print 'Fetching log page history'
    site.loadrevisions(monthpage, getText=True, rvdir=False,
                       step=100, total=100, startid=None)
    hist = monthpage.fullVersionHistory(total=100)  # This should fetch nothing...
    for revision in hist:
        for temp in mwparserfromhell.parse(revision[3]).filter_templates():
            data[temp.name] = (revision[0], revision[1], revision[2])

    return data


def promote_fac(fac_name, rev_info, was_promoted):
    pg = pywikibot.Page(site, fac_name)
    article_title = fac_name.split('/')[1]
    oldid = rev_info[0]
    timestamp = rev_info[1].strftime('%H:%M, %d %B %Y (UTC)')
    username = rev_info[2]
    text = pg.get()
    if was_promoted:
        prom_text = 'promoted'
    else:
        prom_text = 'not promoted'
    if '<!--FAtop-->' in text or '<!--FLtop-->' in text:
        # Already handled
        print '%s has already been handled, skipping.' % fac_name
        return
    print fac_name, oldid
    top_text = "{{{{subst:Fa top|result='''{prom}''' by [[User:{user}|{user}]] {ts} [//en.wikipedia.org/?diff={oldid}]" \
               "}}}}".format(user=username, ts=timestamp, oldid=oldid, prom=prom_text)
    newtext = top_text + '\n' + text + '\n' + '{{subst:Fa bottom}}'
    pg.put(newtext, 'Bot: Archiving FAC')
    article = pywikibot.Page(site, article_title)
    article_text = article.get()
    if was_promoted:
        # add the FA icon, possibly removing the GA icon
        needs_fa_icon = True
        if re.search('\{\{featured\s?(small|article)\}\}', article_text, re.IGNORECASE):
            needs_fa_icon = False
        elif re.search('\{\{(good|ga) article\}\}', article_text, re.IGNORECASE):
            new_article_text = re.sub('\{\{(good|ga) article\}\}', '{{featured article}}', article_text, flags=re.IGNORECASE)
        else:
            new_article_text = '{{featured article}}\n' + article_text
        if needs_fa_icon:
            article.put(new_article_text, 'Bot: Adding {{featured article}}')
    latest_rev = pywikibot.Page(site, article_title).latestRevision()
    article_talk = article.toggleTalkPage()
    article_talk_text = article_talk.get()

    if was_promoted:
        current_status = 'FA'
    else:
        current_status = 'FFAC'

    has_article_history = False
    parsed = mwparserfromhell.parse(article_talk_text)
    for temp in parsed.filter_templates():
        # This might have some false positives, may need adjusting later.
        if was_promoted and temp.has_param('class'):
            temp.get('class').value = 'FA'
        for ah_name in ARTICLE_HISTORY:
            if temp.name.matches(ah_name):
                has_article_history = True
                num = 1
                while temp.has_param('action' + str(num)):
                    num += 1
                prefix = 'action' + str(num)
                temp.add(prefix, 'FAC')
                temp.add(prefix+'date', timestamp.replace(' (UTC)', ''))
                temp.add(prefix+'link', fac_name)
                temp.add(prefix+'result', prom_text)
                temp.add(prefix+'oldid', latest_rev)
                if was_promoted or temp.get('currentstatus') != 'GA':
                    temp.get('currentstatus').value = current_status
                break

    article_talk_text = unicode(parsed)
    if not has_article_history:
        article_talk_text = """
{{{{Article history
|action1=FAC
|action1date={date}
|action1link={link}
|action1result={prom}
|action1oldid={oldid}
|currentstatus={status}
}}}}
""".format(date=timestamp, link=fac_name, oldid=latest_rev, prom=prom_text, status=current_status) + article_talk_text
    article_talk_text = re.sub('\{\{featured article candidates.*?\}\}', '', article_talk_text, flags=re.IGNORECASE)
    article_talk.put(article_talk_text, 'Bot: Updating {{Article history}} after FAC')
    if was_promoted:
        update_ga_listings(article_title)
    quit()


def update_ga_listings(article):
    """
    This whole function is pretty bad.
    We can optimize checking all the subpages by doing a db query
    on the pagelinks table and only look for subpages of "WP:GA"
    """
    for subj in GA_SUBPAGES:
        pg = pywikibot.Page(site, 'Wikipedia:Good articles/' + subj)
        if pg.isRedirectPage():
            pg = pg.getRedirectTarget()
        text = pg.get()
        if not article in text:
            continue
        # This part is weird, but meh
        lines = text.splitlines()
        for line in lines[:]:
            if article in line:
                lines.remove(line)
                break
        pg.put('\n'.join(lines), 'Bot: Removing [[%s]] since it was promoted to FA' % article)
        break


if __name__ == '__main__':
    for was_promoted in [True, False]:
        facs = get_facs_to_handle(promoted=was_promoted)
        for fac, rev_info in facs.iteritems():
            if fac == 'TOClimit':
                continue
            promote_fac(fac, rev_info, was_promoted=was_promoted)