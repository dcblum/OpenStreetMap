# Majority of Code provided by Udacity later edited by myself, David Blum
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus

import schema

OSM_PATH = "Irvine.osm"

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


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item] = element.get(item)
        for elem in element:
            if elem.tag == 'tag':
                if not re.search(PROBLEMCHARS, elem.attrib['k']):
                    # If there are no problem chars...
                    tags.append(shape_tag(elem, node_attribs))

        return {'node': node_attribs, 'node_tags': tags}


    elif element.tag == 'way':
        position = 0
        for item in way_attr_fields:
            way_attribs[item] = element.get(item)
        for elem in element:
            if elem.tag == 'nd':
                node = {}
                node['id'] = way_attribs['id']
                node['node_id'] = elem.get('ref')
                node['position'] = position
                position += 1
                way_nodes.append(node)

            if elem.tag == 'tag':
                if not re.search(PROBLEMCHARS, elem.attrib['k']):
                    # If there are no problem chars...
                    tags.append(shape_tag(elem, way_attribs))

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def shape_tag(elem, attribs):
    '''Modifies tags from shape_element. Uses attributes from higher level tag'''

    tags = {}
    # Splits tag if colon present. Will only split the last colon in string.
    if re.search(LOWER_COLON, elem.attrib['k']):
        elem_split = elem.attrib['k'].split(':', 1)
        tags['key'] = elem_split[1]
        tags['type'] = elem_split[0]
    else:
        tags['key'] = elem.get('k')
        tags['type'] = 'regular'

    tags['id'] = attribs['id']

    # Audits street value in tag based on function update_name
    if tags['key'] == 'street':
        tags['value'] = update_name(elem.get('v'), mapping)

    # Finds and assigns postcode
    elif tags['key'] == 'postcode':
        postcode = elem.get('v')
        tags['value'] = postcode
        # Audits postcode
        postcode_split = re.split('[ -]', postcode)
        for item in postcode_split:
            if len(item) == 5:
                tags['value'] = item
    else:
        tags['value'] = elem.get('v')

    return tags

#------------------------------------------------------------#
#
#------------------------------------------------------------#
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Trail", "Parkway", "Ridge", "Commons", "Way", "Vista", "Terrace", "Circle", "Glen", "Grove", "Hill", "South", "East", "West", "North", "Tree", "Valley", "Creek", "Canyon", "Brook", "Bloom", "Springs", "Verde", "Arbor", "Center", "Loop"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Blvd" : "Boulevard",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "CT" : "Court",
            "Rd" : "Road",
            "Rd." : "Road",
            "PKWY" : "Parkway",
            "Pkwy." : "Parkway"}

def update_name(name, mapping):
    name_split = name.split()
    for e in range(len(name_split)):
        if name_split[e] in mapping:
            name_split[e] = mapping[name_split[e]]

    name = " ".join(name_split)
    return name


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


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


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

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

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

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

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
    process_map(OSM_PATH, validate=True) # Run to actually process mapping
