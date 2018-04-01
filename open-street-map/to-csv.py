#!/usr/bin/python
# -*- coding: utf-8 -*-
#to csv
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

# import cerberus

import schema

OSM_PATH = "calgary_canada.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def clean_tag(tag):
    if tag.attrib['k'] == "addr:street":
        tag.attrib['v'] = update_name(tag.attrib['v'], mapping)
    elif tag.attrib['k'] == "phone":
        tag.attrib['v'] = update_phone(tag.attrib['v'])
    elif tag.attrib['k'] == "addr:postcode":
        tag.attrib['v'] = update_zip(tag.attrib['v'])
    return tag


def shape_tag(el, tag):
    tag_cleaned = clean_tag(tag)  # 调用清洗好数据的函数
    tag_dict = {
        'id': el.attrib['id'],
        'key': tag_cleaned.attrib['k'],  # 调用清洗好的数据
        'value': tag_cleaned.attrib['v'],
        'type': 'regular'
    }
    if LOWER_COLON.match(tag_dict['key']):
        tag_dict['type'], _, tag_dict['key'] = tag_dict['key'].partition(':')
    return tag_dict


def shape_way_node(el, i, nd):
    return {
        'id': el.attrib['id'],
        'node_id': nd.attrib['ref'],
        'position': i
    }


def shape_element(el, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    #     tags = []  # Handle secondary tags the same way for both node and way elements



    tags = [shape_tag(el, t) for t in el.iter('tag')]  # 从中取出“tag”的内容，把它命名为t。调用shape_tag函数。
    if el.tag == 'node':
        node_attribs = {f: el.attrib[f] for f in node_attr_fields}
        return {'node': node_attribs, 'node_tags': tags}
    elif el.tag == 'way':
        way_attribs = {f: el.attrib[f] for f in way_attr_fields}

        way_nodes = [shape_way_node(el, i, nd)
                     for i, nd in enumerate(el.iter('nd'))]
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


            # def validate_element(element, validator, schema=SCHEMA):
            #  """Raise ValidationError if element does not match schema"""
            # if validator.validate(element, schema) is not True:
            # field, errors = next(validator.errors.iteritems())
            # message_string = "\nElement of type '{0}' has the following errors:\n{1}"
            # error_string = pprint.pformat(errors)

            # raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'wb') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        #  validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            # if el:
            #  if validate is True:
            # validate_element(el, validator)

            if element.tag == 'node':
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
            elif element.tag == 'way':
                ways_writer.writerow(el['way'])
                way_nodes_writer.writerows(el['way_nodes'])
                way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)



