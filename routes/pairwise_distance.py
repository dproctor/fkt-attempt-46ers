#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Calls Gaiagps.com API to get hiking directions for all pairs of coordinates.
"""

from __future__ import print_function
import os
import sys
import argparse
import requests

import common

GAIA_REQUEST_PATTERN = 'https://routing.gaiagps.com/route?json=%7B%22locations%22%3A%5B%7B%22lon%22%3A{start_lon}%2C%22lat%22%3A{start_lat}%2C%22type%22%3A%22break%22%7D%2C%7B%22lon%22%3A{end_lon}%2C%22lat%22%3A{end_lat}%2C%22type%22%3A%22break%22%7D%5D%2C%22costing%22%3A%22pedestrian%22%7D&max_hiking_difficulty=6'


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c',
                        '--coordinates',
                        help="Coordinates csv, with summit name, lat, long",
                        type=argparse.FileType('r'))

    args = parser.parse_args(arguments)

    peaks_to_lat_long = dict(
        common.line_to_peak_lat_long(i)
        for i in args.coordinates.readlines()[1:])

    for p in peaks_to_lat_long:
        for q in peaks_to_lat_long:
            if p == q:
                continue
            res = requests.post(
                GAIA_REQUEST_PATTERN.format(
                    start_lon=peaks_to_lat_long[p]['long'],
                    start_lat=peaks_to_lat_long[p]['lat'],
                    end_lon=peaks_to_lat_long[q]['long'],
                    end_lat=peaks_to_lat_long[q]['lat']))
            print("{}({}, {}) > {}({}, {}): {}km".format(
                p, peaks_to_lat_long[p]['long'], peaks_to_lat_long[p]['lat'],
                q, peaks_to_lat_long[q]['long'], peaks_to_lat_long[q]['lat'],
                res.json()['trip']['summary']['length']))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
