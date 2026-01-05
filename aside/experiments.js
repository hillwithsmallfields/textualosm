#!/usr/bin/node

const OverpassFrontend = require('overpass-frontend')

my_bbox = {minlat: 48.14, maxlat: 48.15, minlon: 17.11, maxlon: 17.12 };

as_on_overpass_turbo = `[out:json][timeout:25];
area[name="Bratislava"];
way(area)[name="Štúrova"]->.my_street;
(
        nw[amenity](around.my_street:25);
        nwr[building](around.my_street:25);
        wr[highway](around.my_street:25);
);
(._;>;);
out;`;

just_the_street = `way[name="Štúrova"];` // works OK
street_and_follower = `way[name="Štúrova"];around;`

without_area =`[name="Štúrova"]->.my_street;
(
        nw[amenity](around.my_street:25);
        nwr[building](around.my_street:25);
        wr[highway](around.my_street:25);
);
(._;>;);
out;`

without_variable =`[nwr](
        nw[amenity](around.[name="Štúrova"]:25);
        nwr[building](around.[name="Štúrova"]:25);
        wr[highway](around.[name="Štúrova"]:25);
);
(._;>;);
out;`

adjoining_highways = `way[highway](around.[name="Štúrova"]:25);`

from_simple_examples_0 = `rel[ref="E61"];
node(r);

out body;`;

// you may specify an OSM file as url, e.g. 'test/data.osm.bz2'
const overpassFrontend = new OverpassFrontend('//overpass-api.de/api/interpreter')

// request restaurants in the specified bounding box
overpassFrontend.BBoxQuery(
    // just_the_street,
    street_and_follower,
    // without_area,
    // without_variable,
    // adjoining_highways,
    // from_simple_examples_0,
    // as_on_overpass_turbo,
  my_bbox,
  {
    properties: OverpassFrontend.ALL
  },
  function (err, result) {
    console.log('* ' + result.tags.name + ' (' + result.id + ')')
  },
  function (err) {
    if (err) { console.log(err) }
  }
)
