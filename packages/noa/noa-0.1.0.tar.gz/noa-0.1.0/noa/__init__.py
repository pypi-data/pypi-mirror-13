#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
import yaml
import argparse

this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "defaults.yaml")

with open(DATA_PATH) as f:
    REGEXES = yaml.load(f)


def available_regexes():
    availables = []
    for key in REGEXES:
        availables.append(key)
        for subkey in REGEXES[key]:
            if subkey != 'regex':
                availables.append('{}:{}'.format(key, subkey))
    return availables


parser = argparse.ArgumentParser(prog='noa', description='This is the better port of qf.')

parser.add_argument('regex', action="store", choices=available_regexes())
parser.add_argument('file', action="store", nargs='?', type=argparse.FileType('r'))


def create_pattern(key):
    if ':' in key and key.split(':') == 2:
        if key.split(':')[0] in REGEXES and key.split(':')[1] in REGEXES[key.split(':')[0]]:
            return re.compile(REGEXES[key.split(':')[0]]['regex'], flags=re.IGNORECASE)
    elif key:
        if key in REGEXES:
            return re.compile(REGEXES[key]['regex'], flags=re.IGNORECASE)


def main():
    args = parser.parse_args()
    if args.file is None:
        text = sys.stdin.read()
    else:
        text = args.file.read()

    regex = create_pattern(args.regex)

    print('\n'.join(regex.findall(text)))

if __name__ == '__main__':
    main()
