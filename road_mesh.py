#!/usr/bin/python3

from OSMPythonTools.overpass import Overpass
from OSMPythonTools.nominatim import Nominatim
# from OSMPythonTools.overpass import overpassQueryBuilder

import argparse

WAY_NODES_CACHE = {}
NODE_WAYS_CACHE = {}

def way_nodes(way_id):
    """Get the OSMPythonTools nodes for a way."""
    global WAY_NODES_CACHE
    global NODE_WAYS_CACHE
    if way_id in WAY_NODES_CACHE:
        return WAY_NODES_CACHE[way_id]
    nodes_result = OVERPASS.query("""way(%s); out geom;""" % way_id)
    nodes = []
    # collect the ways of the street
    for way in nodes_result.elements():
        nodes += way.nodes()
    WAY_NODES_CACHE[way_id] = nodes
    for node in nodes:
        node_id = node.id()
        if node_id in NODE_WAYS_CACHE:
            NODE_WAYS_CACHE[node_id].add(way_id)
        else:
            NODE_WAYS_CACHE[node_id] = set([way_id])
    return nodes

def way_joiners(way_id):
    "Get the OSMPythonTools ways joining a way."
    return list(OVERPASS.query("""(way(%s);way(around:0)[highway~"."];); out geom;""" % way_id).elements())

class Node(object):

    pass

    def __init__(self, node, initial_street):
        self.pynode = node
        self.n_id = node.id()
        self.streets = set([initial_street])

    def __repr__(self):
        return "<node " + str(self.n_id) + ": " + str(self.pynode) + " on " + ",".join((str(s) for s in self.streets)) + ">"

    def add_way(self, way_id):
        self.streets.add(way_id)

    def ref_count(self):
        return len(self.streets)

class Segment(object):

    pass

    def __init__(self, name, s_type, s_id):
        self.name = name
        self.s_type = s_type
        self.s_id = s_id

    def __repr__(self):
        return "<segment " + self.name + ":" + self.s_type + ">"

def collect(way_id, way_name,
            depth,
            all_nodes={}, all_segments={}, all_streets={}):

    for node in way_nodes(way_id):
        node_id = node.id()
        if node_id in all_nodes:
            all_nodes[node_id].add_way(way_id)
        else:
            all_nodes[node_id] = Node(node, way_id)

    for joiner in way_joiners(way_id):
        j_name = joiner.tag('name')
        if j_name is not None:
            j_id = joiner.id()
            if j_name in all_streets:
                all_streets[j_name].add(j_id)
            else:
                all_streets[j_name] = set([j_id])
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
    result = OVERPASS.query(query)
    return result.elements()[0].id()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Tirana")
    parser.add_argument("--county", default="Tirana")
    parser.add_argument("--country", default="Albania")
    parser.add_argument("--start", "-s", default="Rruga Urani Pano")
    parser.add_argument("--depth", "-d", type=int, default=3)
    parser.add_argument("--verbose", "-v", action='store_true')
    args = parser.parse_args()

    global OVERPASS

    OVERPASS = Overpass()
    nominatim = Nominatim()

    starting_area = nominatim.query('%s, %s, %s' % (
                             args.city, args.county, args.country)).areaId()

    nodes, segments, streets = collect(
        way_id_from_name(args.start,
                         starting_area),
        args.start, args.depth)
    print("nodes")
    for node in sorted(nodes.keys()):
        print("  ", node, nodes[node])
    print("segments")
    for segment in sorted(segments.keys()):
        print("  ", segment, segments[segment])
    print("streets")
    for street in sorted(streets.keys()):
        print("  ", street, streets[street])

if __name__ == '__main__':
    main()
