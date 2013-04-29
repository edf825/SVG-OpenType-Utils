#!/usr/bin/python

# Takes an SVG document, returns all the glyphchar and glyphid values found

import sys

from xml.sax import parseString, handler

class SVGInfo(handler.ContentHandler):

  def __init__(self, filename):
    self.glyph_ids = []
    self.glyph_chars = []

    # Let the exception be handled downstream. Should probably document this.
    svgfile = open(filename, 'r')
    self.svg_text = svgfile.read()
    self.do_svg_walk(self.svg_text)

  def do_svg_walk(self, svgfile):
    parseString(svgfile, self)

    print str(self.glyph_ids) + "\n" + str(self.glyph_chars)

    return (self.glyph_ids, self.glyph_chars)

  def startElement(self, name, attrs):
    if attrs.has_key("glyphchar"):
      self.glyph_chars.append(attrs.getValue("glyphchar"))
    if attrs.has_key("glyphid"):
      self.glyph_ids.append(int(attrs.getValue("glyphid")))
