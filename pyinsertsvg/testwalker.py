#!/usr/bin/python

from svgwalker import SVGInfo
from fontinfo import FontInfo
from cmap import CmapTable
from svgtable import SVGTable

svg = SVGInfo("test.svg")

font = FontInfo("UVSLiberation.otf")
cmap = CmapTable(font.tables['cmap'].data)

for glyph_char in svg.glyph_chars:
  print glyph_char + " => " + str(cmap.map_glyph(glyph_char))

svgtable = SVGTable(cmap, map(SVGInfo, ["reftest1.svg", "reftest2.svg",
                                        "reftest3.svg", "reftest4.svg"]))

font.tables['SVG '] = svgtable

outfile = open("out.otf", "w")
outfile.write(font.serialize())
outfile.close()
