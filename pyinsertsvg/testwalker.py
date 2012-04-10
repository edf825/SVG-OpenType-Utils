#!/usr/bin/python
from svgwalker import get_glyph_lists
from fontinfo import FontInfo
from cmap import CmapTable

(glyph_ids, glyph_chars) = get_glyph_lists("test.svg")

font = FontInfo("UVSLiberation.otf")
cmap = CmapTable(font.tables['cmap'].data)

for glyph_char in glyph_chars:
  glyph_id = 0
  if len(glyph_char) == 1:
    glyph_id = cmap.map_glyph(glyph_char[0])
  elif len(glyph_char) == 2:
    glyph_id = cmap.map_glyph(glyph_char[0], glyph_char[1])
  else:
    print "glyphchar string with bad length " + str(len(glyph_char))
    continue
  print glyph_char + " => " + str(glyph_id)
