"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "Irvine.osm"
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
                if is_street_name(tag) and len(tag.attrib['v'].split(' ')) > 1:
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def user_choice(choices, question):
    choice = None
    while choice not in choices:
        choice = raw_input("\n" + question + "\n").upper()
    return choice


def update_name(name, mapping):
    name_split = name.split()
    for e in range(len(name_split)):
        if name_split[e] in mapping:
            name_split[e] = mapping[name_split[e]]

    # print name_split
    name = " ".join(name_split)

    # Double Check update_name
    check = 0
    while check = 0:
        update =  user_choice (['YES', 'Y', 'NO', 'N'], "\nShould This be Mapped?\n" + name + " => " + better_name)
        if update == 'YES' or update == 'Y':
            check = 1
        else:
            better_name = string(raw_input())


    return name


def test():
    st_types = audit(OSMFILE)
    #assert len(st_types) == 3
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            if name != better_name:
                print name, "=>", better_name
            '''
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"
            '''

if __name__ == '__main__':
    test()
