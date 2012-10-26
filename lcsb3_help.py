#!/usr/bin/python
#
# (C) Legoktm 2012, MIT License
# 
import pywikibot
import oursql


def count():
    db = oursql.connect(db='u_sigma_webcite_p', host="sql-user-l.toolserver.org", read_default_file="/home/legoktm/.my.cnf")
    cur = db.cursor()
    cur.execute("SELECT table_name, table_rows     FROM INFORMATION_SCHEMA.TABLES     WHERE TABLE_SCHEMA = 'u_sigma_webcite_p' AND TABLE_NAME='new_links';")
    query = cur.fetchall()
    res = query[0][1]
    db.close()
    return res


site = pywikibot.Site()
page = pywikibot.Page(site, "User:lowercase sigmabot III/Counting")
page.put(unicode(res), 'BOT: Updating lcsb queued count')
