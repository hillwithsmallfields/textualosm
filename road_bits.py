
from OSMPythonTools.overpass import Overpass
from OSMPythonTools.nominatim import Nominatim
# from OSMPythonTools.overpass import overpassQueryBuilder

OVERPASS = None
NOMINATIM = None

def road_bits_setup():
    global OVERPASS
    global NOMINATIM

    OVERPASS = Overpass()
    NOMINATIM = Nominatim()

WAY_NODES_CACHE = {}
NODE_WAYS_CACHE = {}

def area(city, county, country):
    return NOMINATIM.query('%s, %s, %s' % (city, county, country)).areaId()

def way_points(way_id):
    """Get the OSMPythonTools nodes for a way."""
    global WAY_NODES_CACHE
    global NODE_WAYS_CACHE
    if way_id in WAY_NODES_CACHE:
        return WAY_NODES_CACHE[way_id]
    nodes_result = OVERPASS.query("""way(%s); out geom;""" % way_id)
    nodes = []
    # collect the ways of the street
    for way in nodes_result.elements():
        print("adding", len(way.nodes()), "nodes")
        for node in way.nodes():
            print("  adding node", node)
        nodes += way.nodes()
    WAY_NODES_CACHE[way_id] = nodes
    for node in nodes:
        node_id = node.id()
        if node_id in NODE_WAYS_CACHE:
            NODE_WAYS_CACHE[node_id].add(way_id)
        else:
            NODE_WAYS_CACHE[node_id] = set([way_id])
    return [node.geometry()['coordinates'] for node in nodes]

def way_joiners(way_id):
    "Get the OSMPythonTools ways joining a way."
    return list(OVERPASS.query("""(way(%s);way(around:0)[highway~"."];); out geom;""" % way_id).elements())

def way_abutters(way_id, within=10):
    "Get the OSMPythonTools buildings near a way."
    # TODO: get amenities and address-only things too
    return OVERPASS.query(
        """(way(%s)->.w;
        (
          way(around.w:%d)[building];
        );
        );
        out;""" % (way_id, within)).elements()

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

def street_abutters(initial_way_id, way_name, abutters={}, within=25):
    ab = way_abutters(initial_way_id, within=within)
    print("for way", initial_way_id, "got abutters", ab)
    for a in ab:
        print("  ", a.tag('name'), a.tag('building'), a.tag('addr:street'), a.tag('addr:housenumber'))
    abutters[initial_way_id] = ab
    for stretch in way_joiners(initial_way_id):
        j_name = stretch.tag('name')
        stretch_id = stretch.id()
        print("  got joiner", stretch, j_name)
        if j_name == way_name and stretch_id not in abutters:
            print("  part of same road", way_name)
            street_abutters(stretch_id, way_name, abutters)
    return abutters

def collect(initial_way_id, way_name,
            depth,
            all_nodes={}, all_segments={}, all_streets={}):

    for node in way_nodes(initial_way_id):
        node_id = node.id()
        if node_id in all_nodes:
            all_nodes[node_id].add_way(initial_way_id)
        else:
            all_nodes[node_id] = Node(node, initial_way_id)

    for joiner in way_joiners(initial_way_id):
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
