#!/usr/bin/node

const OverpassFrontend = require('overpass-frontend')

// you may specify an OSM file as url, e.g. 'test/data.osm.bz2'
const overpassFrontend = new OverpassFrontend('//overpass-api.de/api/interpreter')



const short_query = 'way[name="Štúrova"];node(around:40)[amenity~"."]' // this one works

    // 'way[name="Štúrova"]->.street;(node(around.street:30)[amenity~"."];way(around.street:30)[building~"."])',
    // 'way[name="Štúrova"]->.street;(node(around.street:30)[amenity~"."];)',
    // 'way[name="Štúrova"]->.street;node(around.street:30)[amenity~"."]',

const short_bbox = { minlat: 48.14, maxlat: 48.15, minlon: 17.11, maxlon: 17.12 }

const long_query = `
    area[name="Tirana"]; 
    way[name="Rruga Urani Pano"]->.street;
    (
        way(around.street:30)[building~"."];
        node(around.street:30)[amenity~"."];
        node(around.street:30)[tourism~"."];
        node(around.street:30)[shop~"."];
        node(around.street:30)[office~"."];
        way(around.street:0)[highway~"."];
    );`

const long_bbox = { minlat: 41.30, maxlat: 41.32, minlon: 18.80, maxlon: 19.83 }

// Other streets to try:
// St John Street, London: https://www.openstreetmap.org/way/38752553
// High Street, Porlock: https://www.openstreetmap.org/way/149883088
// Αλεπού - Πέλεκας, Pelekas, Corfu: https://www.openstreetmap.org/way/618264889

const props = { properties: OverpassFrontend.ALL }


function handle_result(err, result) {
    if (result) {
        console.log('* ' + result.tags.name + ' ' + result.tags.amenity + ' (' + result.id + ')')
    } else {
        console.log("null result")
    }
}

function handle_error (err) {
    if (err) { console.log(err) }
}

function long_fn() {
    overpassFrontend.BBoxQuery(long_query, long_bbox,
                               props,
                               handle_result, handle_error)
}

function short_fn() {
    overpassFrontend.BBoxQuery(short_query, short_bbox,
                               props,
                               handle_result, handle_error)
}

// short_fn()
long_fn()
