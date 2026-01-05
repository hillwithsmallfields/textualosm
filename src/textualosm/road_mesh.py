#!/usr/bin/python3

import argparse

import road_bits

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Tirana")
    parser.add_argument("--county", default="Tirana")
    parser.add_argument("--country", default="Albania")
    parser.add_argument("--start", "-s", default="Rruga Urani Pano")
    parser.add_argument("--depth", "-d", type=int, default=3)
    parser.add_argument("--verbose", "-v", action='store_true')
    args = parser.parse_args()

    road_bits.road_bits_setup()

    nodes, segments, streets = road_bits.collect(
        road_bits.way_id_from_name(args.start,
                                   road_bits.area(
                                       args.city, args.county, args.country)),
        args.start, args.depth)

    print("nodes")
    for node in sorted(nodes.keys()):
        print("  ", node, nodes[node])
    print("segments")
    for segment in sorted(segments.keys()):
        print("  ", segment, segments[segment])
    print("streets")
    for street in sorted(streets.keys()):
        print("  ", street, streets[street])

if __name__ == '__main__':
    main()
