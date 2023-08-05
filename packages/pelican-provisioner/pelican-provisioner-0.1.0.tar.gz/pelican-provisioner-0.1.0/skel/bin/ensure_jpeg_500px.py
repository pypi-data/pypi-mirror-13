#!/usr/bin/env python

import sys, os, glob, re, datetime, time

# ensure a JPEG has the correct proportions

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s \"[pdf_filename]\"\n\n" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

noext = os.path.splitext(filename)[0]
magick_cmd = "mogrify -resize 500x {noext}.jpg".format(noext=noext)
os.system(magick_cmd)
