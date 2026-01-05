// Script to accompany maplookup.html
// with bits from
// https://www.taniarascia.com/how-to-connect-to-an-api-with-javascript/
// and
// https://stackabuse.com/using-fetch-to-send-http-requests-in-javascript/

function fetch_map() {
    var querystring = document.getElementById("mapfetcher").elements["mapquery"].value;
    var request = new XMLHttpRequest()

    request.open('GET',
                 'https://nominatim.openstreetmap.org/search?addressdetails=1&format=json&q=' + querystring,
                 true)

    request.onload = function () {
        const app = document.getElementById('results')
        if (request.status >= 200 && request.status < 400) {
            app.textContent = '' // empty out any previous results
            const results_table = document.createElement('table')
            results_table.setAttribute('class', 'mapEntriesTable')
            app.appendChild(results_table)
            var entries = JSON.parse(request.response);
            entries.forEach((entry) => {
                const entry_row = document.createElement('tr')
                results_table.appendChild(entry_row)

                const country_cell = document.createElement('td')
                country_cell.setAttribute('class', 'country')
                country_cell.textContent = entry.address.country
                entry_row.appendChild(country_cell)
                
                const entry_address_cell = document.createElement('td')
                entry_address_cell.setAttribute('class', 'entry_address')
                entry_address_cell.textContent = entry.display_name
                entry_row.appendChild(entry_address_cell)

                const entry_class_cell = document.createElement('td')
                entry_class_cell.setAttribute('class', 'entry_class')
                entry_class_cell.textContent = entry.class
                entry_row.appendChild(entry_class_cell)
            })
        } else {
            console.log("Error");
        }
    }

    // Send request
    request.send()
    return true;
}
