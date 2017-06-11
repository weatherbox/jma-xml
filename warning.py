# -*- coding: utf-8 -*-
from datetime import datetime as dt
import requests
import xmltodict

def parse(url):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    xml = xmltodict.parse(res.text.encode('utf-8'))

    # status check
    if xml['Report']['Control']['Status'] != u'通常':
        return

    data = {}

    print xml['Report']['Head']['Title']
    timestr = xml['Report']['Head']['ReportDateTime']
    report_time = dt.strptime(timestr[:-6], "%Y-%m-%dT%H:%M:%S")
    print report_time
    print xml['Report']['Head']['Headline']['Text']

    pref_warning = xml['Report']['Body']['Warning'][0]
    for kind in pref_warning['Item']['Kind']:
        print kind['Name']

    print pref_warning['Item']['Area']['Code']


    city_warnings = xml['Report']['Body']['Warning'][3]
    for city in city_warnings['Item']:
        print city['Area']['Name']

        if isinstance(city['Kind'], list):
            for kind in city['Kind']:
                print kind['Name']

        else:
            if city['Kind']['Status'] != u'発表警報・注意報はなし':
                print city['Kind']['Name']

    return data


if __name__ == '__main__':
    import sys
    parse(sys.argv[1])

