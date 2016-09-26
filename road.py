#!/usr/bin/python
# coding=utf-8
import web
import urllib

# For the web part, see http://webpy.org/docs/0.3/tutorial

# For the OSM part, see
# http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide and
# https://github.com/mapbox/mapping/wiki/Overpass-Guide and
# http://osmlab.github.io/learnoverpass//en/

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

render = web.template.render('templates/')
urls = (
    '/(\d+)', 'way'
)

overpass = "http://overpass-api.de/api/interpreter?data="

class way:
    def GET(self, way):
        query_preamble = """[out:json];"""
        query = "way(37143281);" # In the complete program, this will be able to take a way ID, or a (street) name and something to disambiguate it (city etc)
        fetcher_params = { "building" : "building", # may have to be building|shop|amenity
                           "wayrange": 10,
                           "noderange": 20}
        get_nodes = """node [~".+"~".+"](around:%(noderange)d);""" % fetcher_params
        # for the following two, I might omit the final ">;" and use the "out center", but then I wouldn't be able to tell whether the tagged nodes retrieved above are inside the buildings
        get_areas = """way [~"%(building)s"~".+"](around:%(wayrange)d);>;""" % fetcher_params
        get_relations = """rel [~"%(building)s"~".+"](around:%(wayrange)d);>;""" % fetcher_params # todo: fetch just the outer of the relation (and fetch only multipolygon relations)
        query_postamble = "(" + get_nodes + get_areas + get_relations + "); out body qt center;"
        query = overpass + query_preamble + query + query_postamble
        handle = urllib.urlopen(query)
        mapdata = handle.read()
        # todo: convert the data into a Python data structure (with a JSON reader)
        # todo: convert into features along the way, combining building areas with POIs tagged inside those areas
        # todo: sort the features along the way, probably by working out which way segment the feature is nearest to, and where along that segment the normal from the way to the feature centre falls
        # todo: filter out features which are behind others (we can't guarantee to get only the front rank of things facing the street)
        # todo: work out which features are facing more than one feature on the other side of the street
        # todo: output
        return render.way("Query was:\n" + query + "\nand reply was:\n" + mapdata)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
