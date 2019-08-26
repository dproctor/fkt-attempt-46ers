#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Converts peak sequence (ps) to gpx (viewable in Google Earth.

Doesn't attempt to create actual hiking path between points, but simply assumes
straight lines between points.

Dev command:
    ls routes/ps2gpx.py | entr -c python3 routes/ps2gpx.py -ps routes/2019-fkt-peak-sequence.txt -c summits/coordinates.csv
"""

from __future__ import print_function
import os
import sys
import argparse
import re
import requests
import polyline
import datetime

import common

GPX_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Garmin Connect" version="1.1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/11.xsd"
  xmlns:ns3="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
  <metadata>
    <name>46er FKT attempt proposed peak sequence</name>
    <link href="connect.garmin.com">
      <text>Garmin Connect</text>
    </link>
    <time>2019-08-18T20:28:51.000Z</time>
  </metadata>
  <trk>
    <name>46er FKT attempt proposed route</name>
    <trkseg>"""

GPX_FOOTER = """    </trkseg>
  </trk>
</gpx>"""

TRKPT_PATTERN = """      <trkpt lat="%s" lon="%s">
        <time>%s</time>
      </trkpt>"""


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c',
                        '--coordinates',
                        help="Coordinates csv, with summit name, lat, long",
                        type=argparse.FileType('r'))
    parser.add_argument(
        '-s',
        '--simplify',
        help="Print simplified (only summit coordinates) or full route",
        type=bool)
    parser.add_argument('-ps',
                        '--peak_sequence',
                        help="Peak sequence file, one summit per line",
                        type=argparse.FileType('r'))

    args = parser.parse_args(arguments)

    peaks_to_lat_long = dict(
        common.line_to_peak_lat_long(i)
        for i in args.coordinates.readlines()[1:])

    print(GPX_HEADER)
    start_time = datetime.datetime(2018, 8, 1)
    i = 0
    last = None
    for p in args.peak_sequence.readlines():
        peak = p.strip()
        if not common.is_peak(peak):
            continue
        if args.simplify:
            print(TRKPT_PATTERN %
                  (peaks_to_lat_long[peak]['lat'],
                   peaks_to_lat_long[peak]['long'],
                   (start_time + datetime.timedelta(0, i * 3600)).isoformat()))
        else:
            if last is None:
                last = peak
                continue
            res = requests.post(
                common.GAIA_REQUEST_PATTERN.format(
                    start_lon=peaks_to_lat_long[last]['long'],
                    start_lat=peaks_to_lat_long[last]['lat'],
                    end_lon=peaks_to_lat_long[peak]['long'],
                    end_lat=peaks_to_lat_long[peak]['lat']))
            for point in polyline.decode(
                    res.json()['trip']['legs'][0]['shape']):
                print(TRKPT_PATTERN %
                      (point[0] / 10, point[1] / 10,
                       (start_time +
                        datetime.timedelta(0, i * 3600)).isoformat()))
        i += 1
        last = peak
    print(GPX_FOOTER)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
