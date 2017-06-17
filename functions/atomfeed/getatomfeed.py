# -*- coding: utf-8 -*-
from datetime import datetime as dt
import datetime
import feedparser

import warning

last_update = None

url = 'http://www.data.jma.go.jp/developer/xml/feed/extra.xml'
url_long = 'http://www.data.jma.go.jp/developer/xml/feed/extra_l.xml'

def fetch():
    global last_update
    if last_update is None:
        last_update = warning.check()
    print last_update

    atom = feedparser.parse(url)
    xmllist = []

    for entry in atom.entries:
        if entry.title == u'気象警報・注意報（Ｈ２７）':
            updated = dt.strptime(entry.updated[:-4], "%Y-%m-%dT%H:%M") + datetime.timedelta(hours=9)

            if updated > last_update:
                print entry.updated, entry.title, entry.content[0]['value']
                xmllist.append(entry.links[0]['href'])

    if len(xmllist):
        last_update = warning.processall(reversed(xmllist))


def initall():
    atom = feedparser.parse(url_long)
    xmlpref = {}

    for entry in atom.entries:
        if entry.title == u'気象警報・注意報（Ｈ２７）':
            pref = entry.content[0]['value'][1:4]

            if not pref in xmlpref:
                xmlpref[pref] = entry.links[0]['href']

    warning.processall(xmlpref.values(), init=True)


# called by aws lambda
def handler(event, context):
    fetch()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        initall()
    else:
        fetch()

