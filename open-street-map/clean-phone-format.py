#!/usr/bin/python
# -*- coding: utf-8 -*-

#clean phone number
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "calgary_canada.osm"
a = re.compile(r'^[^+](\d.*){1,}')  # 匹配不以“+”开头的电话号码


def audit_phone(invalid_phone, phone):
    if a.search(phone):
        invalid_phone.add(phone)


def is_phone(elem):
    return (elem.attrib['k'] == "phone")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    invalid_phone = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    audit_phone(invalid_phone, tag.attrib['v'])

    osm_file.close()

    return invalid_phone


b = re.compile(r'^[4|(](\d.*){1,}')  # 匹配“4或（”开头的电话号码。


def update_phone(phone):
    if b.search(phone):
        phone = "+1" + phone
        phone = phone.replace(".", "")
        return phone
    else:
        return phone


if __name__ == '__main__':
    ph = audit(OSMFILE)
    print (ph)
    for phone in ph:
        better_phone = update_phone(phone)
        print phone, "=>", better_phone