#!/usr/bin/python
# -*- coding: utf-8 -*-

#clean street name


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "calgary_canada.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Northeast", "Northwest", "Southeast",
            "Southwest", "North", "West", "Highway", "Way", "W", "N", "E", "S"]

# UPDATE THIS VARIABLE
mapping = {
    "St.": "Street",
    "SE": "Southeast",
    "SW": "Southwest",
    "S.W.": "Southwest",
    "NE": "Northeast",
    "N.E.": "Northeast",
    "NW": "Northwest",
    "N.W": "Northwest",
    "N.W.": "Northwest",
    "Blvd": "Boulevard"

}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    for word in mapping:
        if name.endswith(word):
            return name.replace(word, mapping[word])

    return name


if __name__ == '__main__':
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name



