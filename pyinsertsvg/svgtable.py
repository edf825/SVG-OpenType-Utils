#!/usr/bin/python

import struct
from fontinfo import FontTable

class SVGTable(FontTable):

  table_version = 1

# version, num index entries
  header_format = ">HH"
  header_size = struct.calcsize(header_format)

# start glyph, end glyph, doc offset, doc length
  index_format = ">HHLL"
  index_size = struct.calcsize(index_format)

  def __init__(self, cmap, svg_array):
    self.cmap = cmap
    self.svg_array = svg_array
    self.tag = "SVG "
    self.padded_length = 0

    self.make_svg_ranges()
    self.make_data()

  def make_svg_ranges(self):
    self.ranges = []

    # map individual glyph ids
    mappings = {}
    for i in reversed(range(len(self.svg_array))):
      svg = self.svg_array[i]
      # LOOK AT ME, AREN'T I JUST MISTER FUNCTIONAL NOW?
      glyph_ids = svg.glyph_ids + map(self.cmap.map_glyph, svg.glyph_chars)
      for glyph_id in glyph_ids:
        mappings[glyph_id] = i

    keys = sorted(mappings.keys())
    if len(keys) == 0:
      return

    first_glyph = keys[0]
    last_glyph = keys[0]
    last_doc = mappings[first_glyph]
    for key in keys:
      if last_doc != mappings[key]:
        self.ranges.append((first_glyph, last_glyph + 1, last_doc))
        first_glyph = key
        last_doc = mappings[key]
      last_glyph = key

    self.ranges.append((first_glyph, last_glyph + 1, last_doc))

    print self.ranges

  def make_data(self):
    data = ""
    offset = self.header_size + \
             self.index_size * len(self.ranges)

    data = struct.pack(self.header_format, self.table_version, len(self.ranges))

    svg_offsets = []
    for svg in self.svg_array:
      svg_offsets.append(offset)
      offset += len(svg.svg_text)

    for (start_glyph, end_glyph, doc_id) in self.ranges:
      data += struct.pack(self.index_format, start_glyph, end_glyph,
                          svg_offsets[doc_id],
                          len(self.svg_array[doc_id].svg_text))
      print "offset " + str(svg_offsets[doc_id]) + \
              "; len " + str(len(self.svg_array[doc_id].svg_text))

    for svg in self.svg_array:
      data += svg.svg_text

    self.data = data
    self.pad_data()
