#!/usr/bin/env python3

import argparse
import logging

import contextily as ctx

import geometry
import road_bits

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def draw():
    fig_height = 600
    ratio = 1.2
    fig_width = fig_height * ratio
    fig, ax_plt = plt.subplots(figsize=(fig_width, fig_height))
    ctx.add_basemap(
        self.ax_plt,
        source=BASEMAP_PROVIDER,
        zoom=self.style['basemap_zoom'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Tirana")
    parser.add_argument("--county", default="Tirana")
    parser.add_argument("--country", default="Albania")
    parser.add_argument("--start", "-s", default="Rruga Urani Pano")
    parser.add_argument("--within", "-w", type=int, default=5)
    parser.add_argument("--verbose", "-v", action='store_true')
    args = parser.parse_args()

    road_bits.road_bits_setup()

    area_id = road_bits.area(args.city, args.county, args.country)
    street_ways, joiners, abutters = road_bits.fetch_street_data(
        args.start, area_id, within=args.within)

    log.debug("street ways: %d segments", len(street_ways))
    for way in street_ways:
        points = [node.geometry()['coordinates'] for node in way.nodes()]
        this = points[0]
        for that in points[1:]:
            log.debug("segment %s %s; distance %d; bearing %d; https://www.openstreetmap.org/way/%s#map=19/%g/%g",
                      this, that,
                      round(geometry.distance(this, that)),
                      round(geometry.bearing(this, that)),
                      way.id(), this[1], this[0])
            this = that

    log.debug("abutters: %d total", len(abutters))
    for a in abutters:
        ftype = road_bits.feature_type(a)
        log.debug("  name=%s %s=%s coords=%s",
                  a.tag('name') or "<unnamed>", ftype, a.tag(ftype),
                  a.geometry().get('coordinates')[0])
        feature_street = a.tag('addr:street')
        if feature_street and feature_street != args.start:
            log.debug("*** Belongs on a different street ***")
        for k, v in a.tags().items():
            if k != 'note':
                log.debug("    tag %s=%s", k, v)

if __name__ == '__main__':
    main()
