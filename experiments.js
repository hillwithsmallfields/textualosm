#!/usr/bin/node

// see https://www.npmjs.com/package/overpass-frontend and
// https://rawgit.com/plepe/overpass-frontend/master/doc/OverpassFrontend.html

const OverpassFrontend = require('overpass-frontend')

import {OverpassFrontend} from '/modules/'

// you may specify an OSM file as url, e.g. 'test/data.osm.bz2'
const overpassFrontend = new OverpassFrontend('//overpass-api.de/api/interpreter')

function fetch_map() {
    var querystring = document.getElementById("mapfetcher").elements["mapquery"].value;
    console.log("starting fetch_map")
    const app = document.getElementById('results')
    app.textContent = '' // empty out any previous results
    const results_table = document.createElement('table')
    results_table.setAttribute('class', 'mapEntriesTable')
    app.appendChild(results_table)

    const entry_row = document.createElement('tr')
    results_table.appendChild(entry_row)
    const demo_cell = document.createElement('td')
    demo_cell.setAttribute('class', 'demo')
    demo_cell.textContent = "Demo text"
    entry_row.appendChild(demo_cell)

    overpassFrontend.BBoxQuery(
        querystring,
        // near Wien Westbahnhof
        { minlat: 48.19, maxlat: 48.20, minlon: 16.33, maxlon: 16.34 },
        {
            properties: OverpassFrontend.ALL
        },
        function (err, result) {
            const entry_row = document.createElement('tr')
            results_table.appendChild(entry_row)
            const name_cell = document.createElement('td')
            name_cell.setAttribute('class', 'country')
            name_cell.textContent = result.tags.name
            entry_row.appendChild(name_cell)
            const id_cell = document.createElement('td')
            id_cell.setAttribute('class', 'country')
            id_cell.textContent = result.id
            entry_row.appendChild(id_cell)
        },
        function (err) {
            if (err) { console.log(err) }
        }
    )
}
