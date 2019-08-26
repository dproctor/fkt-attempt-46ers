#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Common route methods.
"""

from __future__ import print_function
import os
import sys
import argparse
import requests
import csv
import re
from collections import defaultdict

from dijkstar import Graph, find_path
from io import StringIO

GAIA_REQUEST_PATTERN = 'https://routing.gaiagps.com/route?json=%7B%22locations%22%3A%5B%7B%22lon%22%3A{start_lon}%2C%22lat%22%3A{start_lat}%2C%22type%22%3A%22break%22%7D%2C%7B%22lon%22%3A{end_lon}%2C%22lat%22%3A{end_lat}%2C%22type%22%3A%22break%22%7D%5D%2C%22costing%22%3A%22pedestrian%22%7D&max_hiking_difficulty=6'

_TRAILHEAD_NAME = "Trailhead"


def merge_pairwise_and_matrix_distances(pairs, matrix):
    merged = defaultdict(dict)
    for p1 in matrix:
        for p2 in matrix[p1]:
            if p1 == p2 or not is_peak(p1) or not is_peak(p2):
                merged[p1][p2] = matrix[p1][p2]
            else:
                merged[p1][p2] = (min(pairs[p1][p2][0], matrix[p1][p2][0]),
                                  matrix[p1][p2][1], matrix[p1][p2][2])
    return merged


def parse_distance_matrix_from_pairs(pair_reader):
    distance_matrix = defaultdict(dict)
    for row in pair_reader:
        # Convert from miles to kilometers
        distance = float(row[2]) * 0.621371
        distance_matrix[row[0]][row[1]] = (distance, 0, 0)
    return distance_matrix


def parse_distance_matrix(csv_reader, cost_function):
    # Ignore last column for trailhead.
    peaks = csv_reader.__next__()[1:-1]
    distances = {p: {p: None for p in peaks} for p in peaks}
    trailhead_distances = {p: None for p in peaks + [_TRAILHEAD_NAME]}
    for row in csv_reader:
        if not is_peak(row[0]):
            continue
        # Note: trailhead distances are read as Peak > Trailhead, but here
        # stored as Trailhead > Peak, so they need to be reversed below.
        trailhead_distances[row[0]] = _parse_distance_gain_loss_string(row[-1])
        i = 0
        for d in row[1:-1]:
            distances[row[0]][peaks[i]] = _parse_distance_gain_loss_string(d)
            i += 1

    # Add back distances
    for p1 in distances:
        for p2 in distances[p1]:
            if distances[p1][p2] is not None and distances[p2][p1] is None:
                distances[p2][p1] = (
                    distances[p1][p2][0],
                    distances[p1][p2][2],  # swap climb/desc
                    distances[p1][p2][1])
    # Build graph for shortest path computation
    g = Graph()
    for p1 in distances:
        for p2 in distances[p1]:
            g.add_edge(p1, p2, distances[p1][p2])

    def internal_cost_function(_0, _1, x, _2):
        return cost_function(x)

    for p1 in distances:
        for p2 in distances[p1]:
            distances[p1][p2] = tuple(
                sum(x) for x in zip(*find_path(
                    g, p1, p2, cost_func=internal_cost_function).edges))

    # Trailhead has to be added after shortest path computation to make sure
    # shortest parths don't go through the artificial trailhead.
    distances[_TRAILHEAD_NAME] = {}
    for p in trailhead_distances:
        d = trailhead_distances[p]
        if d is None:
            d = (1e9, 1e9, 1e9)
        distances[_TRAILHEAD_NAME][p] = (d[0], d[2], d[1])
        distances[p].update({_TRAILHEAD_NAME: (d[0], d[1], d[2])})

    # Add self distance
    for p1 in distances:
        distances[p1][p1] = (0, 0, 0)
    return distances


def peaks_connected_to(peak, sparse):
    peaks = []
    for (k0, v0) in sparse.items():
        for (k1, v1) in v0.items():
            if k1 == peak and v1 is not None:
                peaks.append(k0)
    return peaks


def is_peak(string):
    return string != _TRAILHEAD_NAME


def line_to_peak_lat_long(i):
    pat = re.compile('(?P<peak>[^,]*),.*, (?P<lat>[^,]*), (?P<long>[^,]*)\\n')
    a = pat.search(i)
    return (a.group('peak'), {'lat': a.group('lat'), 'long': a.group('long')})


def mileage_only_cost(x):
    if x is None: return int(1e9)
    return int(100 * x[0])


def climbing_only_cost(x):
    if x is None: return int(1e9)
    return int(x[1])


def mixed_cost(x):
    return mileage_only_cost(x) + climbing_only_cost(x)


def _parse_distance_gain_loss_string(s):
    if s == '':
        return None
    pat = re.compile(
        'Distance: (?P<distance>[^ ]*) mi\\n\+(?P<gain>[^ ]*) ft / -(?P<loss>[^ ]*) ft'
    )
    res = pat.search(s)
    assert res is not None, 'String ({}) does not match expected distance pattern'.format(
        s)
    return (_stof(res.group('distance')), _stof(res.group('gain')),
            _stof(res.group('loss')))


def _stof(s):
    return float(s.replace(',', ''))


DEFAULT_COST = mixed_cost

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
