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
    padding = ("\0" * ((4 - (self.length % 4)) % 4));
    self.data += padding
    self.padded_length = self.length + len(padding)

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

  def make_header(self, offset):
    struct.pack(header_format, self.tag[0], self.tag[1], self.tag[2], self.tag[3],
                self.compute_checksum(), offset, self.length)

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

  def read_tables(self):
    for i in range(self.num_tables):
      table = FontTable(i, self.data)
      self.tables[table.tag] = table

  def get_table_headers(self):
    return self.tables.keys()
