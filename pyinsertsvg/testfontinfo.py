#!/usr/bin/python

from fontinfo import *
from cmap import *
from sys import *

font = FontInfo("UVSLiberation.otf")
print font.get_header()
print font.get_table_headers()
cmap = CmapTable(font.tables['cmap'].data)
print "L UVS => " + str(cmap.map_glyph('L', u'\ufe01'))

serd = font.serialize()

outfile = open('out.ttf', 'w')
outfile.write(serd)
outfile.close()
