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

    abutters = road_bits.street_abutters(
        road_bits.way_id_from_name(args.start,
                                   road_bits.area(
                                       args.city, args.county, args.country)),
        args.start,
        within=args.within)

    for abutter in sorted(abutters.keys()):
        print("  ", abutter, abutters[abutter])

if __name__ == '__main__':
    main()
