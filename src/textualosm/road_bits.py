"""Handle bits of roads."""

import collections
import logging

from OSMPythonTools.overpass import Overpass
from OSMPythonTools.nominatim import Nominatim
# from OSMPythonTools.overpass import overpassQueryBuilder

overpass = None
nominatim = None

def road_bits_setup():
    global overpass
    global nominatim

    overpass = Overpass()
    nominatim = Nominatim()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def area(city, county, country):
    return nominatim.query('%s, %s, %s' % (city, county, country)).areaId()

def feature_type(feature):
    """Return what type of feature this is, according to which feature type tags are present."""
    tags = feature.tags()
    for x in ('building', 'amenity', 'highway', 'shop', 'tourism', 'office'):
        if x in tags:
            return x
    return None

def fetch_street_data(way_name, area_id, within=5):
    """Fetch all data for a named street in a single Overpass query.

    Returns (street_ways, joiners, abutters):
    - street_ways: OSM way elements forming the named street
    - joiners: OSM way elements that intersect the street (different name)
    - abutters: OSM elements (buildings, amenities, shops, offices) near the street
    """
    query = """
area(%d)->.searchArea;
way["name"="%s"](area.searchArea)->.street;
(
  .street;
  way(around.street:0)[highway~"."];
  way(around.street:%d)[building];
  node(around.street:%d)[amenity];
  node(around.street:%d)[shop];
  node(around.street:%d)[office];
);
out geom;
""" % (area_id, way_name, within, within, within, within)
    log.debug("fetch_street_data: querying for '%s'", way_name)
    elements = overpass.query(query, timeout=60).elements()
    log.debug("fetch_street_data: got %d elements total", len(elements))

    street_ways = []
    joiners = []
    abutters = []
    for element in elements:
        tags = element.tags()
        if 'highway' in tags and tags.get('name') == way_name:
            street_ways.append(element)
        elif 'highway' in tags:
            joiners.append(element)
        elif any(t in tags for t in ('building', 'amenity', 'shop', 'office', 'tourism')):
            abutters.append(element)

    log.debug("fetch_street_data: %d street ways, %d joiners, %d abutters",
              len(street_ways), len(joiners), len(abutters))
    return street_ways, joiners, abutters

class Node:

    """A node, collecting all the streets that meet there."""

    def __init__(self, node, initial_street=None):
        self.pynode = node
        self.n_id = node.id()
        self.streets = set([initial_street]) if initial_street else set()

    def __repr__(self):
        return "<node " + str(self.n_id) + ": " + str(self.pynode) + " on " + ",".join((str(s) for s in self.streets)) + ">"

    def add_way(self, way_id):
        self.streets.add(way_id)

    def ref_count(self):
        return len(self.streets)

class Segment:

    def __init__(self, name, s_type, s_id):
        self.name = name
        self.s_type = s_type
        self.s_id = s_id

    def __repr__(self):
        return "<segment " + self.name + ":" + self.s_type + ">"


def collect(initial_way_id, way_name,
            depth,
            all_nodes=None, all_segments=None, all_streets=None):

    if all_nodes is None:
        all_nodes = collections.defaultdict(Node)
    if all_segments is None:
        all_segments = {}
    if all_streets is None:
        all_streets = collections.defaultdict(set)

    for node in way_nodes(initial_way_id):
        all_nodes[node.id()].add_way(initial_way_id)

    for joiner in way_joiners(initial_way_id):
        j_name = joiner.tag('name')
        if j_name is not None:
            j_id = joiner.id()
            all_streets[j_name].add(j_id)

            if j_id not in all_segments:
                all_segments[j_id] = Segment(j_name, joiner.tag('highway'), j_id)
                if j_name == way_name:
                    # same name, so another part of the same street, so don't increase the depth
                    collect(j_id, j_name, depth, all_nodes, all_segments, all_streets)
                elif depth > 0:
                    collect(j_id, way_name, depth-1, all_nodes, all_segments, all_streets)
    return all_nodes, all_segments, all_streets

