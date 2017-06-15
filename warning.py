# -*- coding: utf-8 -*-
import json
from datetime import datetime as dt
import datetime
import codecs

import warningxml

import boto3
s3_client = boto3.client('s3')


def processall(urllist, init=False):
    if init:
        prefjson = {}
        cityjson = {}
    else:
        prefjson = download('pref')
        cityjson = download('city')

    for url in urllist:
        prefjson, cityjson = process(url, prefjson, cityjson)

    upload('pref', prefjson)
    upload('city', cityjson)


def process(url, prefjson, cityjson):
    prefdata, citydata, report_time = warningxml.parse(url)

    for prefcode in prefdata.keys():
        prefjson[prefcode] = prefdata[prefcode]
    prefjson['lastupdate'] = report_time

    for citycode in citydata.keys():
        cityjson[citycode] = citydata[citycode]
    cityjson['lastupdate'] = report_time

    return prefjson, cityjson


def check():
    prefdata = download('pref')
    last_update = dt.strptime(prefdata['lastupdate'], "%Y%m%d%H%M%S")
    last_update_utc = last_update - datetime.timedelta(hours=9)
    return last_update_utc


def download(type):
    key = 'warning/' + type + '.json'
    file = '/tmp/' + key.replace('/', '-')
    s3_client.download_file('vector-tile', key, file)

    with open(file) as f:
        return json.loads(f.read(), 'utf-8')

def upload(type, jsondata):
    key = 'warning/' + type + '.json'
    jsonfile = '/tmp/' + type + '.json'

    with codecs.open(jsonfile, 'w', 'utf-8') as f:
        f.write(json.dumps(jsondata, ensure_ascii=False))

    s3_client.upload_file(jsonfile, 'vector-tile', key,
        ExtraArgs={
            'ContentType': 'application/json; charset=utf-8',
            'ACL': 'public-read'})


if __name__ == '__main__':
    import sys
    process(sys.argv[1], {}, {})


