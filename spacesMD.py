#!/usr/bin/env python3
"""
Add trailing spaces to Markdown
Prevent the GitHub Markdown format to concatenate lines

Copyright (C) 2019 - Fred Rique (farique)
https://github.com/farique1/ConvertMD

spacesMD.py [source] [destination] -ns #
-ns #    :Number of spaces to add. Default = 2
Uses README.md if no [source] given
Overwrite [source] if [destination>] is omitted.
"""

import argparse

# Config
fileeLad = ''       # Source file
fileeSve = ''       # Destination file
trailing_spaces = 2
buffercode = []

# Set command line
parser = argparse.ArgumentParser(description='Add trailing spaces to the end of lines to conform with GitHub.')
parser.add_argument("input", nargs='?', default=fileeLad, help='Source file. Uses README.md if missing.')
parser.add_argument("output", nargs='?', default=fileeSve, help='Destination file. Overwrite [source] if missing.')
parser.add_argument("-ns", default=2, type=int, help="Number of spaces to add. Default = 2")
args = parser.parse_args()

# Apply chosen settings
fileeLad = args.input
fileeSve = args.output
if args.output == '':
    fileeSve = fileeLad
trailing_spaces = ' ' * args.ns

if not fileeLad:
    fileeLad = 'README.md'

file = open(fileeLad, 'r')
source = file.readlines()
file.close()

for line in source:
    line_alt = line
    line_alt = line_alt.rstrip()
    line_alt = line_alt + trailing_spaces + '\n'
    buffercode.append(line_alt)

save = open(fileeSve, 'w')
for line in buffercode:
    save.write(line)
save.close()
