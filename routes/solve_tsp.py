#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Solves the Travelling Salesman Problem (TSP) for the provided distance matrix.

Dev command: ls routes/*.py | entr -c -s "python3 routes/solve_tsp.py '-d https://docs.google.com/spreadsheets/u/0/d/19ft1S-RoGl5jbBcyiCKPZuqL4a4MvFkjW_hu6I87Fhc/export?format=csv&id=19ft1S-RoGl5jbBcyiCKPZuqL4a4MvFkjW_hu6I87Fhc&gid=0'"

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

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import common

from io import StringIO


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d',
                        '--distance_matrix',
                        help='Url of distance matrix',
                        type=str)
    parser.add_argument(
        '-pw',
        '--pairwise_distances',
        help='csv file containing pairwise distances between peaks',
        type=argparse.FileType('r'))

    args = parser.parse_args(arguments)

    response = requests.get(args.distance_matrix)
    assert response.status_code == 200, 'Download failed'

    reader = csv.reader(StringIO(response.content.decode("utf-8")))
    print('Using cost function:',
          common.DEFAULT_COST.__name__,
          file=sys.stderr)
    distance_matrix = common.parse_distance_matrix(reader, common.DEFAULT_COST)

    # Parse pairwise distances
    pairs_distances = common.parse_distance_matrix_from_pairs(
        csv.reader(args.pairwise_distances))
    distance_matrix = common.merge_pairwise_and_matrix_distances(
        pairs_distances, distance_matrix)
    peaks = list(distance_matrix.keys())

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        1,  # num_vehicles
        len(distance_matrix) - 1)  # trailhead

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return common.DEFAULT_COST(
            distance_matrix[peaks[from_node]][peaks[to_node]])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.SAVINGS)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 30
    search_parameters.log_search = True

    assignment = routing.SolveWithParameters(search_parameters)

    if assignment:
        _print_solution(manager, routing, assignment, peaks, distance_matrix)


def _print_solution(manager, routing, assignment, peaks, distances):
    """Prints assignment on console."""
    index = routing.Start(0)
    route_distance = (0, 0, 0)
    while not routing.IsEnd(index):
        print(peaks[manager.IndexToNode(index)], file=sys.stdout)
        previous_index = index
        index = assignment.Value(routing.NextVar(index))
        edge_distance = distances[peaks[manager.IndexToNode(previous_index)]][
            peaks[manager.IndexToNode(index)]]

        route_distance = tuple(map(sum, zip(route_distance, edge_distance)))
        print(
            '{0:<25}     >     {1: <25} ({2:.1f} miles, +{3:.0f} ft / -{4:.0f} ft)'
            .format(peaks[manager.IndexToNode(previous_index)],
                    peaks[manager.IndexToNode(index)], edge_distance[0],
                    edge_distance[1], edge_distance[2]),
            file=sys.stderr)
    print(peaks[manager.IndexToNode(index)], file=sys.stdout)
    print('Optimal route computed (Objective value: {})'.format(
        common.DEFAULT_COST(route_distance)),
          file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
