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
    <name>46er FKT attempt proposed peak sequence</name>
    <trkseg>"""

GPX_FOOTER = """    </trkseg>
  </trk>
</gpx>"""

TRKPT_PATTERN = """      <trkpt lat="%s" lon="%s">
        <time>2019-08-01T00:%02d:00:000Z</time>
      </trkpt>"""


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c',
                        '--coordinates',
                        help="Coordinates csv, with summit name, lat, long",
                        type=argparse.FileType('r'))
    parser.add_argument('-ps',
                        '--peak_sequence',
                        help="Peak sequence file, one summit per line",
                        type=argparse.FileType('r'))

    args = parser.parse_args(arguments)
    pat = re.compile('(?P<peak>[^,]*),.*, (?P<lat>[^,]*), (?P<long>[^,]*)\\n')

    def line_to_peak_lat_long(i):
        a = pat.search(i)
        return (a.group('peak'), {
            'lat': a.group('lat'),
            'long': a.group('long')
        })

    peaks_to_lat_long = dict(
        line_to_peak_lat_long(i) for i in args.coordinates.readlines()[1:])

    print(GPX_HEADER)
    i = 0
    for p in args.peak_sequence.readlines():
        peak = p.strip()
        print(TRKPT_PATTERN % (peaks_to_lat_long[peak]['lat'],
                               peaks_to_lat_long[peak]['long'], i))
        i += 1
    print(GPX_FOOTER)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
