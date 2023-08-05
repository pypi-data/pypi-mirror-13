#!/usr/bin/env python

import sys, os, glob, re, datetime, time

# convert a PDF, such as a poster, to a PNG thumbnail

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s \"[pdf_filename]\"\n\n" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

noext = os.path.splitext(filename)[0]
magick_cmd = "convert {noext}.pdf -resize 500x -flatten -background white {noext}.jpg".format(noext=noext)
os.system(magick_cmd)
