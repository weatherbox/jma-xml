# -*- coding: utf-8 -*-
import json
from datetime import datetime as dt
import datetime
import gzip

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

    last_update_utc = dt.strptime(prefjson['lastupdate'], "%Y%m%d%H%M%S")
    return last_update_utc


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
    last_update_utc = dt.strptime(prefdata['lastupdate'], "%Y%m%d%H%M%S")
    return last_update_utc


def download(type):
    key = 'warning/' + type + '.json.gz'
    file = '/tmp/' + key.replace('/', '-')
    s3_client.download_file('vector-tile', key, file)

    with gzip.open(file) as f:
        return json.loads(f.read(), 'utf-8')

def upload(type, jsondata):
    key = 'warning/' + type + '.json.gz'
    jsonfile = '/tmp/' + type + '.json.gz'

    with gzip.open(jsonfile, 'w') as f:
        f.write(json.dumps(jsondata, ensure_ascii=False).encode('utf-8'))

    s3_client.upload_file(jsonfile, 'vector-tile', key,
        ExtraArgs={
            'ContentType': 'application/json; charset=utf-8',
            'ACL': 'public-read',
            'ContentEncoding': 'gzip'})

    print 'upload', jsonfile


if __name__ == '__main__':
    import sys
    process(sys.argv[1], {}, {})


