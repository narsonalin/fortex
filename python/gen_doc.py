#!/usr/bin/env python3
# coding: utf-8

# Code d'Evolution Stellaire, Adaptatif et Modulaire for the 2020 decade.
# Copyright (c) 1997-2023 The Cesam2k20 authors
# SPDX-License-Identifier : GPL-3.0-or-later


import argparse

from CAutoGenF import CAutoGenF

parser = argparse.ArgumentParser()
parser.add_argument('list', type=str, default=None, help='file name with list of files' )

if __name__ == '__main__':

    args = parser.parse_args()

    with open( args.list, 'r' ) as f:
        files = f.readlines()

    path = files[0].replace( '\n', '')

    for file in files[1:]:
        if file[0][0] != '#':
            file = file.split( )
            if len( file ) == 6:
                doc = CAutoGenF( file[0], out=file[1], path=path, depth=int(file[2]), ttype=bool(int(file[3])),
                    write_vars=bool(int(file[4])), pprog=bool(int(file[5])) )
                doc.parse()
                doc.write_latex( )
