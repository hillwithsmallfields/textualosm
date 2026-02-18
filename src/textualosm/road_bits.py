"""Handle bits of roads."""

import time

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

way_nodes_cache = {}
node_ways_cache = collections.defaultdict(set)

def area(city, county, country):
    return nominatim.query('%s, %s, %s' % (city, county, country)).areaId()

def feature_type(feature):
    """Return what type of feature this is, according to which feature type tags are present."""
    tags = feature.tags()
    for x in ('building', 'amenity', 'highway', 'shop', 'tourism', 'office'):
        if x in tags:
            return x
    return None

def way_points(way_id):
    """Get the OSMPythonTools nodes for a way."""
    if way_id in way_nodes_cache:
        return way_nodes_cache[way_id]
    nodes_result = overpass.query("""way(%s); out geom;""" % way_id, timeout=60)
    nodes = []
    # collect the ways of the street
    for way in nodes_result.elements():
        nodes += way.nodes()
    way_nodes_cache[way_id] = nodes
    for node in nodes:
        node_ways_cache[node.id()].add(way_id)
    return [node.geometry()['coordinates'] for node in nodes]

def way_joiners(way_id):
    "Get the OSMPythonTools ways joining a way."
    return list(overpass.query("""(way(%s);way(around:0)[highway~"."];); out geom;""" % way_id, timeout=60).elements())

def way_abutters(way_id, within=5):
    "Get the OSMPythonTools buildings near a way."
    # TODO: get amenities and address-only things too
    log.debug("in way_abutters(%d), within=%d", way_id, within)
    return overpass.query(
        """(way(%s)->.w;
        (
          way(around.w:%d)[building];
          node(around.w:%d)[amenity];
          node(around.w:%d)[shop];
          node(around.w:%d)[office];
        );
        );
        out geom;""" % (way_id, within, within, within, within),
        timeout=60).elements()

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

def street_abutters(initial_way_id, way_name, abutters={}, within=5, depth=0):
    log.debug("getting abutters for %d %s at depth %d", initial_way_id, way_name, depth)
    ab = way_abutters(initial_way_id, within=within)
    log.debug("%d for way %s got %d abutters:", depth, initial_way_id, len(ab))
    for a in ab:
        log.debug("%d  name=%s building=%s street=%s housenumber=%s", depth, a.tag('name'), a.tag('building'), a.tag('addr:street'), a.tag('addr:housenumber'))
    abutters[initial_way_id] = ab
    joiners = way_joiners(initial_way_id)
    log.debug("%d %d joining stretches:", depth, len(joiners))
    for stretch in joiners:
        j_name = stretch.tag('name')
        stretch_id = stretch.id()
        log.debug("%d    got joiner %s name=%s highway=%s geom=%s", depth, stretch, j_name, stretch.tag('highway'), stretch.geometry())
        if j_name == way_name and stretch_id not in abutters:
            log.debug("%d    part of same road: %s", depth, way_name)
            time.sleep(2)
            street_abutters(stretch_id, way_name, abutters, within, depth+1)
    return abutters

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

def way_id_from_name(way_name, area_id):
    """Get an OSM ID for a given name in a given area.
    It might not be unique, as a single named street may be
    represented by multiple OSM ways, but we only need it as a
    starting point."""
    query = """area(%d)->.searchArea;(way["name"="%s"](area.searchArea);); out geom;""" % (area_id, way_name)
    result = overpass.query(query, timeout=60)
    elements = result.elements()
    log.info("got %d way elements for %s", len(elements), way_name)
    return elements[0].id()
