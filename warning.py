# -*- coding: utf-8 -*-
import json
from datetime import datetime as dt

import warningxml

import boto3
s3_client = boto3.client('s3')

def check():
    return


def process(url, prefjson, cityjson):
    prefdata, citydata, report_time = warningxml.parse(url)

    for prefcode in prefdata.keys():
        prefjson[prefcode] = prefdata[prefcode]
    prefjson['lastupdate'] = report_time
    print json.dumps(prefjson, ensure_ascii=False)

    for citycode in citydata.keys():
        cityjson[citycode] = citydata[citycode]
    cityjson['lastupdate'] = report_time
    print json.dumps(cityjson, ensure_ascii=False)


def download(type):
    key = 'warning/' + type + '.json'
    file = '/tmp/' + key.replace('/', '-')
    s3_client.download_file('vector-tile', key, file)

    with open(file) as f:
        return json.load(f)

def upload(type, jsondata):
    key = 'warning/' + type + '.json'
    jsonfile = '/tmp/' + type + '.json'

    with open(jsonfile, 'w') as f:
        f.write(json.dumps(jsondata, ensure_ascii=False))

        s3_client.upload_file(jsonfile, 'vector-tile', key,
            ExtraArgs={'ContentType': "application/json"})


if __name__ == '__main__':
    import sys
    process(sys.argv[1], {}, {})


