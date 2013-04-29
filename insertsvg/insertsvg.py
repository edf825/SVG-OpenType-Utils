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

font = FontInfo(in_font_filename)
cmap = CmapTable(font.tables['cmap'].data)
svgtable = SVGTable(cmap, map(SVGInfo, svg_filenames))
font.tables['SVG '] = svgtable

out_file = open(out_font_filename, "w")
out_file.write(font.serialize())
out_file.close()
