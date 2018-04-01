#!/usr/bin/python
# -*- coding: utf-8 -*-
#clean zip code format
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "calgary_canada.osm"
d = re.compile(r'([A-Z]\d){3}')  # 匹配缺失空格的邮编。


def audit_zipcode(invalid_zipcodes, zipcode):
    if d.search(zipcode):
        invalid_zipcodes.add(zipcode)


def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    invalid_zipcodes = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes, tag.attrib['v'])

    osm_file.close()

    return invalid_zipcodes


def update_zip(zipcode):
    if d.search(zipcode):
        zipcode = zipcode[:3] + " " + zipcode[3:]
        return zipcode
    else:
        return zipcode


if __name__ == '__main__':
    invalid_zipcodes = audit(OSMFILE)
    print invalid_zipcodes
    for zipcode in invalid_zipcodes:
        better_zipcode = update_zip(zipcode)
        print zipcode, "=>", better_zipcode