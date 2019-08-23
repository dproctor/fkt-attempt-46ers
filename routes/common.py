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

from dijkstar import Graph, find_path
from io import StringIO

_TRAILHEAD_NAME = "Trailhead"


def parse_distance_matrix(csv_reader, cost_function):
    peaks = csv_reader.__next__()[1:]
    distances = {p: {p: None for p in peaks} for p in peaks}
    for row in csv_reader:
        i = 0
        for d in row[1:]:
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


def climbing_only_cost(x):
    if x is None: return int(1e9)
    return int(x[1])


def mileage_only_cost(x):
    if x is None: return int(1e9)
    return int(100 * x[0])


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


DEFAULT_COST = mileage_only_cost

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))