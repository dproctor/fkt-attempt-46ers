#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Devon Proctor <devon.proctor@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Extracts peak urls from https://www.peakbagger.com/list.aspx?lid=5120.
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
    parser.add_argument('infile',
                        help="Input file",
                        type=argparse.FileType('r'))

    args = parser.parse_args(arguments)

    soup = BeautifulSoup(args.infile.read())
    urls = [
        "https://www.peakbagger.com/" + a['href']
        for a in soup.find_all('a', href=True) if 'peak.aspx' in a['href']
    ]
    for u in urls:
        print(u)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
