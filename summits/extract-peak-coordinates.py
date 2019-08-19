#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Extracts peak coordinates from, e.g.
https://www.peakbagger.com/peak.aspx?pid=6048.
"""

from __future__ import print_function
import os
import sys
import argparse
from bs4 import BeautifulSoup


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infiles', help="Comma separated infiles", type=str)

    args = parser.parse_args(arguments)

    print("Name, Lat, Long")
    for filename in args.infiles.split(","):
        with open(filename, 'r') as f:
            soup = BeautifulSoup(f.read())
            info = [l.text for l in soup.find_all("td") if '&deg' in l.text][1]
            lat = info[info.find("W4") + 1:info.find(",", info.find("W4"))]
            long = info[info.find(" ", info.find("W4")):info.
                        find(" ",
                             info.find(" ", info.find("W4")) + 1)]
            el = [l.text for l in soup.find_all("h2")][0]
            name = [l.text for l in soup.find_all("h1")][0]
            print("\"%s (%s)\", %s,%s" % (name, el, lat, long))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
