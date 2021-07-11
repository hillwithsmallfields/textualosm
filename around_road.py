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

    abutters = road_bits.street_abutters(
        way_id,
        args.start,
        within=args.within)

    print("results:")
    for k in sorted(abutters.keys()):
        print("---")
        for a in abutters[k]:
            print("  ", a.tag('name') or "<unnamed>", road_bits.feature_type(a), a.geometry().get('coordinates'))
            for k, v in a.tags().items():
                if k != 'note':
                    print("    ", k, v)

if __name__ == '__main__':
    main()
