# Majority of Code provided by Udacity later edited by myself, David Blum
import xml.etree.cElementTree as ET
import pprint
import re

'''Finds the number of unique users in the OSM database'''

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        uid = element.get('uid')
        if uid != None:
            users.add(uid)

    return users


def test():

    users = process_map('Irvine.osm')
    pprint.pprint(len(users))
    #assert len(users) == 6



if __name__ == "__main__":
    test()
