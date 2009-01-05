#!/usr/bin/env python2.5

from builder import *

#<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
class SvgDocument(XmlDocument):
    def __init__(self):
        XmlDocument.__init__(self, "svg", None, Doctype("svg"))

if __name__ == '__main__':
    svg = SvgDocument()
    print svg
