#!/usr/bin/python3

import argparse

import contextily as ctx

import geometry
import road_bits

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
    parser.add_argument("--within", "-w", type=int, default=25)
    parser.add_argument("--verbose", "-v", action='store_true')
    args = parser.parse_args()

    road_bits.road_bits_setup()

    way_id = road_bits.way_id_from_name(
        args.start,
        road_bits.area(
            args.city, args.county, args.country))

    points = road_bits.way_points(way_id)

    print("points:")
    for point in points:
        print("  ", point)

    this = points[0]
    for that in points[1:]:
        bearing = geometry.bearing(this, that)
        distance = geometry.distance(this, that)
        print("segment", this, that, "distance", round(distance), "bearing", round(bearing), "https://www.openstreetmap.org/#map=19/%g/%g" % (this[1], this[0]))
        this = that

    abutters = road_bits.street_abutters(
        way_id,
        args.start,
        within=args.within)

    print("results:")
    for k in sorted(abutters.keys()):
        print("---")
        for a in abutters[k]:
            ftype = road_bits.feature_type(a)
            print("  ", a.tag('name') or "<unnamed>", a.tag(ftype), ftype, a.geometry().get('coordinates')[0])
            feature_street = a.tag('addr:street')
            if feature_street and feature_street != args.start:
                print("*** Belongs on a different street ***")
            for k, v in a.tags().items():
                if k != 'note':
                    print("    ", k, v)

if __name__ == '__main__':
    main()
