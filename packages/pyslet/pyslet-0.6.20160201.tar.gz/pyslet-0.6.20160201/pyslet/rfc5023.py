#! /usr/bin/env python
"""Implements the Atom Publishing Protocol defined in RFC 5023

References:

IRIs [RFC3987]; cf URI [RFC3986]
Before an IRI in a document is used by HTTP, the IRI is first converted to a
URI according to the procedure defined in Section 3.1 of [RFC3987]

xml:base attribute [W3C.REC-xmlbase-20010627]
xml:lang attribute [W3C.REC-xml-20040204], Section 2.12
"""

import string
import StringIO
import sys
import io
import traceback

import pyslet.http.client as http
import pyslet.http.messages as messages
import pyslet.pep8 as pep8
import pyslet.rfc2396 as uri
import pyslet.rfc4287 as atom
import pyslet.xmlnames20091208 as xmlns


#: The namespace to use for Atom Publishing Protocol elements
APP_NAMESPACE = "http://www.w3.org/2007/app"
#: The mime type for service documents
ATOMSVC_MIMETYPE = "application/atomsvc+xml"
#: The mime type for category documents
ATOMCAT_MIMETYPE = "application/atomcat+xml"

APP_MIMETYPES = {
    ATOMSVC_MIMETYPE: True,
    ATOMCAT_MIMETYPE: True,
    atom.ATOM_MIMETYPE: True
}


def parse_yes_no(src):
    return src.strip().lower() == 'yes'


def format_yes_no(value):
    if value:
        return 'yes'
    else:
        return 'no'


class APPElement(xmlns.XMLNSElement):

    """Base class for all APP elements.

    All APP elements can have xml:base, xml:lang and/or xml:space attributes.
    These are handled by the base
    :py:class:`~pyslet.xml20081126.structures.Element` base class."""
    pass


class Accept(APPElement):

    """Represents the accept element."""
    XMLNAME = (APP_NAMESPACE, 'accept')


class Categories(APPElement):

    """The root of a Category Document.

    A category document is a document that describes the categories
    allowed in a collection."""
    XMLNAME = (APP_NAMESPACE, 'categories')

    XMLATTR_href = ('href', uri.URI.from_octets, str)
    XMLATTR_fixed = ('fixed', parse_yes_no, format_yes_no)
    XMLATTR_scheme = 'scheme'
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        APPElement.__init__(self, parent)
        self.href = None
        #: an optional :py:class:`~pyslet.rfc2396.URI` to the category
        self.fixed = None
        #: indicates whether the list of categories is a fixed set. By
        #: default they're open.
        self.scheme = None
        #: identifies the default scheme for categories defined by this
        #: element
        self.Category = []
        #: the list of categories, instances of
        #: :py:class:~pyslet.rfc4287.Category

    def GetChildren(self):  # noqa
        for child in self.Category:
            yield child
        for child in APPElement.GetChildren(self):
            yield child


class Service(APPElement):

    """The container for service information

    Associated with one or more Workspaces."""
    XMLNAME = (APP_NAMESPACE, 'service')
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        APPElement.__init__(self, parent)
        self.Workspace = []		#: a list of :py:class:`Workspace` instances

    def GetChildren(self):  # noqa
        for child in APPElement.GetChildren(self):
            yield child
        for child in self.Workspace:
            yield child


class Workspace(APPElement):

    """Workspaces are server-defined groups of Collections."""
    XMLNAME = (APP_NAMESPACE, 'workspace')
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        APPElement.__init__(self, parent)
        self.Title = None			#: the title of this workspace
        self.Collection = []		#: a list of :py:class:`Collection`

    def GetChildren(self):  # noqa
        for child in APPElement.GetChildren(self):
            yield child
        if self.Title:
            yield self.Title
        for child in self.Collection:
            yield child


class Collection(APPElement):

    """Describes a collection (feed)."""
    XMLNAME = (APP_NAMESPACE, 'collection')
    XMLCONTENT = xmlns.ElementContent

    XMLATTR_href = ('href', uri.URI.from_octets, str)

    def __init__(self, parent):
        APPElement.__init__(self, parent)
        self.href = None
        #: the URI of the collection (feed)
        self.Title = None
        #: the human readable title of the collection
        self.Accept = []
        #: list of :py:class:`Accept` media ranges that can be posted to
        #: the collection
        self.Categories = []
        # : list of :py:class:`Categories` that can be applied to
        # : members of the collection

    def GetChildren(self):  # noqa
        for child in APPElement.GetChildren(self):
            yield child
        if self.Title:
            yield self.Title
        for child in self.Accept:
            yield child
        for child in self.Categories:
            yield child

    @pep8.renamed_method
    def GetFeedURL(self):   # noqa
        pass

    def get_feed_url(self):
        """Returns a fully resolved URL for the collection (feed)."""
        return self.ResolveURI(self.href)


class Document(atom.AtomDocument):

    """Class for working with APP documents.

    This call can represent both APP and Atom documents."""
    classMap = {}

    def __init__(self, **args):
        atom.AtomDocument.__init__(self, **args)
        self.defaultNS = APP_NAMESPACE

    def ValidateMimeType(self, mimetype):   # noqa
        """Checks *mimetype* against the APP or Atom specifications."""
        return (mimetype in APP_MIMETYPES or
                atom.AtomDocument.ValidateMimeType(self, mimetype))

    @classmethod
    def get_element_class(cls, name):
        """Returns the APP or Atom class used to represent name.

        Overrides
        :py:meth:`~pyslet.rfc4287.AtomDocument.get_element_class` when the
        namespace is :py:data:`APP_NAMESPACE`."""
        if name[0] == APP_NAMESPACE:
            return cls.classMap.get(
                name, atom.AtomDocument.classMap.get((name[0], None),
                                                     APPElement))
        else:
            return atom.AtomDocument.get_element_class(name)

xmlns.MapClassElements(Document.classMap, globals())


class Slug(object):

    """Represents an HTTP slug header value.

    slug
            The opaque slug as a unicode string

    The built-in str function can be used to format instances according
    to the grammar defined in the specification.

    Instances must be treated as immutable, they define comparison
    methods and a hash implementation to allow them to be used as keys
    in dictionaries."""

    def __init__(self, slug):
        self.slug = slug		#: the slug value

    @classmethod
    def from_str(cls, source):
        """Creates a slug from a *source* string."""
        return cls(unicode(uri.unescape_data(source), 'utf-8'))

    def __str__(self):
        result = []
        for c in self.slug.encode('utf-8'):
            if c == '%' or ord(c) < 0x20 or ord(c) > 0x7E:
                result.append("%%%02X" % ord(c))
            else:
                result.append(c)
        return string.join(result, '')

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return "Slug(%s)" % repr(self.slug)

    def __cmp__(self, other):
        """Slugs are compared case sensitive."""
        if isinstance(other, unicode):
            result = cmp(self.slug, other)
        elif isinstance(other, str):
            other = Slug.from_str(other)
            result = cmp(self.slug, other.slug)
        elif isinstance(other, Slug):
            result = cmp(self.slug, other.slug)
        return result

    def __hash__(self):
        return hash(self.slug)


class Client(http.Client):

    def __init__(self, **kwargs):
        http.Client.__init__(self, **kwargs)

    def queue_request(self, request, timeout=60):
        # if there is no Accept header, add one
        if not request.has_header('Accept'):
            request.set_header('Accept', string.join(
                (atom.ATOM_MIMETYPE, ATOMSVC_MIMETYPE, ATOMCAT_MIMETYPE),
                ','), True)
        super(Client, self).queue_request(request, timeout)


class InputWrapper(io.RawIOBase):

    """A class suitable for wrapping the input object.

    The purpose of the class is to behave in a more file like way, so
    that applications can ignore the fact they are dealing with
    a wsgi input stream.

    The object will buffer the input stream and claim to be seekable for
    the first *seek_size* bytes.  Once the stream has been advanced
    beyond *seek_size* bytes the stream will raise IOError if seek is
    called.

    *environ* is the environment dictionary

    *seek_size* specifies the size of the seekable buffer, it defaults
    to io.DEFAULT_BUFFER_SIZE"""

    def __init__(self, environ, seek_size=io.DEFAULT_BUFFER_SIZE):
        super(InputWrapper, self).__init__()
        self.input_stream = environ['wsgi.input']
        if ('HTTP_TRANSFER_ENCODING' in environ and
                environ['HTTP_TRANSFER_ENCODING'].lower() != 'identity'):
            self.input_stream = messages.ChunkedReader(self.input_stream)
            # ignore the content length
            self.inputLength = None
        elif ("CONTENT_LENGTH" in environ and environ['CONTENT_LENGTH']):
            self.inputLength = int(environ['CONTENT_LENGTH'])
            if self.inputLength < seek_size:
                # we can buffer the entire stream
                seek_size = self.inputLength
        else:
            # read until EOF
            self.inputLength = None
        self.pos = 0
        self.buffer = None
        self.buffSize = 0
        if seek_size > 0:
            self.buffer = StringIO.StringIO()
            # now fill the buffer
            while self.buffSize < seek_size:
                data = self.input_stream.read(seek_size - self.buffSize)
                if len(data) == 0:
                    # we ran out of data
                    self.input_stream = None
                    break
                self.buffer.write(data)
                self.buffSize = self.buffer.tell()
            # now reset the buffer ready for reading
            self.buffer.seek(0)

    def read(self, n=-1):
        """This is the heart of our wrapper.

        We read bytes first from the buffer and, when exhausted, from
        the input_stream itself."""
        if self.closed:
            raise IOError("InputWrapper was closed")
        if n == -1:
            return self.readall()
        data = ''
        if n and self.pos < self.buffSize:
            data = self.buffer.read(n)
            self.pos += len(data)
            n = n - len(data)
        if n and self.input_stream is not None:
            if self.inputLength is not None and \
                    self.pos + n > self.inputLength:
                # application should not attempt to read past the
                # CONTENT_LENGTH
                n = self.inputLength - self.pos
            idata = self.input_stream.read(n)
            if len(idata) == 0:
                self.input_stream = None
            else:
                self.pos += len(idata)
                if data:
                    data = data + idata
                else:
                    data = idata
        return data

    def seek(self, offset, whence=io.SEEK_SET):
        if self.pos > self.buffSize:
            raise IOError("InputWrapper seek buffer exceeded")
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self.pos + offset
        elif whence == io.SEEK_END:
            if self.inputLength is None:
                raise IOError("InputWrapper can't seek from end of stream "
                              "(CONTENT_LENGTH unknown)""")
            new_pos = self.inputLength + offset
        else:
            raise IOError("Unknown seek mode (%i)" % whence)
        if new_pos < 0:
            raise IOError("InputWrapper: attempt to set the stream position "
                          "to a negative value")
        if new_pos == self.pos:
            return
        if new_pos <= self.buffSize:
            self.buffer.seek(new_pos)
        else:
            # we need to read and discard some bytes
            while new_pos > self.pos:
                n = new_pos - self.pos
                if n > io.DEFAULT_BUFFER_SIZE:
                    n = io.DEFAULT_BUFFER_SIZE
                data = self.read(n)
                if len(data) == 0:
                    break
                else:
                    self.pos += len(data)
        # new_pos may be beyond the end of the input stream, that's OK
        self.pos = new_pos

    def seekable(self):
        """A bit cheeky here, we are initially seekable."""
        if self.pos > self.buffSize:
            return False
        else:
            return True

    def fileno(self):
        raise IOError("InputWrapper has no fileno")

    def flush(self):
        pass

    def isatty(self):
        return False

    def readable(self):
        return True

    def readall(self):
        result = []
        while True:
            data = self.read(io.DEFAULT_BUFFER_SIZE)
            if data:
                result.append(data)
            else:
                break
        return string.join(result, '')

    def readinto(self, b):
        n = len(b)
        data = self.read(n)
        i = 0
        for d in data:
            b[i] = ord(d)
            i = i + 1
        return len(data)

    def readline(self, limit=-1):
        """Read and return one line from the stream.

        If limit is specified, at most limit bytes will be read.  The
        line terminator is always b'\n' for binary files."""
        line = []
        while limit < 0 or len(line) < limit:
            b = self.read(1)
            if len(b) == 0:
                break
            line.append(b)
            if b == '\n':
                break
        return string.join(line, '')

    def readlines(self, hint=-1):
        """Read and return a list of lines from the stream.

        No more lines will be read if the total size (in
        bytes/characters) of all lines so far exceeds hint."""
        total = 0
        lines = []
        for line in self:
            total = total + len(line)
            lines.append(line)
            if hint >= 0 and total > hint:
                break
        return lines

    def tell(self):
        return self.pos

    def truncate(self, size=None):
        raise IOError("InputWrapper cannot be truncated")

    def writable(self):
        return False

    def write(self, b):
        raise IOError("InputWrapper is not writable")

    def writelines(self):
        raise IOError("InputWrapper is not writable")

    def __iter__(self):
        while True:
            line = self.readline()
            if line:
                yield line


class Server(pep8.PEP8Compatibility):

    def __init__(self, service_root='http://localhost/', **kwargs):
        pep8.PEP8Compatibility.__init__(self)
        service_root = kwargs.get('serviceRoot', service_root)
        if not isinstance(service_root, uri.URI):
            #: the canonical URL of the service root
            self.serviceRoot = uri.URI.from_octets(service_root).canonicalize()
        else:
            self.serviceRoot = service_root.canonicalize()
        #: the :py:class:`Service` instance that describes this service.
        self.serviceDoc = Document(root=Service, baseURI=self.serviceRoot)
        self.service = self.serviceDoc.root
        # make the base explicit in the document
        self.service.SetBase(str(self.serviceRoot))
        #: set this to True to expose python tracebacks in 500
        #: responses, defaults to False
        self.debugMode = False

    def __call__(self, environ, start_response):
        """wsgi interface for calling instances of this Atom server object.

        We add an additional optional parameter *response_headers*"""
        response_headers = []
        if environ['SCRIPT_NAME'] + environ['PATH_INFO'] == \
                self.serviceRoot.abs_path:
            data = unicode(self.serviceDoc).encode('utf-8')
            response_headers.append(("Content-Type", ATOMSVC_MIMETYPE))
            response_headers.append(("Content-Length", str(len(data))))
            start_response("200 Ok", response_headers)
            return [data]
        else:
            return self.HandleMissing(environ, start_response)

    def handle_missing(self, environ, start_response):
        response_headers = []
        data = "This server supports the Atom Publishing Protocol\r\n"\
            "For service information see: %s" % str(self.serviceRoot)
        response_headers.append(("Content-Length", str(len(data))))
        response_headers.append(("Content-Type", 'text/plain'))
        start_response("404 Not found", response_headers)
        return [data]

    def handle_error(self, environ, start_response, code=500):
        """Designed to be called by an otherwise uncaught exception.

        Generates a 500 response by default."""
        response_headers = []
        cdata = StringIO.StringIO()
        if self.debugMode:
            traceback.print_exception(*sys.exc_info(), file=cdata)
        else:
            cdata.write("Sorry, there was an internal error "
                        "while processing this request")
        response_headers.append(("Content-Type", 'text/plain'))
        response_headers.append(("Content-Length", str(len(cdata.getvalue()))))
        start_response("%i Unexpected error" % code, response_headers)
        return [cdata.getvalue()]
