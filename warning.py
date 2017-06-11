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

    # head
    timestr = xml['Report']['Head']['ReportDateTime']
    report_time = dt.strptime(timestr[:-6], "%Y-%m-%dT%H:%M:%S")
    comment = xml['Report']['Head']['Headline']['Text']

    print xml['Report']['Head']['Title'], report_time

    # 気象警報・注意報（府県予報区等）
    prefdata = {}
    pref_warnings = xml['Report']['Body']['Warning'][0]
    items = pref_warnings['Item']
    if not isinstance(items, list): items = [items]
    for pref in items:
        warnings = warnings_tolist(pref)
        code = pref['Area']['Code']

        prefdata[code] = {
            'name': pref['Area']['Name'],
            'status': warning_status(warnings),
            'warnings': pref_warnings,
            'report_time': report_time,
            'comment': comment
        }

    # 気象警報・注意報（市町村等）
    city_warnings = xml['Report']['Body']['Warning'][3]
    citydata = parse_city_warnings(city_warnings)

    # 量的予想時系列（市町村等）
    # 複雑....

    return prefdata, citydata


def parse_city_warnings(city_warnings):
    citydata = {}
    for city in city_warnings['Item']:
        code = city['Area']['Code']
        warnings = warnings_tolist(city)
        
        citydata[code] = {
            'name': city['Area']['Name'],
            'status': warning_status(warnings),
            'warnings': warnings
        }

    return citydata


def warnings_tolist(item):
    warnings = []

    if isinstance(item['Kind'], list):
        for kind in item['Kind']:
            warnings.append(kind['Name'])

    else:
        if item['Kind']['Status'] != u'発表警報・注意報はなし':
            warnings.append(item['Kind']['Name'])

    return warnings


def warning_status(warnings):
    # emergency | warning | advisory | none
    status = 'none'
    if len(warnings):
        if len([w for w in warnings if w[:-4] == u'特別警報']):
            status = 'emergency'
        elif len([w for w in warnings if w[:-2] == u'警報']):
            status = 'warning'
        else:
            status = 'advisory'

    return status


if __name__ == '__main__':
    import sys
    prefdarta, citydata = parse(sys.argv[1])


