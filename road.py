#!/usr/bin/python
import web

# For the web part, see http://webpy.org/docs/0.3/tutorial

# For the OSM part, see
# http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guides and
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
    '/\(d+)', 'way'
)

sample_query = "[out:json];way(37143281);(around(10);<;);out qt;"

class way:
    def GET(self, way):
        contents = "sample " + way + " data"
        return render.way(contents)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
