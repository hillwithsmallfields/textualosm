#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import web
import overpass
import geojson
import sys
import pprint
import json

# For the web part, see http://webpy.org/docs/0.3/tutorial

# For the OSM part, see
# http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide and
# https://github.com/mapbox/mapping/wiki/Overpass-Guide and and
# https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL and
# http://osmlab.github.io/learnoverpass//en/ and for the API wrapper:
# https://github.com/mvexel/overpass-api-python-wrapper

# Started as part of: https://hackpad.com/SOTMOSgeo-Hackday-live-reporting-H4q1GRbgRCz

# Using http://www.openstreetmap.org/way/37143281 as a hard-coded sample to start with

# The hand-written stripmap for this street looked like the following
# block, and the idea is to generate this automatically by fetching
# everything near the way, using overpass.

# Hand-generated sample for http://www.openstreetmap.org/way/37143281

# * Medená *

# # Starting from north-east end, each line reads your right-hand side then your left as you walk down the file.

#                                 --- Štúrova ---+--- Štúrova ---
#                           pharmacy DM Drogerie % Shoe shop Gabor
#                                       building | Shoe shop Passo di Trend
#                                       building | kindergarten Materská škola
#                                    35 building | bank ČSOB
#                                    33 Caffe 33 | building 20
#                                    31 building | 18 restaurant Spaghetti Leviathan
#                              29 Musica Slovaca | 16 Nightclub Nu Spirit Bar
#                                110/27 building | 16 Nightclub Nu Spirit Bar
#                                    25 building | 14 Dowina musical instruments
#                                    23 building | 12 building
#                                 21 Music av 21 +--- Tobrucká ---
#                                       alleyway % road triangle containing postbox
# 19 Convenience shop Celiakis - bezlepkový svet | 10 (past road triangle)
#                        19 music shop Dr. Horák | road triangle
#                                  31/7 building | road triangle
#                                 --- Kúpeľná ---+--- Kúpeľná ---
#                bookshop Kníhkupectvo U Bandiho % building
#                        Café La Vecchia Bottega | building
#                                    15 building | Shop Moja Samoška
#                                    13 building | Shop Moja Samoška
#                                    11 building | 4 Okrsková stanica mestskej polície hlavného mesta SR Bratislavy
#                                   Hotel Avance | Okrsková stanica mestskej polície hlavného mesta SR Bratislavy
#                                     5 building | Ministerstvo životného prostredia Slovenskej republiky
#                                         Reduta | Námestie Ľudovíta Štúra
#                                 --- Mostová ---+--- Mostová ---

# To test, run this program from the command line with the port number you want to use, then in your browser visit localhost:<port>/<wayID>

# render = web.template.render('templates/')
urls = (
    '/(\d+)', 'way'
)

overpass_api = overpass.API()

class edge:

    """

    Edges represent the sections between the successive nodes from the OSM server.

    They hold the incoming way data in a form helpful for converting
    to output segments, which typically represent smaller sections of
    the way.

    """

    def __init__(self):
        self.travel = 0.0
        self.distance = 0.0
        self.direction = 0.0
        self.start_latitude = 0.0
        self.start_longitude = 0.0
        self.osm_type = None    # usually highway
        self.osm_subtype = None # residential, tertiary, etc
        self.segments = []      # references to the output data being constructed

class segment:

    """This describes one segment of the road.

    A segment may hold a feature fronting the road on one side, or one
    on each side, or describe a part of the road (for junctions,
    pedestrian crossings, etc), or possibly both.
    """

    def __init__(self):
        self.left_fronter = None
        self.left_setback = 0.0
        self.right_fronter = None
        self.right_setback = 0.0
        self.travel = 0.0       # how much travel this segment covers
        self.distance = 0.0     # cumulatively from the start of the road
        self.direction = 0.0    # the compass direction
        self.road_feature = None
        self.edge = None        # reference to the incoming data

class street:

    def __init__(self):
        self.edges = []
        self.segments = []

    def add_fronter(self, fronter, along, setback):
        # todo: use the edges to put a segment in place that this fronter can go on
        pass

class way:

    def __init__(self):
        pass

    def GET(self, way_id_or_name):
        pp = pprint.PrettyPrinter(indent=2)
        # In the complete program, this will be able to take a way ID,
        # or a (street) name and something to disambiguate it (city
        # etc); it should also be able to take a set of ways
        # representing a street, and perhaps a list of way sections
        # representing a result from a routing engine

        query = "37143281"

        # todo: try to get the geometry of the way, without having to fetch the nodes; likewise, try to get the building co-ordinates
        way_query = "(way(" + query + """)->.w;
        .w >;
        way[building](around.w: 10)->.b;
        .b >;
        );"""
        print("Way query is", way_query)
        way_data = overpass_api.get(way_query, responseformat='json')
        print("pretty-printed:")
        pp.pprint(json.loads(geojson.dumps(way_data)))

        # or, get the way, then use "around:5" for within 5 metres
        # way[building](around.THEOTHERQUERY: 30);

        # way[highway=primary] -> .blindway;
        # way[building](around.blindway: 30);

        # cross track distance, long track distance

        # (from Tobias Zwick)

        # https://movable-type.co.uk/scripts/latlong.html

        # todo: convert into features along the way, combining building areas with POIs tagged inside those areas
        # todo: sort the features along the way, probably by working out which way segment the feature is nearest to, and where along that segment the normal from the way to the feature centre falls
        # todo: filter out features which are behind others (we can't guarantee to get only the front rank of things facing the street)
        # todo: work out which features are facing more than one feature on the other side of the street
        # todo: output
        debug_text = ""
        # debug_text += "way data: " + str(way) + "\n"
        # debug_text += "feature data:\n" + '\n'.join([str(f) for f in mapdata['features']])
        # debug_text += "way data:\n" + str(way_response) + "\n"
        # return render.way("Query was:\n" + query + "\nAnd full query was:\n" + feature_query + "\nand reply was:\n" + debug_text)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
