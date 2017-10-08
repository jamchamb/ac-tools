#!/usr/bin/env python
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('simple_map', type=str)
    parser.add_argument('offset', type=str)
    args = parser.parse_args()

    infile = open(args.simple_map, 'r')

    lines = infile.read().split('\n')

    infile.close()

    for line in lines:
        if len(line) == 0:
            continue

        address = int(line[:8], 16)
        func_name = line[9:]

        print '%08x %s' % (address + int(args.offset, 16), func_name)


if __name__ == '__main__':
    main()
