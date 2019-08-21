#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Computes the distance and elevation gain/loss of a particular peak sequence.

This assumes that the provided distance matrix has distances for all of the
implied transitions, and does not do any path finding.

Dev command:  ls routes/ps2d.py | entr -c -s 'python3 routes/ps2d.py -ps routes/2019-fkt-peak-sequence.txt -d https://docs.google.com/spreadsheets/u/0/d/19ft1S-RoGl5jbBcyiCKPZuqL4a4MvFkjW_hu6I87Fhc/export?format=csv&id=19ft1S-RoGl5jbBcyiCKPZuqL4a4MvFkjW_hu6I87Fhc&gid=0'

Google sheet with distance matrix is at:
https://docs.google.com/spreadsheets/d/19ft1S-RoGl5jbBcyiCKPZuqL4a4MvFkjW_hu6I87Fhc/edit?usp=sharing
"""

from __future__ import print_function
import os
import sys
import argparse
import requests
import csv
import re
import common

from io import StringIO


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-ps',
                        '--peak_sequence',
                        help='Filename of peak sequence to evaluate',
                        type=argparse.FileType('r'))
    parser.add_argument('-d',
                        '--distance_matrix',
                        help='Url of distance matrix',
                        type=str)

    args = parser.parse_args(arguments)

    response = requests.get(args.distance_matrix)
    assert response.status_code == 200, 'Download failed'

    reader = csv.reader(StringIO(response.content.decode("utf-8")))
    distances = common.parse_distance_matrix(reader)
    totals = [0., 0., 0.]
    curr = None
    for p in args.peak_sequence.readlines():
        pe = p.strip()
        if curr is not None:
            if distances[curr][pe] is None:
                raise Exception('Missing distance {} > {}'.format(curr, pe))
            totals[0] += distances[curr][pe][0]
            totals[1] += distances[curr][pe][1]
            totals[2] += distances[curr][pe][2]
        curr = pe
    print('Distance: {:.1f} miles\n+{:.0f} ft / -{:.0f} ft'.format(*totals))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
