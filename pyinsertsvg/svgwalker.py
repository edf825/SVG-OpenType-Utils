#!/usr/bin/python

# Takes an SVG document, returns all the glyphchar and glyphid values found

import sys

from xml.sax import make_parser, handler

class SVGWalker(handler.ContentHandler):

  def __init__(self):
    self.glyph_ids = [];
    self.glyph_chars = [];

  def startElement(self, name, attrs):
    if attrs.has_key("glyphchar"):
      self.glyph_chars.append(attrs.getValue("glyphchar"))
    if attrs.has_key("glyphid"):
      self.glyph_ids.append(int(attrs.getValue("glyphid")))

def get_glyph_lists(filename):
  walker = SVGWalker()

  try:
    parser = make_parser()
    parser.setContentHandler(walker)
    parser.parse(filename)
  except IOError as ioex:
    print "Couldn't open file " + filename
    sys.exit(1);

  print filename + ":\n" + str(walker.glyph_ids) + "\n" + str(walker.glyph_chars)

  return (walker.glyph_ids, walker.glyph_chars)
