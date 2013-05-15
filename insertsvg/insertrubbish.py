#!/usr/bin/python

import sys

from svgwalker import SVGInfo
from fontinfo import FontInfo, FontTable
from cmap import CmapTable
from svgtable import SVGTable

class RawTable(FontTable):

  data = ""

  def __init__(self, filename):
    self.length = 0
    self.padded_length = 0
    self.tag = "SVG "
    fd = open(filename, "r")
    data = fd.read()
    fd.close()

  def make_data(self):
    self.pad_data()

if len(sys.argv) < 4:
  print "Usage: " + sys.argv[0] + " <opentype font> <output file> <rubbish file>"
  sys.exit(1)

in_font_filename = sys.argv[1]
out_font_filename = sys.argv[2]
rubbish_filename = sys.argv[3]

font = FontInfo(in_font_filename)
cmap = CmapTable(font.tables['cmap'].data)
rawtable = RawTable(rubbish_filename)
font.tables['SVG '] = rawtable

out_file = open(out_font_filename, "w")
out_file.write(font.serialize())
out_file.close()

