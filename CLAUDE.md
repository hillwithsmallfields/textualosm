# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

TextualOSM generates accessible text representations of OpenStreetMap data — specifically "stripmaps" showing one street per page with abutting buildings and amenities listed on either side of a central street column. Designed for speech synthesizers and braille displays.

The stripmap format: a central column of `|` characters (street), `+` at junctions, other symbols for crossings, with buildings/amenities listed left and right.

## Running

Activate the virtual environment first:
```bash
source textualosm.env/bin/activate
```

Analyze a street:
```bash
python3 src/textualosm/around_road.py \
  --within 5 \
  --country Belgium \
  --county "Brussels-Capital" \
  --city Etterbeek \
  --start "Rue du Cornet - Hoornstraat" \
  --verbose
```

The run scripts (`runrdc`, `runrgl`, `runrup`) are convenience wrappers that source the venv and invoke `around_road.py` with preset arguments.

## Dependencies

```
OSMPythonTools   # Overpass API + Nominatim wrappers
contextily       # Tile-based basemaps (for visualization)
```

Install: `pip install -r requirements.txt`

## Architecture

Data flows through these layers:

1. **`road_bits.py`** — core OSM data fetching. Uses Overpass API (60s timeout, 2s delays between requests) and Nominatim. Module-level caches avoid repeated API calls. Key functions:
   - `area()` — city/county/country → OSM area ID
   - `way_id_from_name()` — street name → OSM way ID
   - `way_points()` — way coordinates
   - `way_joiners()` — intersecting streets at a location
   - `way_abutters()` — nearby buildings and amenities within radius
   - `street_abutters()` — recursively collects all segments of a multi-segment street
   - `collect()` — top-level: returns nodes, segments, and streets dict
   - `feature_type()` — classifies OSM tags (building, amenity, shop, etc.)

2. **`geometry.py`** — haversine `distance()` (meters) and compass `bearing()` between lat/lon pairs. Has a self-test with hardcoded UK coordinates when run directly.

3. **`around_road.py`** — CLI frontend. Calls `road_bits.collect()`, logs results at DEBUG level.

4. **`road.py`** — legacy web.py HTTP interface (`/{way_id}` → JSON). Stub/incomplete.

5. **`road_mesh.py`** — road mesh/grid operations. Stub/incomplete.

## Key Architectural Challenges

The `description` file documents the core difficulty: assigning buildings to the correct side of curved or bent roads. When a road bends sharply (hairpin), determining which building on the outside is "opposite" a building on the inside is geometrically non-trivial. The bearing calculations in `geometry.py` exist to address this.

## Reference Output

`samples/bratislava.txt` contains a complete example of the target stripmap format — consult it when working on text rendering.

## No Automated Tests

There is no test suite. Manual testing uses the `q*`/`r*` files (Overpass query/response pairs from Porlock) and the run scripts.
