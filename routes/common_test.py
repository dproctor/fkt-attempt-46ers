#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Tests for common.py.

Dev command:
 ls routes/*py | entr -c -s 'python3 routes/common_test.py'
"""

import unittest
import common
import csv
import re

SPARSE_DISTANCE_CSV_STRING = """,p1,p2,p3
p1,,"Distance: 1.0 mi\n+1,000 ft / -100 ft",
p2,,,"Distance: 2.0 mi\n+2,000 ft / -200 ft"
p3,,,
"""


class TestParseDistanceMatrix(unittest.TestCase):
    def _simple_cost(x):
        if x is None: return int(1e9)
        return x[0]

    def setUp(self):
        self.distance = common.parse_distance_matrix(
            csv.reader(re.findall('(?:"[^"]*"|.)+',
                                  SPARSE_DISTANCE_CSV_STRING)),
            TestParseDistanceMatrix._simple_cost)

    def test_back_distances(self):
        self.assertEqual(self.distance['p1']['p2'], (1.0, 1000.0, 100.0))
        self.assertEqual(self.distance['p2']['p1'], (1.0, 100.0, 1000.0))

        self.assertEqual(self.distance['p2']['p3'], (2.0, 2000.0, 200.0))
        self.assertEqual(self.distance['p3']['p2'], (2.0, 200.0, 2000.0))

    def test_self_distance(self):
        self.assertEqual(self.distance['p1']['p1'], (0.0, 0.0, 0.0))
        self.assertEqual(self.distance['p2']['p2'], (0.0, 0.0, 0.0))
        self.assertEqual(self.distance['p3']['p3'], (0.0, 0.0, 0.0))

    def test_transitive_distance(self):
        self.assertEqual(self.distance['p1']['p3'], (3.0, 3000.0, 300.0))
        self.assertEqual(self.distance['p3']['p1'], (3.0, 300.0, 3000.0))


if __name__ == '__main__':
    unittest.main()
