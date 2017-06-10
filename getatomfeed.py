# -*- coding: utf-8 -*-
import feedparser

url = 'http://www.data.jma.go.jp/developer/xml/feed/extra.xml'

def fetch():
    atom = feedparser.parse(url)
    print atom.updated

    for entry in atom.entries:
        if entry.title == u'気象警報・注意報（Ｈ２７）':
            print entry.title, entry.content[0]['value']
            print entry.links[0]['href']



if __name__ == '__main__':
    fetch()

