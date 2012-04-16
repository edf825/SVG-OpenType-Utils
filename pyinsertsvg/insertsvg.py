#!/usr/bin/python

import sys

from svgwalker import SVGInfo
from fontinfo import FontInfo
from cmap import CmapTable
from svgtable import SVGTable

if len(sys.argv) < 4:
  print "Usage: " + sys.argv[0] + " <opentype font> <output file> <svg file> [<svg file>*]"
  sys.exit(1)

in_font_filename = sys.argv[1]
out_font_filename = sys.argv[2]
svg_filenames = sys.argv[3:]


