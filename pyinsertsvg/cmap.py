#!/usr/bin/python

import struct

class CmapTable:

# version, numTables : all USHORT
  header_format = ">HH"
  header_size = struct.calcsize(header_format)

# platformID, encodingID, offset : USHORT, USHORT, ULONG
  subheader_format = ">HHL"
  subheader_size = struct.calcsize(subheader_format)

  def __init__(self, data):
    self.data = data
    (self.version, self.num_tables) = struct.unpack_from(self.header_format, data)
    self.read_subtables()

  def read_subtables(self):
    self.subtables = []

    for i in range(self.num_tables):
      (platform, encoding, offset) = struct.unpack_from(self.subheader_format, self.data,
                                                        self.header_size + i * self.subheader_size)
      cmap_format = struct.unpack_from(">H", self.data, offset)[0]
      if cmap_format == 4:
        subtable = Cmap4Subtable(self.data[offset:])
      elif cmap_format == 14:
        subtable = Cmap14Subtable(self.data[offset:])
      else:
        print "Unsupported subtable format " + str(cmap_format) + ": ignoring."
        continue
      self.subtables.append(subtable)

  def map_glyph(self, char, var_selector = '\0'):
    for subtable in self.subtables:
      glyph_id = subtable.map_glyph(ord(char), ord(var_selector))
      if glyph_id and glyph_id != 0:
        return glyph_id
    if var_selector != 0:
      return self.map_glyph(ord(char))
    return 0

class Cmap4Subtable:

# format, length, language, segCountX2, searchRange, entrySelector, rangeShift
  header_format = ">7H"
  header_size = struct.calcsize(header_format)

  def __init__(self, data):
    self.data = data
    (self.format, self.length, self.language, self.seg_count, self.search_range,
     self.entry_selector, self.range_shift) = \
        struct.unpack_from(self.header_format, self.data)

    self.seg_count /= 2

    print "Got a format " + str(self.format) + " cmap table with " + \
      str(self.seg_count) + " segments"

    self.read_mappings()

  def read_mappings(self):
    array_format = ">" + str(self.seg_count) + "H"
    array_format_signed = ">" + str(self.seg_count) + "h"
    array_size = struct.calcsize(array_format)

    self.end_count = struct.unpack_from(array_format, self.data, self.header_size)
    self.start_count = struct.unpack_from(array_format, self.data,
                                          self.header_size + array_size + 2)
    self.id_delta = struct.unpack_from(array_format_signed, self.data,
                                       self.header_size + array_size * 2 + 2)

# This actually gets both the idRangeOffset _and_ glyphIdArray tables because
# the spec assumes we're using a nice language like C and so does some address
# hackery
    total_length = self.header_size + array_size * 3 + 2
    id_range_offset_length = (self.length - total_length) / 2
    id_range_offset_format = ">" + "H" * id_range_offset_length
    self.id_range_offset = struct.unpack_from(id_range_offset_format, self.data,
                                              total_length)

    for i in range(self.seg_count):
      print "maps " + str(self.start_count[i]) + "," + str(self.end_count[i]) + \
        " by delta " + str(self.id_delta[i]) + \
        " and idRangeOffset " + str(self.id_range_offset[i])

  def map_glyph(self, char, var_selector):
    if var_selector != 0:
      return 0

    for i in range(self.seg_count):
      if char <= self.end_count[i] and char >= self.start_count[i]:

        if self.id_range_offset[i] != 0:
          # This bit not tested very well, but rare enough anyway
          offset = self.id_range_offset[i] / 2 + (char - self.start_count[i])
          index = self.id_range_offset[i + offset]
          if index == 0:
            continue
          # XXX Does negative mod -> negative in python? I dunno
          return ((index + self.id_delta[i]) + 65536) % 65536

        return char + self.id_delta[i]

    

class Cmap14Subtable:

# format, length, numVarSelectorRecords
  header_format = ">HLL"
  header_size = struct.calcsize(header_format)

# varSelector (bytewise---stupid uint24), defaultUVSOffset, nonDefaultUVSOffset
  record_format = ">BHLL"
  record_size = struct.calcsize(header_format)

  def __init__(self, data):
    self.data = data
    (self.format, self.length, self.num_records) = struct.unpack_from(self.header_format,
                                                                      self.data)

    print "Got a format " + str(self.format) + " cmap table with " + \
      str(self.num_records) + " records"

    self.read_mappings()

  def read_mappings(self):
    self.default_offsets = {}
    self.non_default_offsets = {}
    for i in range(self.num_records):
      (a, b, default_offset, non_default_offset) = \
        struct.unpack_from(self.record_format, self.data,
                           self.header_size + i * self.record_size)
# BITSHIFT OPERATOR PRECEDENCE STRIKES AGAIN
      self.default_offsets[(a<<16) + b] = default_offset
      self.non_default_offsets[(a<<16) + b] = non_default_offset

      print "Got var selector " + str((a << 16) + b)

  def map_glyph(self, char, var_selector):
    # Hacky and not entirely correct, but mostly we just want the non-default
    #   part to be right anyway
    default_offset = self.default_offsets[var_selector]
    non_default_offset = self.non_default_offsets[var_selector]

    if default_offset and default_offset != 0:
      # Ignore this case: we fall back to default glyphs if no UVS matches
      #   anyway
      print str(var_selector) + " has default offset " + str(default_offset)

    if non_default_offset and non_default_offset != 0:
      print str(var_selector) + " has non-default offset " + str(non_default_offset)
      print "mappings for " + str(var_selector) + ":"

      num_values = struct.unpack_from(">L", self.data, non_default_offset)[0]
      for i in range(num_values):
        # length of "L" = 4, length of "BHH" = 5
        (charcode_high, charcode_low, glyph_id) = \
         struct.unpack_from(">BHH", self.data, non_default_offset + 4 + i * 5)

        charcode = (charcode_high << 16) + charcode_low
        print str((charcode, glyph_id))
        if char == charcode:
          return glyph_id

    return 0

