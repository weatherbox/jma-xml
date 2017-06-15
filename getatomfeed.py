# -*- coding: utf-8 -*-
from datetime import datetime as dt
import feedparser

import warning

url = 'http://www.data.jma.go.jp/developer/xml/feed/extra.xml'
url_long = 'http://www.data.jma.go.jp/developer/xml/feed/extra_l.xml'

def fetch():
    atom = feedparser.parse(url)
    last_update_utc = warning.check()
    xmllist = []
    print last_update_utc

    for entry in atom.entries:
        if entry.title == u'気象警報・注意報（Ｈ２７）':
            updated_utc = dt.strptime(entry.updated[:-1], "%Y-%m-%dT%H:%M:%S")
            print updated_utc

            if updated_utc > last_update_utc:
                print entry.title, entry.content[0]['value'], entry.updated
                xmllist.append(entry.links[0]['href'])

    if len(xmllist):
        warning.processall(reversed(xmllist))


def init():
    atom = feedparser.parse(url_long)
    xmlpref = {}

    for entry in atom.entries:
        if entry.title == u'気象警報・注意報（Ｈ２７）':
            pref = entry.content[0]['value'][1:4]

            if not pref in xmlpref:
                xmlpref[pref] = entry.links[0]['href']

    warning.processall(xmlpref.values(), init=True)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        init()
    else:
        fetch()

