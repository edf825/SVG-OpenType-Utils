#!/usr/bin/python

import struct

class FontTable:

# tag, checksum, offset, length : all ULONG
  header_format = ">4c3L"
  header_size = struct.calcsize(header_format)

  def __init__(self, index, data):
    (a, b, c, d, self.checksum, self.offset, self.length) = \
      struct.unpack_from(self.header_format, data,
                         FontInfo.header_size + index * self.header_size)
    self.tag = a + b + c + d

    self.data = data[self.offset : self.offset + self.length]
    self.padded_length = 0
    self.pad_data()

    print "got table " + self.tag
    print "length " + str(len(self.data)) + " : " + str(self.length)
    print "checksum = " + str(self.checksum) + " : " + str(self.compute_checksum())

  def compute_checksum(self):
    sum = 0
    for i in range(self.padded_length / 4):
      word = struct.unpack_from(">L", self.data, i * 4)[0]
      sum += word
    sum %= 1 << 32
    return sum

  def make_header(self):
    return struct.pack(FontTable.header_format, self.tag[0], self.tag[1],
                       self.tag[2], self.tag[3], self.compute_checksum(),
                       self.offset, self.length)

  def pad_data(self):
    if self.padded_length == len(self.data):
      return

    length = len(self.data)
    padded_len = length + ((4 - (length % 4)) % 4)

    self.data += '\0' * (padded_len - length)
    self.length = length
    self.padded_length = padded_len

class FontInfo:

# version_major, version_minor, num_tables, search_range, entry_selector,
# range_shift
# all USHORT
  header_format = ">6H"
  header_size = struct.calcsize(header_format)

  def __init__(self, filename):
    f = open(filename, 'r')
    self.data = f.read();

    self.table_headers = {}
    self.tables = {}

    self.read_header();
    self.read_tables();

  def read_header(self):
    (self.version_major, self.version_minor, self.num_tables,
     self.search_range, self.entry_selector, self.range_shift) = \
     struct.unpack_from(self.header_format, self.data)

  def get_header(self):
    return (self.version_major, self.version_minor, self.num_tables,
            self.search_range, self.entry_selector, self.range_shift)

  def make_header(self):
    self.recompute_header_values()
    return struct.pack(self.header_format,
                       self.version_major, self.version_minor,
                       self.num_tables, self.search_range, self.entry_selector,
                       self.range_shift)

  def recompute_header_values(self):
    num_tables = len(self.tables)
    entry_selector = 0
    while 2**entry_selector <= num_tables:
      entry_selector = entry_selector + 1
    entry_selector = entry_selector - 1
    search_range = 2**entry_selector * 16
    range_shift = num_tables * 16 - search_range

    (self.num_tables, self.entry_selector, self.search_range, self.range_shift) = \
      (num_tables, entry_selector, search_range, range_shift)

  def read_tables(self):
    for i in range(self.num_tables):
      table = FontTable(i, self.data)
      self.tables[table.tag] = table

  def get_table_headers(self):
    return self.tables.keys()

  def serialize(self):
    tags = sorted(self.tables.keys())
    num_tables = len(tags)

    result = self.make_header()

    offset = FontInfo.header_size + num_tables * FontTable.header_size
    for tag in tags:
      table = self.tables[tag]
      table.offset = offset

      table.pad_data()
      offset += table.padded_length
      result += table.make_header()

    for tag in tags:
      result += self.tables[tag].data

    return result
