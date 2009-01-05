#!/usr/bin/env python2.5
from __future__ import with_statement
from xml.sax.saxutils import escape, quoteattr
import StringIO

class Element(object):
    def __init__(self, name, attributes=None, contents=None):
        self.name = name
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if contents:
            self.contents = contents
        else:
            self.contents = []

    # methods for a with-block
    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb): pass

    def cdata(self, contents):
        cdata = CData(contents)
        self.contents.append(cdata)
        return cdata

    def comment(self, text):
        comment = Comment(text)
        self.contents.append(comment)
        return comment

    def element(self, name, attributes=None, contents=None):
        element = Element(name, attributes, contents)
        self.contents.append(element)
        return element

    def tag(self, name, attributes=None, contents=None):
        return self.element(name, attributes, contents)

    def text(self, text):
        t = Text(text)
        self.contents.append(t)
        return t

    def render(self, out, indentation=0, margin=0):
        # start tag:
        ident = margin*indentation*" "
        newline = "\n" if indentation > 0 else ""
        out.write(newline)
        out.write(ident+"<%s" % self.name)
        for name, value in self.attributes.iteritems():
            out.write(" %s=%s" % (name, quoteattr(value)))
        if len(self.contents) == 0:
            out.write(" />") # end tag
        else:
            out.write(">")
            for content in self.contents:
                if type(content) == str:
                    out.write(newline+ident+str(content))
                else:
                    content.render(out, indentation, margin+1)
            out.write(newline+ident+"</%s>" % self.name)

    def __str__(self):
        out = StringIO.StringIO()
        self.render(out, 0, 0)
        return out.getvalue()


class Text(object):
    def __init__(self, text):
        self.text = text

    def render(self, out, indentation=0, margin=0):
        out.write(str(self))

    def __str__(self):
        return escape(str(self.text))


# <!-- comment -->
class Comment(object):
    def __init__(self, text):
        self.text = text

    def render(self, out, indentation=0, margin=0):
        out.write(str(self))

    def __str__(self):
        if str(self.text).find("--") > -1:
            raise ValueError, "The string \"--\" (double-hyphen) MUST NOT occur within comments."
        return "<!-- %s -->" % escape(str(self.text))


# <![CDATA[ <element>this element and '&' is not seen as markup</element>]]>
class CData(object):
    def __init__(self, contents):
        self.contents = contents

    def render(self, out, indentation=0, margin=0):
        out.write("<![CDATA[")
        out.write(self.contents)
        out.write("]]>")

    def __str__(self):
        if self.contents.find(']]>') > -1:
            raise ValueError, "CDATA can contain all characters except for the ']]>' combination."
        return "<![CDATA[%s]]>" % self.contents


# <?xml version="1.0" encoding="utf-8" ?>
class XmlDeclaration(object):
    def __init__(self, name="xml", version="1.0", encoding="UTF-8", standalone=None):
        self.name = name
        self.version = version
        self.encoding = encoding
        self.standalone = standalone

    def __str__(self):
        s = '<?'+self.name
        s += " version=%s" % quoteattr(self.version)
        if self.encoding:
            s += " encoding=%s" % quoteattr(self.encoding)
        if self.standalone:
            s += " standalone=%s" % quoteattr(self.standalone)
        s += "?>"
        return s


#<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/SVG/DTD/svg10.dtd">
class Doctype(object):
    def __init__(self, system_id=None, public_id=None, internal_subset=None):
        self.system_id = system_id
        self.public_id = public_id
        self.internal_subset = internal_subset

    def __str__(self):
        if self.system_id:
            s = '<!DOCTYPE'
            s += ' '+str(self.system_id)
            if self.public_id:
                s += ' '+str(self.public_id)
            if self.internal_subset:
                s += ' '+str(self.internal_subset)
            s += '>'
            return s
        else:
            return ""


# this is like an element prepended by a xml-declaration and a doctype
class XmlDocument(Element):
    def __init__(self, root_element, attributes=None, contents=None, xmldecl=None, doctype=""):
        Element.__init__(self, root_element, attributes, contents)
        if xmldecl:
            self.xmldecl= xmldecl
        else:
            self.xmldecl = XmlDeclaration()
        if doctype:
            self.doctype = doctype
        else:
            self.doctype = Doctype()

    def __str__(self):
        return str(self.xmldecl) + str(self.doctype) + Element.__str__(self)


if __name__ == '__main__':
    foo = Element("foo")
    foo.contents += "lalala"
    foo.tag("x")

    bar = Element("bar", {"thing": "baz"})
    bar.contents.append("dinges")
    foo.contents.append(bar)

    baz = XmlDocument("baz", doctype="")
    with baz.tag("WithBlock"): pass
    baz.tag("WithoutBlock")
    with baz.tag("stuff") as stuff:
        with stuff.tag("Y") as y:
            y.comment("why?")
        with stuff.tag("X") as x:
            x.tag("Z")
            x.text("'x&z'")
        stuff.comment("stuff is fun")
        with stuff.tag("Block") as block:
            block.text("blocks are fun too!")
        stuff.contents.append( Comment("lalala") )
    baz.cdata("huh?")

    print foo
    print bar
    print baz


    head = Element("head")
    with head as h:
        with h.tag("title") as t: t.text("builder.py")

    foo = XmlDocument("html", doctype='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">', attributes={ 'xmlns':"http://www.w3.org/1999/xhtml", 'lang':"en", 'xml:lang':"en"})
    foo.contents.append(head)
    with foo as f:
        with foo.tag("body") as body:
            with body.tag("p") as p:
                p.text("blah blah & yadda yadda")
                p.comment("replace with praise for builder.py")
                p.tag("br")
                p.text("that's all!")
    print foo
