#!/usr/bin/python3

import argparse

import road_bits

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

    start_long, start_lat = points[0]
    for next_long, next_lat in points[1:]:
        # TODO: bearings and distances for segments, then use the distances to construct a sequence
        print("segment", (start_long, start_lat), (next_long, next_lat))
        start_long = next_long
        start_lat = next_lat

    abutters = road_bits.street_abutters(
        way_id,
        args.start,
        within=args.within)

    print("results:")
    for k in sorted(abutters.keys()):
        print("---")
        for a in abutters[k]:
            ftype = road_bits.feature_type(a)
            print("  ", a.tag('name') or "<unnamed>", a.tag(ftype), ftype, a.geometry().get('coordinates'))
            feature_street = a.tag('addr:street')
            if feature_street and feature_street != args.start:
                print("*** Belongs on a different street ***")
            for k, v in a.tags().items():
                if k != 'note':
                    print("    ", k, v)

if __name__ == '__main__':
    main()
