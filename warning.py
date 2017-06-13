# -*- coding: utf-8 -*-
import boto3
from datetime import datetime as dt
import json

import warningxml



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


def download():
    return


def upload():
    return


if __name__ == '__main__':
    import sys
    process(sys.argv[1], {}, {})


