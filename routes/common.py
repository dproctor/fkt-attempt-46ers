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

from io import StringIO


# TODO(dproctor): Need to make distances "symmetric" (though reversing
# gain/loss)
def parse_distance_matrix(csv_reader):
    peaks = csv_reader.__next__()[1:]
    distances = {p: {p: None for p in peaks} for p in peaks}
    for row in csv_reader:
        i = 0
        for d in row[1:]:
            distances[row[0]][peaks[i]] = _parse_distance_gain_loss_string(d)
            i += 1
    for p1 in distances:
        for p2 in distances[p1]:
            if distances[p1][p2] is not None and distances[p2][p1] is None:
                distances[p2][p1] = (distances[p1][p2][0],
                                     distances[p1][p2][1],
                                     distances[p1][p2][2])
    return distances


def sparse_to_dense(dm, cost_function):
    return [[cost_function(dm[p1][p2]) for p2 in dm[p1]] for p1 in dm]


def _parse_distance_gain_loss_string(s):
    if s == '':
        return None
    pat = re.compile(
        'Distance: (?P<distance>[^ ]*) mi\\n\+(?P<gain>[^ ]*) ft / -(?P<loss>[^ ]*) ft'
    )
    res = pat.search(s)
    return (_stof(res.group('distance')), _stof(res.group('gain')),
            _stof(res.group('loss')))


def _stof(s):
    return float(s.replace(',', ''))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
