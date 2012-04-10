#!/usr/bin/python

from fontinfo import *
from cmap import *

font = FontInfo("UVSLiberation.otf")
print font.get_header()
print font.get_table_headers()
cmap = CmapTable(font.tables['cmap'].data)
print "L UVS => " + str(cmap.map_glyph(76, 0xFE01))
