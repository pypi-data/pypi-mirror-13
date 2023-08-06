#! /usr/bin/env python
"""Utilities for writing applications based on wsgi"""

import base64
import cgi
import io
import json
import mimetypes
import optparse
import os
import os.path
import random
import string
import StringIO
import sys
import threading
import time
import urllib
import urlparse

from hashlib import sha256
from wsgiref.simple_server import make_server

try:
    from Crypto.Cipher import AES
    from Crypto import Random
    got_crypto = True
except ImportError:
    got_crypto = False

import pyslet.http.cookie as cookie
import pyslet.http.messages as messages
import pyslet.http.params as params
import pyslet.iso8601 as iso
import pyslet.odata2.core as odata
import pyslet.odata2.csdl as edm
import pyslet.odata2.metadata as edmx
import pyslet.xml20081126.structures as xml

from pyslet.odata2.sqlds import SQLEntityContainer
from pyslet.rfc2396 import URI, FileURL

import logging
logger = logging.getLogger('pyslet.wsgi')


class BadRequest(Exception):

    """An exception that will generate a 400 response code"""
    pass


class PageNotAuthorized(BadRequest):

    """An exception that will generate a 403 response code"""
    pass


class PageNotFound(BadRequest):

    """An exception that will generate a 404 response code"""
    pass


class MethodNotAllowed(BadRequest):

    """An exception that will generate a 405 response code"""
    pass


class SessionError(RuntimeError):

    """Unexpected session handling error"""
    pass


def generate_key(key_length=128):
    """Generates a new key

    key_length
        The minimum key length in bits.  Defaults to 128.

    The key is returned as a sequence of 16 bit hexadecimal
    strings separated by '.' to make them easier to read and
    transcribe into other systems."""
    key = []
    if key_length < 1:
        raise ValueError("wsgi.generate_key(%i)" % key_length)
    nfours = (key_length + 15) // 16
    try:
        rbytes = os.urandom(nfours * 2)
        for i in xrange(nfours):
            four = "%02X%02X" % (
                ord(rbytes[2 * i]), ord(rbytes[2 * i + 1]))
            key.append(four)
    except NotImplementedError:
        logger.warn("urandom required for secure key generation")
        for i in xrange(nfours):
            four = []
            for j in xrange(4):
                four.append(random.choice('0123456789ABCDEF'))
            key.append(string.join(four, ''))
    return string.join(key, '.')


def key60(src):
    """Generates a non-negative 60-bit long from a source string.

    src
        A binary string.

    The idea behind this function is to create an (almost) unique
    integer from a given string.  The integer can then be used as the
    key field of an associated entity without having to create foreign
    keys that are long strings.  There is of course a small chance that
    two source strings will result in the same integer.

    The integer is calculated by truncating the SHA256 hexdigest to 15
    characters (60-bits) and then converting to long.  Future versions
    of Python promise improvements here, which would allow us to squeeze
    an extra 3 bits using int.from_bytes but alas, not in Python 2.x"""
    return long(sha256(src).hexdigest()[0:15], 16)


class WSGIContext(object):

    """A class used for managing WSGI calls

    environ
        The WSGI environment

    start_response
        The WSGI call-back

    This class acts as a holding place for information specific to each
    request being handled by a WSGI-based application.  In some
    frameworks this might be called the request object but we already
    have requests modelled in the http package and, anyway, this holds
    information about the WSGI environment and the response too."""

    #: The maximum amount of content we'll read into memory (64K)
    MAX_CONTENT = 64 * 1024

    def __init__(self, environ, start_response):
        #: the WSGI environ
        self.environ = environ
        #: the WSGI start_response callable
        self.start_response_method = start_response
        #: the response status code (an integer), see :meth:`set_status`
        self.status = None
        #: the response status message (a string), see :meth:`set_status`
        self.status_message = None
        #: a *list* of (name, value) tuples containing the headers to
        #: return to the client.  name and value must be strings
        self.headers = []
        self._query = None
        self._content = None
        self._form = None
        self._cookies = None

    def set_status(self, code):
        """Sets the status of the response

        code
            An HTTP *integer* response code.

        This method sets the :attr:`status_message` automatically from
        the code.  You must call this method before calling
        start_response."""
        self.status = code
        self.status_message = messages.Response.REASON.get(code, "Unknown")

    def add_header(self, name, value):
        """Adds a header to the response

        name
            The name of the header (a string)

        value
            The value of the header (a string)"""
        self.headers.append((name, value))

    def start_response(self):
        """Calls the WSGI start_response method

        If the :attr:`status` has not been set a 500 response is
        generated.  The status string is created automatically from
        :attr:`status` and :attr:`status_message` and the headers are
        set from :attr:`headers`.

        The return value is the return value of the WSGI start_response
        call, an obsolete callable that older applications use to write
        the body data of the response.

        If you want to use the exc_info mechanism you must call
        start_response yourself directly using the value of
        :attr:`start_response_method`"""
        if self.status is None:
            self.status = 500
            self.status_message = messages.Response.REASON.get(500,
                                                               "No status")
        return self.start_response_method(
            "%i %s" % (self.status, self.status_message), self.headers)

    def get_app_root(self, authority=None):
        """Returns the root of this application

        authority
            The URL scheme and authority (including optional port) that
            should be used instead of the information obtained from the
            WSGI environment (e.g., the SERVER_NAME and SERVER_PORT
            variables).

        The result is a :class:`pyslet.rfc2396.URI` instance, It is
        calculated from the environment in the same way as
        :meth:`get_url` but only examines the SCRIPT_NAME portion of the
        path.

        It always ends in a trailing slash.  So if you have a script
        bound to /script/myscript.py running over http on
        www.example.com then you will get::

            http://www.example.com/script/myscript.py/

        This allows you to generate absolute URLs by resolving them relative
        to the computed application root, e.g.::

            URI.from_octets('images/counter.png').resolve(
                context.get_app_root())

        would return::

            http://www.example.com/script/myscript.py/images/counter.png

        for the above example.  This is preferable to using absolute
        paths which would strip away the SCRIPT_NAME prefix when used."""
        if authority:
            url = [authority]
        else:
            url = [self.environ['wsgi.url_scheme'], '://']
            url.append(self._get_authority())
        script = urllib.quote(self.environ.get('SCRIPT_NAME', ''))
        url.append(script)
        # we always add the slash, that's our root URL
        if not script or script[-1] != '/':
            url.append('/')
        return URI.from_octets(string.join(url, ''))

    def get_url(self, authority=None):
        """Returns the URL used in the request

        authority
            See :meth:`get_app_root`

        The result is a :class:`pyslet.rfc2396.URI` instance, It is
        calculated from the environment using the algorithm described in
        URL Reconstruction section of the WSGI specification except
        that it ignores the Host header for security reasons.

        Unlike the result of :meth:`get_app_root` it *doesn't*
        necessarily end with a trailing slash.  So if you have a script
        bound to /script/myscript.py running over http on
        www.example.com then you may get::

            http://www.example.com/script/myscript.py

        A good pattern to adopt when faced with a missing trailing slash
        on a URL that is intended to behave as a 'directory' is to add
        the slash to the URL and use xml:base (for XML responses) or
        HTML's <base> tag to set the root for relative links.  The
        alternative is to issue an explicit redirect but this requires
        another request from the client.

        This causes particular pain in OData services which frequently
        respond on the service script's URL without a slash but generate
        incorrect relative links to the contained feeds as a result."""
        if authority:
            url = [authority]
        else:
            url = [self.environ['wsgi.url_scheme'], '://']
            url.append(self._get_authority())
        url.append(urllib.quote(self.environ.get('SCRIPT_NAME', '')))
        url.append(urllib.quote(self.environ.get('PATH_INFO', '')))
        query = self.environ.get('QUERY_STRING', '')
        if query:
            url += ['?', query]
        return URI.from_octets(string.join(url, ''))

    def _get_authority(self):
        sflag = (self.environ['wsgi.url_scheme'] == 'https')
        authority = self.environ['SERVER_NAME']
        port = self.environ['SERVER_PORT']
        if sflag:
            if port != '443':
                return "%s:%s" % (authority, port)
        elif port != '80':
            return "%s:%s" % (authority, port)
        return authority

    def get_query(self):
        """Returns a dictionary of query parameters

        The dictionary maps parameter names onto strings.  In cases
        where multiple values have been supplied the values are comma
        separated, so a URL ending in ?option=Apple&option=Pear would
        result in the dictionary::

            {'option': 'Apple,Pear'}

        This method only computes the dictionary once, future calls
        return the same dictionary!

        Note that the dictionary does not contain any cookie values or
        form parameters."""
        if self._query is None:
            self._query = urlparse.parse_qs(
                self.environ.get('QUERY_STRING', ''))
            for n, v in self._query.items():
                self._query[n] = string.join(v, ',')
        return self._query

    def get_content(self):
        """Returns the content of the request as a string

        The content is read from the input, up to CONTENT_LENGTH bytes,
        and is returned as a string.  If the content exceeds
        :attr:`MAX_CONTENT` (default: 64K) then BadRequest is raised.

        This method can be called multiple times, the content is only
        actually read from the input the first time.  Subsequent calls
        return the same string.

        This call cannot be called on the same context as
        :meth:`get_form`, whichever is called first takes precedence.
        Calls to get_content after get_form return None."""
        if self._form is None and self._content is None:
            length = self.environ.get('CONTENT_LENGTH', '')
            if length.isdigit():
                length = int(length)
            else:
                length = 0
            if length <= self.MAX_CONTENT:
                input = self.environ['wsgi.input']
                f = StringIO.StringIO()
                while length:
                    part = input.read(length)
                    if not part:
                        break
                    f.write(part)
                    length -= len(part)
                self._content = f.getvalue()
            else:
                raise BadRequest("Too much data")
        return self._content

    def get_form(self):
        """Returns a FieldStorage object parsed from the content.

        The query string is excluded before the form is parsed as this
        only covers parameters submitted in the content of the request.
        To search the query string you will need to examine the
        dictionary returned by :meth:`get_query` too.

        This method can be called multiple times, the form is only
        actually read from the input the first time.  Subsequent calls
        return the same FieldStorage object.

        This call cannot be called on the same context as
        :meth:`get_content`, whichever is called first takes
        precedence.  Calls to get_form after get_content return None.

        Warning: get_form will only parse the form from the content if
        the request method was POST!"""
        if self._form is None and self._content is None:
            post_environ = self.environ.copy()
            post_environ['QUERY_STRING'] = ''
            self._form = cgi.FieldStorage(
                fp=post_environ['wsgi.input'], environ=post_environ,
                keep_blank_values=True)
        return self._form

    def get_form_string(self, name, max_length=0x10000):
        """Returns the value of a string parameter from the form.

        name
            The name of the parameter

        max_length (optional, defaults to 64KB)
            Due to an issue in the implementation of FieldStorage it
            isn't actually possible to definitively tell the difference
            between a file upload and an ordinary input field.  HTML5
            clarifies the situation to say that ordinary fields don't
            have a content type but FieldStorage assumes 'text/plain' in
            this case and sets the file and type attribute of the field
            anyway.

            To prevent obtuse clients sending large files disguised as
            ordinary form fields, tricking your application into loading
            them into memory, this method checks the size of any file
            attribute (if present) against max_length before returning
            the field's value.

        If the parameter is missing from the form then an empty string
        is returned."""
        form = self.get_form()
        if name in form:
            result = form[name]
            if isinstance(result, list):
                return string.join(map(lambda x: x.value, result), ',')
            else:
                if result.file:
                    # could be an ordinary field in multipart/form-data
                    # this is a bit rubbish
                    fpos = result.file.tell()
                    result.file.seek(0, io.SEEK_END)
                    fsize = result.file.tell()
                    result.file.seek(fpos)
                    if fsize > max_length:
                        raise BadRequest
                return result.value
        return ''

    def get_form_long(self, name):
        """Returns the value of a (long) integer parameter from the form.

        name
            The name of the parameter

        If the parameter is missing from the form then None is returned,
        if the parameter is present but is not a valid integer then
        :class:`BadRequest` is raised."""
        value = self.get_form_string(name, 256)
        try:
            return long(value)
        except ValueError as err:
            logging.debug("get_form_long: %s", str(err))
            raise BadRequest

    def get_cookies(self):
        """Returns a dictionary of cookies from the request

        If no cookies were passed an empty dictionary is returned.

        For details of how multi-valued cookies are handled see:
        :meth:`pyslet.http.cookie.CookieParser.request_cookie_string`."""
        if self._cookies is None:
            cookie_values = self.environ.get('HTTP_COOKIE', None)
            if cookie_values is not None:
                p = cookie.CookieParser(cookie_values)
                self._cookies = p.require_cookie_string()
                for name in self._cookies:
                    value = self._cookies[name]
                    if isinstance(value, set):
                        # join the items into a single string
                        value = list(value)
                        value.sort()
                        self._cookies[name] = string.join(value, ',')
            else:
                self._cookies = {}
        return self._cookies


class DispatchNode(object):

    """An opaque class used for dispatching requests."""

    def __init__(self):
        self._handler = None
        self._wildcard = None
        self._nodes = {}


class WSGIApp(DispatchNode):

    """An object to help support WSGI-based applications.

    Instances are designed to be callable by the WSGI middle-ware, on
    creation each instance is assigned a random identifier which is used
    to provide comparison and hash implementations.  We go to this
    trouble so that derived classes can use techniques like the
    functools lru_cache decorator in future versions."""

    #: the context class to use for this application, must be (derived
    #: from) :class:`WSGIContext`
    ContextClass = WSGIContext

    #: The path to the directory for :attr:`static_files`.  Defaults to
    #: None.
    static_files = None

    private_files = None
    """Private data diretory

    The directory used for storing private data.  The directory is
    partitioned into sub-directories based on the lower-cased class name
    of the object that owns the data.  For example, if private_file is
    set to '/var/www/data' and you derive a class called 'MyApp' from
    WSGIApp you can assume that it is safe to store and retrieve private
    data files from '/var/www/data/myapp'.

    private_files defaults to None for safety.  The current WSGIApp
    implementation does not depend on any private data."""

    settings_file = None
    """The path to the settings file.  Defaults to None.

    The format of the settings file is a json dictionary.  The
    dictionary's keys are class names that define a scope for
    class-specific settings. The key 'WSGIApp' is reserved for settings
    defined by this class.  The defined settings are:

    level (None)
        If specified, used to set the root logging level, a value
        between 0 (NOTSET) and 50 (CRITICAL).  For more information see
        python's logging module.

    authority ("http://localhost")
        The canonical URL scheme, host (and port if required) for the
        application.  This value is passed to
        :meth:`WSGIContext.get_url` and similar methods and is used in
        preference to the SERVER_NAME and SEVER_PORT to construct
        absolute URLs returned or recorded by the application.  Note
        that the Host header is always ignored to prevent related
        `security attacks`__.

        ..  __:
            http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html

    port (8080)
        The port number used by :meth:`run_server`

    interactive (False)
        Sets the behaviour of :meth:`run_server`, if specified the main
        thread prompts the user with a command line interface allowing
        you to interact with the running server.  When False, run_server
        will run forever and can only be killed by an application
        request that sets :attr:`stop` to True or by an external signal
        that kills the process.

    static (None)
        A URL to the static files (not a local file path).  This will
        normally be an absolute path or a relative path.  Relative paths
        are relative to the settings file in which the setting is
        defined. As URL syntax is used you must use the '/' as a path
        separator and add proper URL-escaping.  On Windows, UNC paths
        can be specified by putting the host name in the authority
        section of the URL.

    private (None)
        A URL to the private files.  Interpreted as per the 'static'
        setting above."""

    #: the class settings loaded from :attr:`settings_file` by
    #: :meth:`setup`
    settings = None

    #: the base URI of this class, set from the path to the settings
    #: file itself.  This is a :class:`pyslet.rfc2396.FileURL` instance.
    base = None

    #: the base URI of this class' private files.  This is set from the
    #: :attr:`private_files` member and is a
    #: :class:`pyslet.rfc2396.FileURL` instance
    private_base = None

    content_type = {
        'ico': params.MediaType('image', 'vnd.microsoft.icon'),
    }
    """The mime type mapping table.

    This table is used before falling back on Python's built-in
    guess_type function from the mimetypes module.  Add your own custom
    mappings here.

    It maps file extension (without the dot) on to
    :class:`~pyslet.http.params.MediaType` instances."""

    #: the maximum chunk size to read into memory when returning a
    #: (static) file.  Defaults to 64K.
    MAX_CHUNK = 0x10000

    #: the integer millisecond time (since the epoch) corresponding to
    #: 01 January 1970 00:00:00 UTC the JavaScript time origin.
    js_origin = int(
        iso.TimePoint(
            date=iso.Date(century=19, year=70, month=1, day=1),
            time=iso.Time(hour=0, minute=0, second=0, zdirection=0)
        ).get_unixtime() * 1000)

    #: a threading.RLock instance that can be used to lock the class
    #: when dealing with data that might be shared amongst threads.
    clslock = threading.RLock()

    _nextid = 1

    @classmethod
    def main(cls):
        """Runs the application

        Options are parsed from the command line and used to
        :meth:`setup` the class before an instance is created and
        launched with :meth:`run_server`."""
        parser = optparse.OptionParser()
        cls.add_options(parser)
        (options, args) = parser.parse_args()
        cls.setup(options=options, args=args)
        app = cls()
        app.run_server()

    @classmethod
    def add_options(cls, parser):
        """Defines command line options.

        parser
            An OptionParser instance, as defined by Python's built-in
            optparse module.

        The following options are added to *parser* by the base
        implementation:

        -v          Sets the logging level to WARNING, INFO or DEBUG
                    depending on the number of times it is specified.
                    Overrides the 'level' setting in the settings file.

        -p, --port  Overrides the value of the 'port' setting in the
                    settings file.

        -i, --interactive   Overrides the value of the 'interactive'
                            setting in the settings file.

        --static    Overrides the value of :attr:`static_files`.

        --private   Overrides the value of :attr:`private_files`.

        --settings  Sets the path to the :attr:`settings_file`."""
        parser.add_option(
            "-v", action="count", dest="logging",
            default=None, help="increase verbosity of output up to 3x")
        parser.add_option(
            "-p", "--port", action="store", dest="port",
            default=None, help="port on which to listen")
        parser.add_option(
            "-i", "--interactive", dest="interactive", action="store_true",
            default=None,
            help="Enable interactive prompt after starting server")
        parser.add_option(
            "--static", dest="static", action="store", default=None,
            help="Path to the directory of static files")
        parser.add_option(
            "--private", dest="private", action="store", default=None,
            help="Path to the directory for data files")
        parser.add_option(
            "--settings", dest="settings", action="store", default=None,
            help="Path to the settings file")

    @classmethod
    def setup(cls, options=None, args=None, **kwargs):
        """Perform one-time class setup

        options
            An optional object containing the command line options, such
            as an optparse.Values instance created by calling parse_args
            on the OptionParser instance passed to
            :meth:`add_options`.

        args
            An optional list of positional command-line arguments such
            as would be returned from parse_args after the options have
            been removed.

        All arguments are given as keyword arguments to enable use
        of super and diamond inheritance.

        The purpose of this method is to perform any actions required
        to setup the class prior to the creation of any instances.

        The default implementation loads the settings file and sets the
        value of :attr:`settings`.  If no settings file can be found
        then an empty dictionary is created and populated with any
        overrides parsed from options.

        Finally, the root logger is initialised based on the level
        setting.

        Derived classes should always use super to call the base
        implementation before their own setup actions are performed."""
        if options and options.static:
            cls.static_files = os.path.abspath(options.static)
        if options and options.private:
            cls.private_files = os.path.abspath(options.private)
        if options and options.settings:
            cls.settings_file = os.path.abspath(options.settings)
        cls.settings = {}
        if cls.settings_file:
            cls.base = URI.from_path(cls.settings_file)
            if os.path.isfile(cls.settings_file):
                with open(cls.settings_file, 'rb') as f:
                    cls.settings = json.load(f)
        settings = cls.settings.setdefault('WSGIApp', {})
        if options and options.logging is not None:
            settings['level'] = (
                logging.ERROR, logging.WARNING, logging.INFO,
                logging.DEBUG)[min(options.logging, 3)]
        level = settings.setdefault('level', None)
        if level is not None:
            logging.basicConfig(level=settings['level'])
        settings.setdefault('authority', "http://localhost:8080")
        if options and options.port is not None:
            settings['port'] = int(options.port)
        else:
            settings.setdefault('port', 8080)
        if options and options.interactive is not None:
            settings['interactive'] = options.interactive
        else:
            settings.setdefault('interactive', False)
        url = settings.setdefault('static', None)
        if cls.static_files is None and url:
            cls.static_files = cls.resolve_setup_path(url)
        url = settings.setdefault('private', None)
        if cls.private_files is None and url:
            cls.private_files = cls.resolve_setup_path(url)
        if cls.private_files:
            cls.private_base = URI.from_path(
                os.path.join(cls.private_files, ''))
        # this logging line forces the root logger to be initialised
        # with the default level as a catch all
        logging.debug("Logging configured for %s", cls.__name__)

    @classmethod
    def resolve_setup_path(cls, path, private=False):
        """Resolves a settings-relative path

        path
            The relative URI of a file or directory.

        private (False)
            Resolve relative to the private files directory

        Returns path as a system file path after resolving relative to
        the settings file location or to the private files location as
        indicated by the private flag.  If the required location is not
        set then path must be an absolute file URL (starting with, e.g.,
        file:///). On Windows systems the authority component of the URL
        may be used to specify the host name for a UNC path."""
        url = URI.from_octets(path)
        if private and cls.private_base:
            url = url.resolve(cls.private_base)
        elif not private and cls.base:
            url = url.resolve(cls.base)
        if not url.is_absolute() and not isinstance(url, FileURL):
            raise RuntimeError("Can't resolve setup path %s" % path)
        return url.get_pathname()

    def __init__(self):
        # keyword arguments end here, no more super after WSGIApp
        DispatchNode.__init__(self)
        #: flag: set to True to request :meth:`run_server` to exit
        self.stop = False
        with self.clslock:
            #: a unique ID for this instance
            self.id = WSGIApp._nextid
            WSGIApp._nextid += 1
        self.init_dispatcher()

    def __cmp__(self, other):
        if not isinstance(other, WSGIApp):
            raise TypeError
        # compare first by class name, then by instance ID
        result = cmp(self.__class__.__name__, other.__class__.__name__)
        if not result:
            result = cmp(self.id, other.id)
        return result

    def __hash__(self):
        return self.id

    def init_dispatcher(self):
        """Used to initialise the dispatcher.

        By default all requested paths generate a 404 error.  You
        register pages during :meth:`init_dispatcher` by calling
        :meth:`set_method`.  Derived classes should use super
        to pass the call to their parents."""
        pass

    def set_method(self, path, method):
        """Registers a bound method in the dispatcher

        path
            A path or path pattern

        method
            A bound method or callable with the basic signature::

                result = method(context)

        A star in the path is treated as a wildcard and matches a
        complete path segment.  A star at the end of the path (which
        must be after a '/') matches any sequence of path segments.  The
        matching sequence may be empty, in other words, "/images/*"
        matches "/images/".  In keeping with common practice a missing
        trailing slash is ignored when dispatching so "/images" will
        also be routed to a method registered with "/images/*" though if
        a separate registration is made for "/images" it will be matched
        in preference.

        Named matches always take precedence over wildcards so you can
        register "/images/*" and "/images/counter.png" and the latter
        path will be routed to its preferred handler.  Similarly you can
        register "/*/background.png" and "/home/background.png" but
        remember the '*' only matches a single path component!  There is
        no way to match background.png in any directory."""
        path = path.split('/')
        if not path:
            path = ['']
        node = self
        pleft = len(path)
        for p in path:
            pleft -= 1
            old_node = node
            if p == '*' and not pleft:
                # set a special flag, e.g., if /a/* is declared and we
                # have an unmatched /a we'll call that handler anyway
                old_node._wildcard = method
            node = old_node._nodes.get(p, None)
            if not node:
                node = DispatchNode()
                old_node._nodes[p] = node
        node._handler = method

    def call_wrapper(self, environ, start_response):
        """Alternative entry point for debugging

        Although instances are callable you may use this method instead
        as your application's entry point when debugging.

        This method will log the environ variables, the headers output
        by the application and all the data (in quoted-printable form)
        returned at DEBUG level.

        It also catches a common error, that of returning something
        other than a string for a header value or in the generated
        output.  These are logged at ERROR level and converted to
        strings before being passed to the calling framework."""
        # make a closure
        def wrap_response(status, response_headers, exc_info=None):
            if not isinstance(status, str):
                logger.error("Value for status line: %s", repr(status))
                status = str(status)
            logger.debug("*** START RESPONSE ***")
            logger.debug(status)
            new_headers = []
            for h, v in response_headers:
                if not isinstance(h, str):
                    logger.error("Header name: %s", repr(h))
                    h = str(h)
                if not isinstance(v, str):
                    logger.error("Header value: %s: %s", h, repr(v))
                    v = str(v)
                logger.debug("%s: %s", h, v)
                new_headers.append((h, v))
            return start_response(status, new_headers, exc_info)
        logger.debug("*** START REQUEST ***")
        for key in environ:
            logger.debug("%s: %s", key, str(environ[key]))
        blank = False
        for data in self(environ, wrap_response):
            if not blank:
                logger.debug("")
                blank = True
            if not isinstance(data, str):
                logger.error("Bad type for response data in %s\n%s",
                             str(environ['PATH_INFO']), repr(data))
                if isinstance(data, unicode):
                    data = data.encode('utf-8')
                else:
                    data = str(data)
            else:
                logger.debug(data.encode('quoted-printable'))
            yield data

    def __call__(self, environ, start_response):
        context = self.ContextClass(environ, start_response)
        try:
            path = context.environ['PATH_INFO'].split('/')
            if not path:
                # empty path
                path = ['']
            i = 0
            node = self
            wildcard = None
            stack = []
            while i < len(path):
                p = path[i]
                old_node = node
                wild_node = old_node._nodes.get('*', None)
                node = old_node._nodes.get(p, None)
                if node:
                    if wild_node:
                        # this is a fall-back node, push it
                        stack.append((i, wild_node, wildcard))
                elif wild_node:
                    node = wild_node
                elif wildcard:
                    # if there is an active wildcard, use it
                    break
                elif stack:
                    i, node, wildcard = stack.pop()
                else:
                    break
                if node._wildcard is not None:
                    wildcard = node._wildcard
                i += 1
            if node and node._handler is not None:
                return node._handler(context)
            if wildcard:
                return wildcard(context)
            # we didn't find a handler
            return self.error_page(context, 404)
        except MethodNotAllowed:
            return self.error_page(context, 405)
        except PageNotFound:
            return self.error_page(context, 404)
        except PageNotAuthorized:
            return self.error_page(context, 403)
        except BadRequest:
            return self.error_page(context, 400)
        except Exception as e:
            logger.exception(context.environ['PATH_INFO'])
            return self.internal_error(context, e)

    def static_page(self, context):
        """Returns a static page

        This method can be bound to any path using :meth:`set_method`
        and it will look in the :attr:`static_files` directory for that
        file.  For example, if static_files is "/var/www/html" and the
        PATH_INFO variable in the request is "/images/logo.png" then the
        path "/var/www/html/images/logo.png" will be returned.

        There are significant restrictions on the names of the path
        components.  Each component *must* match a basic label syntax
        (equivalent to the syntax of domain labels in host names) except
        the last component which must have a single '.' separating two
        valid labels.  This conservative syntax is designed to be safe
        for passing to file handling functions."""
        path = context.environ['PATH_INFO'].split('/')
        target_path = self.static_files
        if target_path is None:
            raise PageNotFound
        ext = ''
        pleft = len(path)
        for p in path:
            pleft -= 1
            if pleft:
                # ignore empty components
                if not p:
                    continue
                # this path component must be a directory we re-use the
                # ldb-label test from the cookie module to ensure we
                # have a very limited syntax.  Apologies if you wanted
                # fancy URLs.
                if not cookie.is_ldh_label(p):
                    raise PageNotFound
                target_path = os.path.join(target_path, p)
                if not os.path.isdir(target_path):
                    raise PageNotFound
            elif not p:
                # this is the directory form, e.g., /app/docs/ but we
                # don't support indexing, we're not Apache
                raise PageNotFound
            else:
                # last component must be a filename.ext form
                splitp = p.split('.')
                if (len(splitp) != 2 or
                        not cookie.is_ldh_label(splitp[0]) or
                        not cookie.is_ldh_label(splitp[1])):
                    raise PageNotFound
                filename = p
                ext = splitp[1]
                target_path = os.path.join(target_path, p)
        if not os.path.isfile(target_path):
            raise PageNotFound
        # Now the MIME mapping
        ctype = self.content_type.get(ext, None)
        if ctype is None:
            ctype, encoding = mimetypes.guess_type(filename)
            if ctype is not None:
                ctype = params.MediaType.from_str(ctype)
            if encoding is not None:
                context.add_header("Content-Encoding", encoding)
        if ctype is None:
            ctype = params.APPLICATION_OCTETSTREAM
        context.set_status(200)
        context.add_header("Content-Type", str(ctype))
        return self.file_response(context, target_path)

    def file_response(self, context, target_path):
        """Returns a file from the file system

        target_path
            The system file path of the file to be returned.

        The Content-Length header is set from the file size, the
        Last-Modified date is set from the file's st_mtime and the
        file's data is returned in chunks of :attr:`MAX_CHUNK` in the
        response.

        The status is *not* set and must have been set before calling
        this method."""
        finfo = os.stat(target_path)
        context.add_header("Content-Length", str(finfo.st_size))
        context.add_header("Last-Modified",
                           str(params.FullDate.from_unix_time(finfo.st_mtime)))
        context.start_response()
        bleft = finfo.st_size
        with open(target_path, 'rb') as f:
            while bleft:
                chunk_size = min(bleft, self.MAX_CHUNK)
                chunk = f.read(chunk_size)
                if not chunk:
                    # unexpected EOF while reading
                    raise RuntimeError("Unexpected EOF")
                bleft -= len(chunk)
                yield chunk

    def html_response(self, context, data):
        """Returns an HTML page

        data
            A string containing the HTML page data.  This may be a
            unicode or binary string.

        The Content-Type header is set to text/html (with an explicit
        charset if data is a unicode string).  The status is *not* set and
        must have been set before calling this method."""
        if isinstance(data, unicode):
            data = data.encode('utf-8')
            context.add_header("Content-Type", "text/html; charset=utf-8")
        else:
            context.add_header("Content-Type", "text/html")
        # catch the odd case where data is a subclass of str - still ok
        # but the default WSGI server uses this stronger test!
        if type(data) is not str:
            data = str(data)
        context.add_header("Content-Length", str(len(data)))
        context.start_response()
        return [data]

    def json_response(self, context, data):
        """Returns a JSON response

        data
            A string containing the JSON data.  This may be a unicode or
            binary string (encoded with utf-8).

        The Content-Type is set to "application/json".  The status is
        *not* set and must have been set before calling this method."""
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        if type(data) is not str:
            data = str(data)
        context.add_header("Content-Type", "application/json")
        context.add_header("Content-Length", str(len(data)))
        context.start_response()
        return [data]

    def text_response(self, context, data):
        """Returns a plain text response

        data
            A string containing the text data.  This may be a unicode or
            binary string (encoded with US-ASCII).

        The Content-Type is set to "text/plain" (with an explicit
        charset if a unicode string is passed).  The status is *not* set
        and must have been set before calling this method.

        Warning: do not encode unicode strings before passing them to
        this method as data, if you do you risk problems with non-ASCII
        characters as the default charset for text/plain is US-ASCII and
        not UTF-8 or ISO8859-1 (latin-1)."""
        if isinstance(data, unicode):
            data = data.encode('utf-8')
            context.add_header("Content-Type", "text/plain; charset=utf-8")
        else:
            context.add_header("Content-Type", "text/plain")
        if type(data) is not str:
            data = str(data)
        context.add_header("Content-Length", str(len(data)))
        context.start_response()
        return [data]

    def redirect_page(self, context, location, code=303):
        """Returns a redirect response

        location
            A :class:`~pyslet.rfc2396.URI` instance or a string of
            octets.

        code (303)
            The redirect status code.  As a reminder the typical codes
            are 301 for a permanent redirect, a 302 for a temporary
            redirect and a 303 for a temporary redirect following a POST
            request.  This latter code is useful for implementing the
            widely adopted pattern of always redirecting the user after
            a successful POST request to prevent browsers prompting for
            re-submission and is therefore the default.

        This method takes care of setting the status, the Location
        header and generating a simple HTML redirection page response
        containing a clickable link to *location*."""
        data = """<html>
<head><title>Redirect</title></head>
<body>
    <p>Please <a href=%s>click here</a> if not redirected automatically</p>
</body></html>""" % xml.EscapeCharData7(str(location), True)
        context.add_header("Location", str(location))
        context.add_header("Content-Type", "text/html")
        context.add_header("Content-Length", str(len(data)))
        context.set_status(code)
        context.start_response()
        return [str(data)]

    def error_page(self, context, code=500, msg=None):
        """Generates an error response

        code (500)
            The status code to send.

        msg (None)
            An optional plain-text error message.  If not given then the
            status line is echoed in the body of the response."""
        context.set_status(code)
        if msg is None:
            msg = "%i %s" % (code, context.status_message)
            context.add_header("Content-Type", "text/plain")
        elif isinstance(msg, unicode):
            msg = msg.encode('utf-8')
            context.add_header("Content-Type", "text/plain; charset=utf-8")
        else:
            context.add_header("Content-Type", "text/plain")
        context.add_header("Content-Length", str(len(msg)))
        context.start_response()
        return [str(msg)]

    def internal_error(self, context, err):
        context.set_status(500)
        data = "%i %s\r\n%s" % (context.status, context.status_message,
                                str(err))
        context.add_header("Content-Type", "text/plain")
        context.add_header("Content-Length", str(len(data)))
        context.start_response()
        return [str(data)]

    def _run_server_thread(self):
        """Starts the web server running"""
        port = self.settings['WSGIApp']['port']
        server = make_server('', port, self.call_wrapper)
        logger.info("HTTP server on port %i running", port)
        # Respond to requests until process is killed
        while not self.stop:
            server.handle_request()

    def run_server(self):
        t = threading.Thread(target=self._run_server_thread)
        t.setDaemon(True)
        t.start()
        logger.info("Starting %s server on port %s", self.__class__.__name__,
                    self.settings['WSGIApp']['port'])
        if self.settings['WSGIApp']['interactive']:
            # loop around getting commands
            while not self.stop:
                cmd = raw_input('cmd: ')
                if cmd.lower() == 'stop':
                    self.stop = True
                elif cmd:
                    try:
                        print eval(cmd)
                    except Exception as err:
                        print "Error: %s " % str(err)
                    # print "Unrecognized command: %s" % cmd
            sys.exit()
        else:
            t.join()


class WSGIDataApp(WSGIApp):

    """Extends WSGIApp to include a data store

    The key 'WSGIDataApp' is reserved for settings defined by this
    class in the settings file. The defined settings are:

    container (None)
        The name of the container to use for the data store.  By
        default, the default container is used.  For future
        compatibility you should not depend on using this option.

    metadata (None)
        URI of the metadata file containing the data schema.  The file
        is assumed to be relative to the settings_file.

    source_type ('sqlite')
        The type of data source to create.  The default value
        is sqlite.  A value of 'mysql' select's Pyslet's mysqldbds
        module instead.

    sqlite_path ('database.sqlite3')
        URI of the database file.  The file is assumed to be relative to
        the private_files directory, though an absolute path may be
        given.

    dbhost ('localhost')
        For mysql databases, the hostname to connect to.

    dname (None)
        The name of the database to connect to.

    dbuser (None)
        The user name to connect to the database with.

    dbpassword (None)
        The password to use in conjunction with dbuser

    keynum ('0')
        The identification number of the key to use when storing
        encrypted data in the container.

    secret (None)
        The key corresponding to keynum.  The key is read in plain text
        from the settings file and must be provided in order to use the
        :attr:`app_cipher` for managing encrypted data.  Derived classes
        could use an alternative mechanism for reading the key, for
        example, using the keyring_ python module.

    cipher ('aes')
        The type of cipher to use.  By default :class:`AESAppCipher` is
        used which uses AES_ internally with a 256 bit key created by
        computing the SHA256 digest of the secret string.  The only
        other supported value is 'plaintext' which does not provide any
        encryption but allows the app_cipher object to be used in cases
        where encryption may or may not be used depending on the
        deployment environment.  For example, it is often useful to turn
        off encryption in a development environment!

    when (None)
        An optional value indicating when the specified secret comes
        into operation.  The value should be a fully specified time
        point in ISO format with timezone offset, such as
        '2015-01-01T09:00:00-05:00'.  This value is used when the
        application is being restarted after a key change, for details
        see :meth:`AppCipher.change_key`.

        The use of AES requires the PyCrypto module to be installed.

    ..  _keyring:  https://pypi.python.org/pypi/keyring

    ..  _AES:
            http://en.wikipedia.org/wiki/Advanced_Encryption_Standard"""

    @classmethod
    def add_options(cls, parser):
        """Adds the following options:

        -s, --sqlout        print the suggested SQL database schema and
                            then exit.  The setting of --create is
                            ignored.

        --create_tables     create tables in the database

        -m. --memory        Use an in-memory SQLite database.  Overrides
                            any source_type and encryption setting
                            values .  Implies --create_tables"""
        super(WSGIDataApp, cls).add_options(parser)
        parser.add_option(
            "-s", "--sqlout", dest="sqlout", action="store_true",
            default=False, help="Write out SQL script and quit")
        parser.add_option(
            "--create_tables", dest="create_tables", action="store_true",
            default=False, help="Create tables in the database")
        parser.add_option(
            "-m", "--memory", dest="in_memory", action="store_true",
            default=False, help="Use in-memory sqlite database")

    #: the metadata document for the underlying data service
    metadata = None

    #: the data source object for the underlying data service the type
    #: of this object will vary depending on the source type.  For
    #: SQL-type containers this will be an instance of a class derived
    #: from :class:`~pyslet.odata2.sqlds.SQLEntityContainer`
    data_source = None

    #: the entity container (cf database)
    container = None

    @classmethod
    def setup(cls, options=None, args=None, **kwargs):
        """Adds database initialisation

        Loads the :attr:`metadata` document.  Creates the
        :attr:`data_source` according to the configured :attr:`settings`
        (creating the tables only if requested in the command line
        options).  Finally sets the :attr:`container` to the entity
        container for the application.

        If the -s or --sqlout option is given in options then the data
        source's create table script is output to standard output and
        sys.exit(0) is used to terminate the process."""
        super(WSGIDataApp, cls).setup(options, args, **kwargs)
        settings = cls.settings.setdefault('WSGIDataApp', {})
        metadata_file = settings.setdefault('metadata', None)
        if metadata_file:
            metadata_file = cls.resolve_setup_path(metadata_file)
            # load the metadata document for our data layer
            cls.metadata = edmx.Document()
            with open(metadata_file, 'rb') as f:
                cls.metadata.Read(f)
        else:
            cls.metadata = cls.load_default_metadata()
        container_name = settings.setdefault('container', None)
        if container_name:
            cls.container = cls.metadata.root.DataServices[container_name]
        else:
            cls.container = cls.metadata.root.DataServices.defaultContainer
        if options and options.create_tables:
            create_tables = True
        else:
            create_tables = False
        if options and options.in_memory:
            source_type = "sqlite"
            sqlite_path = ':memory:'
            create_tables = True
        else:
            source_type = settings.setdefault('source_type', 'sqlite')
            if source_type == 'sqlite':
                # do sqlite settings here
                if options and options.sqlout:
                    # use an in-memory database
                    sqlite_path = ':memory:'
                else:
                    sqlite_path = settings.setdefault(
                        'sqlite_path', 'database.sqlite3')
                    sqlite_path = cls.resolve_setup_path(
                        sqlite_path, private=True)
            elif source_type == 'mysql':
                dbhost = settings.setdefault('dbhost', 'localhost')
                dbname = settings.setdefault('dbname', None)
                dbuser = settings.setdefault('dbuser', None)
                dbpassword = settings.setdefault('dbpassword', None)
        if source_type == 'sqlite':
            from pyslet.odata2.sqlds import SQLiteEntityContainer
            cls.data_source = SQLiteEntityContainer(
                file_path=sqlite_path, container=cls.container)
        elif source_type == 'mysql':
            from pyslet.mysqldbds import MySQLEntityContainer
            cls.data_source = MySQLEntityContainer(
                host=dbhost, user=dbuser, passwd=dbpassword, db=dbname,
                container=cls.container)
        else:
            raise ValueError("Unknown data source type: %s" % source_type)
        if isinstance(cls.data_source, SQLEntityContainer):
            if options and options.sqlout:
                out = StringIO.StringIO()
                cls.data_source.create_all_tables(out=out)
                print out.getvalue()
                sys.exit(0)
            elif create_tables:
                cls.data_source.create_all_tables()
        settings.setdefault('keynum', 0)
        if options and options.in_memory:
            settings.setdefault('secret', 'secret')
            settings.setdefault('cipher', 'plaintext')
        else:
            settings.setdefault('secret', None)
            settings.setdefault('cipher', 'aes')
        settings.setdefault('when', None)

    @classmethod
    def load_default_metadata(cls):
        raise RuntimeError("No path to metadata")

    @classmethod
    def new_app_cipher(cls):
        """Creates an :class:`AppCipher` instance

        This method is called automatically on construction, you won't
        normally need to call it yourself but you may do so, for
        example, when writing a script that requires access to data
        encrypted by the application.

        If there is no 'secret' defined then None is returned.

        Reads the values from the settings file and creates an instance
        of the appropriate class based on the cipher setting value.  The
        cipher uses the 'AppKeys' entity set in :attr:`container` to store
        information about expired keys.  The AppKey entities have the
        following three properties:

        KeyNum (integer key)
            The key identification number

        KeyString (string)
            The *encrypted* secret, for example::

                '1:OBimcmOesYOt021NuPXTP01MoBOCSgviOpIL'

            The number before the colon is the key identification number
            of the secret used to encrypt the string (and will always be
            different from the KeyNum field of course).  The data after
            the colon is the base-64 encoded encrypted string.  The same
            format is used for all data enrypted by
            :class:`AppCipher` objects.  In this case the secret was the
            word 'secret' and the algorithm used is AES.

        Expires (DateTime)
            The UTC time at which this secret will expire.  After this
            time a newer key should be used for encrypting data though
            this key may of course still be used for decrypting data."""
        keynum = cls.settings['WSGIDataApp']['keynum']
        secret = cls.settings['WSGIDataApp']['secret']
        cipher = cls.settings['WSGIDataApp']['cipher']
        when = cls.settings['WSGIDataApp']['when']
        if when:
            when = iso.TimePoint.from_str(when)
        if cipher == 'plaintext':
            cipher_class = AppCipher
        elif cipher == 'aes':
            cipher_class = AESAppCipher
        else:
            # danger, raise an error
            raise RuntimeError("Unknown cipher: %s" % cipher)
        if secret:
            return cipher_class(keynum, secret, cls.container['AppKeys'], when)
        else:
            return None

    def __init__(self, **kwargs):
        super(WSGIDataApp, self).__init__(**kwargs)
        #: the application's cipher, a :class:`AppCipher` instance.
        self.app_cipher = self.new_app_cipher()


class PlainTextCipher(object):

    def encrypt(self, data):
        return data

    def decrypt(self, data):
        return data


class AESCipher(object):

    def __init__(self, key):
        self.key = sha256(key).digest()

    def encrypt(self, data):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return iv + cipher.encrypt(data)

    def decrypt(self, data):
        iv = data[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher.decrypt(data[AES.block_size:])


class AppCipher(object):

    """A cipher for encrypting application data

    key_num
        A key number

    key
        A binary string containing the application key.

    key_set
        An entity set used to store previous keys.  The entity set must
        have an integer key property 'KeyNum' and a string field
        'KeyString'.  The string field must be large enough to contain
        encrypted versions of previous keys.

    when (None)
        A fully specified :class:`pyslet.iso8601.TimePoint` at which
        time the key will become active.  If None, the key is active
        straight away.  Otherwise, the key_set is searched for a key
        that is still active and that key is used when encrypting data
        until the when time, at which point the given key takes over.

    The object wraps an underlying cipher.  Strings are encrypted using
    the cipher and then encoded using base64.  The output is then
    prefixed with an ASCII representation of the key number (key_num)
    followed by a ':'.  For example, if key_num is 7 and the cipher
    is plain-text (the default) then encrypt("Hello") results in::

        "7:SGVsbG8="

    When decrypting a string, the key number is parsed and matched
    against the key_num of the key currently in force.  If the string
    was encrypted with a different key then the key_set is used to look
    up that key (which is itself encrypted of course).  The process
    continues until a key encrypted with key_num is found.

    The upshot of this process is that you can change the key associated
    with an application.  See :meth:`change_key` for details."""

    #: the maximum age of a key, which is the number of times the key
    #: can be changed before the original key is considered too old to
    #: be used for decryption.
    MAX_AGE = 100

    def __init__(self, key_num, key, key_set, when=None):
        self.lock = threading.RLock()
        self.key_set = key_set
        self.key_num = key_num
        self.key = key
        self.ciphers = {key_num: self.new_cipher(key)}
        if when:
            # we need to find a key that hasn't expired
            with key_set.OpenCollection() as keys:
                t = edm.EDMValue.NewSimpleValue(edm.SimpleType.DateTime)
                t.set_from_value(time.time())
                filter = odata.CommonExpression.from_str(
                    "Expires gte :t", {'t': t})
                keys.set_filter(filter)
                # Only interested in keys that haven't expired
                old_keys = keys.values()
                if not old_keys:
                    raise RuntimeError("AppCipher: no current key")
                old_key = old_keys[0]
                self.old_num = old_key['KeyNum'].value
                self.old_key = self.decrypt(old_key['KeyString'])
                self.old_expires = when.get_unixtime()
                self.ciphers[self.old_num] = self.new_cipher(self.old_key)
        else:
            self.old_num = None
            self.old_key = None
            self.old_expires = None

    def new_cipher(self, key):
        """Returns a new cipher object with the given key

        The default implementation creates a plain-text 'cipher' and is
        not suitable for secure use."""
        return PlainTextCipher()

    def change_key(self, key_num, key, when):
        """Changes the key of this application.

        key_num
            The number given to the new key, must differ from the last
            :attr:`MAX_AGE` key numbers.

        key
            A binary string containing the new application key.

        when
            A fully specified :class:`pyslet.iso8601.TimePoint` at which
            point the new key will come into effect.

        Many organizations have a policy of changing keys on a routine
        basis, for example, to ensure that people who have had temporary
        access to the key only have temporary access to the data it
        protects.  This method makes it easier to implement such a
        policy for applications that use the AppCipher class.

        The existing key is encrypted with the new key and a record is
        written to the :attr:`key_set` to record the *existing* key
        number, the encrypted key string and the *when* time, which is
        treated as an expiry time in this context.

        This procedure ensures that strings encrypted with an old key
        can always be decrypted because the value of the old key can be
        looked up.  Although it is encrypted, it will be encrypted with
        a new(er) key and the procedure can be repeated as necessary
        until a key encrypted with the newest key is found.

        The key change process then becomes:

        1.  Start a utility process connected to the application's
            entity container using the existing key and then call the
            change_key method.  Pass a value for *when* that will give
            you time to reconfigure all AppCipher clients.  Assuming the
            key change is planned, a time in hours or even days ahead
            can be used.

        2.  Update or reconfigure all existing applications so that they
            will be initialised with the new key and the same value for
            *when* next time they are restarted.

        3.  Restart/refresh all running applications before the change
            over time.  As this does not need to be done simultaneously,
            a load balanced set of application servers can be cycled on
            a schedule to ensure continuous running).

        Following a key change the entity container will still contain
        data encrypted with old keys and the architecture is such that
        compromise of a key is sufficient to read all encrypted data
        with that key and all previous keys.  Therefore, changing the
        key only protects new data.

        In situations where policy dictates a key change it might make
        sense to add a facility to the application for re-encrypting
        data in the data store by going through a
        read-decrypt/encrypt-write cycle with each protected data field.
        Of course, the old key could still be used to decrypt this
        information from archived backups of the data store.
        Alternatively, if the protected data is itself subject to change
        on a routine basis you may simply rely on the natural turnover
        of data in the application.  The strategy you choose will depend
        on your application.

        The :attr:`MAX_AGE` attribute determines the maximum number of
        keys that can be in use in the data set simultaneously.
        Eventually you will have to update encrypted data in the data
        store."""
        with self.lock:
            self.old_num = self.key_num
            self.old_key = self.key
            self.old_expires = when.get_unixtime()
            # we should already have a cipher for this key
            self.key_num = key_num
            self.key = key
            cipher = self.ciphers[key_num] = self.new_cipher(key)
            # we can't use the encrypt method here as we want to force
            # use of the new key
            old_key_encrypted = "%i:%s" % (
                key_num, base64.b64encode(cipher.encrypt(self.old_key)))
        with self.key_set.OpenCollection() as keys:
            e = keys.new_entity()
            e.set_key(self.old_num)
            e['KeyString'].set_from_value(old_key_encrypted)
            e['Expires'].set_from_value(when)
            try:
                keys.insert_entity(e)
            except edm.ConstraintError:
                # Presumably this entity already exists, possible race
                # condition on change_key - load the entity from the old
                # key number to raise KeyError if not
                e = keys[self.old_num]

    def encrypt(self, data):
        """Encrypts data with the current key"""
        with self.lock:
            if self.old_expires:
                if time.time() > self.old_expires:
                    # the old key has finally expired
                    self.old_num = None
                    self.old_key = None
                    self.old_expires = None
                else:
                    # use the old key
                    cipher = self.ciphers[self.old_num]
                    return "%i:%s" % (self.old_num,
                                      base64.b64encode(cipher.encrypt(data)))
            cipher = self.ciphers[self.key_num]
            return "%i:%s" % (self.key_num,
                              base64.b64encode(cipher.encrypt(data)))

    def decrypt(self, data):
        """Decrypts data"""
        key_num, data = self._split_data(data)
        stack = [(key_num, data, None)]
        while stack:
            key_num, data, cipher_num = stack.pop()
            cipher = self.ciphers.get(key_num, None)
            if cipher is None:
                stack.append((key_num, data, cipher_num))
                with self.key_set.OpenCollection() as collection:
                    try:
                        e = collection[key_num]
                        old_key_num, old_key_data = self._split_data(
                            e['KeyString'].value)
                        if len(stack) > self.MAX_AGE:
                            raise KeyError
                        stack.append((old_key_num, old_key_data, key_num))
                    except KeyError:
                        raise RuntimeError("AppCipher.decript: key too old")
            else:
                with self.lock:
                    new_data = cipher.decrypt(data)
                    if cipher_num is not None:
                        self.ciphers[cipher_num] = self.new_cipher(new_data)
                    else:
                        # this is the data we want
                        return new_data

    def _split_data(self, data):
        data = data.split(':')
        if len(data) != 2 or not data[0].isdigit():
            raise ValueError
        key_num = int(data[0])
        try:
            data = base64.b64decode(data[1])
        except TypeError:
            raise ValueError
        return key_num, data


class AESAppCipher(AppCipher):

    """A cipher object that uses AES to encrypt the data

    The Pycrypto module must be installed to use this class.

    The key is hashed using the SHA256 algorithm to obtain a 32 byte
    value for the AES key.  The encrypted strings contain random
    initialisation vectors so repeated calls won't generate the same
    encrypted values.  The CFB mode of operation is used."""

    def new_cipher(self, key):
        return AESCipher(key)


class Session(object):

    """A session object

    A light wrapper for the entity object that is used to persist
    information on the server to make the user's browser session
    stateful.  The session is persisted in a data store using a single
    entity passed on construction which must have the following required
    properties:

    ID: Int32
        A database key for the session, this value is never exposed
        to the client.

    Established: Boolean
        A flag indicating that the session has been established.  A
        session is established when we have successfully read the
        session id from a cookie sent by the browser.  Tracking
        whether or not a session is established helps us defeat
        session fixation attacks.

    UserKey: String
        This is the string used to set the cookie value

    ServerKey: String
        This is a random string that can be used as a server-side secret
        specific to this session.  It is never revealed to the browser

    FirstSeen: DateTime
        The UTC time when the session started.

    LastSeen: DateTime
        The UTC time of the last request issued in this session.

    UserAgent: String
        The user agent string from the browser, if given.

    Derived classes may add optional properties to the basic definition,
    including optional navigation properties, for their own data.

    Changes to the entity are not written back to the database until the
    :meth:`commit` method is called.  This is done automatically by
    :meth:`SessionContext.start_response`."""

    def __init__(self, entity):
        #: the session's entity
        self.entity = entity
        self.touched = False

    def new_from_context(self, context):
        """Initialises the entity's fields from a context

        Generates new keys for UserKey and ServerKey.. The session is
        *not* marked as Established.  The UserAgent is read from the
        context and FirstSeen and LastSeen values are set from the
        current time."""
        user_key = generate_key()
        server_key = generate_key()
        self.entity['UserKey'].set_from_value(user_key)
        self.entity['ServerKey'].set_from_value(server_key)
        self.entity['Established'].set_from_value(False)
        self.entity['FirstSeen'].set_from_value(
            iso.TimePoint.from_now_utc())
        self.entity['LastSeen'].set_from_value(
            self.entity['FirstSeen'].value)
        if 'HTTP_USER_AGENT' in context.environ:
            user_agent = context.environ['HTTP_USER_AGENT']
            if len(user_agent) > 255:
                user_agent = user_agent[0:255]
            self.entity['UserAgent'].set_from_value(user_agent)
        self.touched = True

    def touch(self):
        """Indicates the session entity needs to be updated

        If you change any of the entity field values directly you must
        call this method to ensure the entity is written out correctly
        before the response is returned."""
        self.touched = True

    def sid(self):
        """Returns the UserKey field value"""
        return self.entity['UserKey'].value

    def update_sid(self):
        """Generates a new UserKey value, and returns it."""
        self.entity['UserKey'].set_from_value(generate_key())
        self.touched = True
        return self.entity['UserKey'].value

    def seen(self):
        """Updates the LastSeen field with the current time."""
        self.entity['LastSeen'].set_from_value(iso.TimePoint.from_now_utc())
        self.touched = True

    def expired(self, timeout):
        """Tests for session expiry.

        timeout
            The maximum number of seconds that may have elapsed since
            the session was 'LastSeen'."""
        return (self.entity['LastSeen'].value.with_zone(0).get_unixtime() +
                timeout < time.time())

    def established(self):
        """Return True if this session is Established."""
        if self.entity['Established'].value:
            return True
        else:
            return False

    def establish(self):
        """Marks this session as Established."""
        if not self.entity['Established'].value:
            self.entity['Established'].set_from_value(True)
            self.touched = True

    def match_environ(self, context):
        """Compares the session environment with context

        context
            The current context

        The default implementation compares the user agent string
        to ensure that it is identical.

        The purpose behind this check is to make it that little bit
        harder to carry out session hijacking or fixation.  It doesn't
        add a lot to the security and is here because we might as well
        check the things we can - we do not rely on it to defeat this
        type of attack!"""
        user_agent = context.environ.get('HTTP_USER_AGENT', None)
        if user_agent and len(user_agent) > 255:
            user_agent = user_agent[0:255]
        if self.entity['UserAgent'].value != user_agent:
            return False
        return True

    def absorb(self, new_session):
        """Merge a session into this one.

        new_session
            A session which was started in the same browser session as
            this one but (presumably) in a mode where cookies were
            blocked.

        The purpose of this method is to merge information from the new
        session into this one.  The default implementation simply
        deletes the new session."""
        new_session.entity.Delete()

    def commit(self):
        """Saves any changes back to the data store"""
        if self.touched:
            with self.entity.entity_set.OpenCollection() as collection:
                if self.entity.exists:
                    collection.update_entity(self.entity)
                else:
                    collection.insert_entity(self.entity)
            self.touched = False


def session_decorator(page_method):
    """Decorates a web method with session handling

    page_method
        An unbound method with signature: page_method(obj, context)
        which performs the WSGI protocol and returns the page
        generator.

    Our decorator just calls :meth:`SessionContext.session_wrapper`."""

    def method_call(self, context):
        # There's a smarter way to do this but this is easier to read
        # and understand I think...
        return self.session_wrapper(context, lambda x: page_method(self, x))
        # for more info see:
        # http://stackoverflow.com/questions/1015307/python-bind-an-unbound-method

    return method_call


class SessionContext(WSGIContext):

    """Extends the base class with a session object."""

    def __init__(self, environ, start_response):
        WSGIContext.__init__(self, environ, start_response)
        #: a session object, or None if no session available
        self.session = None

    def start_response(self):
        """Commits changes to the session object.

        If you call start_response with unsaved changes in the session
        the session's :meth:`Session.commit` method is called to save
        them to the data store."""
        if self.session:
            # save any changes to the session to the database
            self.session.commit()
        return super(SessionContext, self).start_response()


class SessionApp(WSGIDataApp):

    """Extends WSGIDataApp to include session handling.

    These sessions require support for cookies. The SessionApp class
    itself uses two cookies purely for session tracking.

    The key 'SessionApp' is reserved for settings defined by this
    class in the settings file. The defined settings are:

    timeout (600)
        The number of seconds after which an inactive session will time
        out and no longer be accessible to the client.

    cookie ('sid')
        The name of the session cookie.

    cookie_test ('ctest')
        The name of the test cookie.  This cookie is set with a longer
        lifetime and acts both as a test of whether cookies are
        supported or not and can double up as an indicator of whether
        user consent has been obtained for any extended use of cookies.
        It defaults to the value '0', indicating that cookies can be
        stored but that no special consent has been obtained.

    cookie_test_age (8640000)
        The age of the test cookie (in seconds).  The default value is
        equivalent to 100 days.  If you use the test cookie to record
        consent to some cookie policy you should ensure that when you
        set the value you use a reasonable lifespan.

    csrftoken ('csrftoken')
        The name of the form field containing the CSRF token

    session_set ('Sessions')
        The name of the entity set to use for persisting session
        entities."""

    _session_timeout = None
    _session_cookie = None
    _test_cookie = None
    _session_set = None

    @classmethod
    def setup(cls, options=None, args=None, **kwargs):
        """Adds database initialisation"""
        super(SessionApp, cls).setup(options, args, **kwargs)
        settings = cls.settings.setdefault('SessionApp', {})
        cls._session_timeout = settings.setdefault('timeout', 600)
        cls._session_cookie = settings.setdefault('cookie', 'sid')
        cls._test_cookie = settings.setdefault('cookie_test', 'ctest')
        cls.csrf_token = settings.setdefault('crsf_token', 'csrftoken')
        session_set = settings.setdefault('session_set', 'Sessions')
        cls._session_set = cls.container[session_set]
        settings.setdefault('cookie_test_age', 8640000)

    @classmethod
    def load_default_metadata(cls):
        mdir = os.path.split(os.path.abspath(__file__))[0]
        metadata_file = os.path.abspath(
            os.path.join(mdir, 'wsgi_metadata.xml'))
        metadata = edmx.Document()
        with open(metadata_file, 'rb') as f:
            metadata.Read(f)
        return metadata

    #: The name of our CSRF token
    csrf_token = None

    #: Extended context class
    ContextClass = SessionContext

    #: The session class to use, must be (derived from) :class:`Session`
    SessionClass = Session

    def init_dispatcher(self):
        """Adds pre-defined pages for this application

        These pages are mapped to /ctest and /wlaunch.  These names are
        not currently configurable.  See :meth:`ctest` and
        :meth:`wlaunch` for more information."""
        WSGIApp.init_dispatcher(self)
        self.set_method('/ctest', self.ctest)
        self.set_method('/wlaunch', self.wlaunch)

    def set_session(self, context):
        """Sets the session object in the context

        The session id is read from the session cookie, if no cookie is
        found a new session is created (and an appropriate cookie is
        added to the response headers)."""
        cookies = context.get_cookies()
        sid = cookies.get(self._session_cookie, '')
        if sid:
            context.session = self._load_session(sid)
        else:
            context.session = None
        if context.session is None:
            with self._session_set.OpenCollection() as collection:
                # generate a new user_key
                entity = collection.new_entity()
                context.session = self.SessionClass(entity)
                context.session.new_from_context(context)
        if context.session.sid() != sid:
            # set the cookie to keep the client up-to-date
            self.set_session_cookie(context)

    def set_session_cookie(self, context):
        """Adds the session ID cookie to the response headers

        The cookie is bound to the path returned by
        :meth:`WSGIContext.get_app_root` and is marked as being
        http_only and is marked secure if we have been accessed through
        an https URL.

        You won't normally have to call this method but you may want to
        override it if your application wishes to override the cookie
        settings."""
        root = context.get_app_root()
        c = cookie.Section4Cookie(
            self._session_cookie, context.session.sid(),
            path=str(root.abs_path), http_only=True,
            secure=root.scheme.lower() == 'https')
        context.add_header('Set-Cookie', str(c))

    def _update_session_key(self, context):
        context.session.update_sid()
        self.set_session_cookie(context)

    def _delete_session(self, sid):
        with self._session_set.OpenCollection() as collection:
            param = edm.EDMValue.NewSimpleValue(edm.SimpleType.String)
            param.set_from_value(sid)
            params = {'sid': param}
            filter = odata.CommonExpression.from_str(
                "UserKey eq :sid", params)
            collection.set_filter(filter)
            slist = collection.values()
            collection.set_filter(None)
            if len(slist):
                for entity in slist:
                    del collection[entity.key()]

    def _load_session(self, sid):
        with self._session_set.OpenCollection() as collection:
            # load the session
            param = edm.EDMValue.NewSimpleValue(edm.SimpleType.String)
            param.set_from_value(sid)
            params = {'user_key': param}
            filter = odata.CommonExpression.from_str(
                "UserKey eq :user_key", params)
            collection.set_filter(filter)
            slist = collection.values()
            collection.set_filter(None)
            if len(slist) > 1:
                # that's an internal error
                raise SessionError(
                    "Duplicate user_key in Sessions: %s" % sid)
            elif len(slist) == 1:
                session = self.SessionClass(slist[0])
                if session.expired(self._session_timeout):
                    self._delete_session(sid)
                    return None
                else:
                    session.seen()
                    return session
            else:
                return None

    def session_page(self, context, page_method, return_path):
        """Returns a session protected page

        context
            The :class:`WSGIContext` object

        page_method
            A function or *bound* method that will handle the page.
            Must have the signature::

                page_method(context)

            and return the generator for the page as per the WSGI
            specification.

        return_path
            A :class:`pyslet.rfc2396.URI` instance pointing at the page
            that will be returned by page_method, used if the session is
            not established yet and a redirect to the test page needs to
            be implemented.

        This method is only called *after* the session has been created,
        in other words, context.session must be a valid session.

        This method either calls the page_method (after ensuring that
        the session is established) or initiates a redirection sequence
        which culminates in a request to return_path."""
        # has the user been here before?
        cookies = context.get_cookies()
        if self._test_cookie not in cookies:
            # no they haven't, set a cookie and redirect
            c = cookie.Section4Cookie(
                self._test_cookie, "0",
                path=str(context.get_app_root().abs_path),
                max_age=self.settings['SessionApp']['cookie_test_age'])
            context.add_header('Set-Cookie', str(c))
            query = urllib.urlencode(
                {'return': str(return_path),
                 'sid': context.session.sid()})
            ctest = URI.from_octets('ctest?' + query).resolve(
                context.get_app_root())
            return self.redirect_page(context, ctest)
        context.session.establish()
        return page_method(context)

    def session_wrapper(self, context, page_method):
        """Called by the session_decorator

        Uses :meth:`set_session` to ensure the context has a session
        object.  If this request is a POST then the form is parsed and
        the CSRF token checked for validity."""
        if context.session is None:
            csrf_match = context.get_cookies().get(self._session_cookie, '')
            self.set_session(context)
            if context.environ['REQUEST_METHOD'].upper() == 'POST':
                # check the CSRF token
                token = context.get_form_string(self.csrf_token)
                # we accept a token even if the session expired but this
                # form is unlikely to do much with a new session.  The point
                # is we compare to the cookie received and not the actual
                # session key as this may have changed
                if not token or token != csrf_match:
                    logger.warn("%s\nSecurity threat intercepted; "
                                "POST token mismatch, possible CSRF attack\n"
                                "cookie=%s; token=%s",
                                context.environ.get('PATH_INFO', ''),
                                csrf_match, token)
                    return self.error_page(context, 403)
        return self.session_page(context, page_method, context.get_url())

    def ctest_page(self, context, target_url, return_url, sid):
        """Returns the cookie test page

        Called when cookies are blocked (perhaps in a frame).

        context
            The request context

        target_url
            A string containing the base link to the wlaunch page.  This
            page can opened in a new window (which may get around the
            cookie restrictions).  You must pass the return_url and the
            sid values as the 'return' and 'sid' query parameters
            respectively.

        return_url
            A string containing the URL the user originally requested,
            and the location they should be returned to when the session
            is established.

        sid
            The session id.

        You may want to override this implementation to provide a more
        sophisticated page.  The default simply constructs the URL to
        the wlaunch page and presents it as a simple hypertext link
        that will open in a new window.

        A more sophisticated application might include a JavaScript to
        follow the link automatically if it detects that the page is
        being displayed in a frame."""
        query = urllib.urlencode({'return': return_url, 'sid': sid})
        target_url = str(target_url) + '?' + query
        data = """<html>
    <head><title>Cookie Test Page</title></head>
    <body>
    <p>Cookie test failed: try opening in a <a href=%s
    target="_blank" id="wlaunch">new window</a></p></body>
</html>""" % xml.EscapeCharData7(str(target_url), True)
        context.set_status(200)
        return self.html_response(context, data)

    def cfail_page(self, context):
        """Called when cookies are blocked completely.

        The default simply returns a plain text message stating that
        cookies are blocked.  You may want to include a page here with
        information about how to enable cookies, a link to the privacy
        policy for your application to help people make an informed
        decision to turn on cookies, etc."""
        context.set_status(200)
        data = "Page load failed: blocked cookies"
        context.add_header("Content-Type", "text/plain")
        context.add_header("Content-Length", str(len(data)))
        context.start_response()
        return [str(data)]

    def ctest(self, context):
        """The cookie test handler

        This page takes three query parameters:

        return
            The return URL the user originally requested

        sid
            The session ID that should be received in a cookie

        framed (optional)
            An optional parameter, if present and equal to '1' it means
            we've already attempted to load the page in a new window so
            if we still can't read cookies we'll return the
            :meth:`cfail_page`.

        If cookies cannot be read back from the context this page will
        call the :meth:`ctest_page` to provide an opportunity to open
        the application in a new window (or :meth:`cfail_page` if this
        possibility has already been exhausted.

        If cookies are successfully read, they are compared with the
        expected values (from the query) and the user is returned to the
        return URL with an automatic redirect.  The return URL must be
        within the same application (to prevent 'open redirect' issues)
        and, to be extra safe, we change the user-visible session ID as
        we've exposed the previous value in the URL which makes it more
        liable to snooping."""
        cookies = context.get_cookies()
        logger.debug("cookies: %s", repr(cookies))
        query = context.get_query()
        logger.debug("query: %s", repr(query))
        if 'return' not in query or 'sid' not in query:
            # missing required parameters
            return self.error_page(context, 400)
        if self._test_cookie not in cookies:
            # cookies are blocked
            if query.get('framed', '0') == '1':
                # we've been through the wlaunch sequence already
                # just fail
                return self.cfail_page(context)
            wlaunch = URI.from_octets('wlaunch').resolve(
                context.get_app_root())
            return self.ctest_page(
                context, str(wlaunch), query['return'], query['sid'])
        sid = query['sid']
        return_path = query['return']
        user_key = cookies.get(self._session_cookie, 'MISSING')
        if user_key != sid:
            # we got a cookie, but not the one we expected.  Possible
            # foul play so remove both sessions and die
            if user_key:
                self._delete_session(user_key)
            if sid:
                self._delete_session(sid)
            # go to an error page
            logger.warn("%s\nSecurity threat intercepted; "
                        "session mismatch, possible fixation attack\n"
                        "cookie=%s; qparam=%s",
                        context.environ.get('PATH_INFO', ''),
                        user_key, sid)
            return self.error_page(context, 400)
        if not self.check_redirect(context, return_path):
            return self.error_page(context, 400)
        # we have matching session ids and the redirect checks out
        self.set_session(context)
        if context.session.sid() == sid:
            # but we've exposed the user_key in the URL which is bad.
            # Let's rewrite that now for safety (without changing
            # the actual session).
            self._update_session_key(context)
        return self.redirect_page(context, return_path)

    def wlaunch(self, context):
        """Handles redirection to a new window

        The redirection may be manual (by the user clicking a link) or
        it may have been automated using JavaScript - though this latter
        technique is liable to fall foul of pop-up blockers so should not
        be relied upon as the only method.

        The query parameters must contain:

        return
            The return URL the user originally requested

        sid
            The session ID that should be received in a cookie

        Typically, this page initiates the redirect sequence again, but
        this time setting the framed query parameter to prevent infinite
        redirection loops."""
        context.get_app_root()
        cookies = context.get_cookies()
        logger.debug("cookies: %s", repr(cookies))
        query = context.get_query()
        if 'return' not in query or 'sid' not in query:
            # missing required parameters
            return self.error_page(context, 400)
        logger.debug("query: %s", repr(query))
        # load the session from the query initially
        sid = query['sid']
        qsession = self._load_session(sid)
        if (qsession is not None and
                (qsession.established() or
                 not qsession.match_environ(context))):
            # we're still trying to establish a session here so this
            # is a surprising result.  Perhaps an attacker has
            # injected their own established session ID here?
            self._delete_session(sid)
            logger.warn("Security threat intercepted in wlaunch; "
                        "unexpected session injected in query, "
                        "possible fixation attack\n"
                        "session=%s", sid)
            return self.error_page(context, 400)
        return_path = query['return']
        if not self.check_redirect(context, return_path):
            return self.error_page(context, 400)
        if self._test_cookie not in cookies:
            # no cookies, either the user has never been here before or
            # cookies are blocked completely, test again
            if qsession is not None:
                # reuse the unestablished session from the query
                # BTW, if you delete the test cookie it could kill your
                # session!
                context.session = qsession
                self.set_session_cookie(context)
            else:
                self.set_session(context)
            c = cookie.Section4Cookie(
                self._test_cookie, "0",
                path=str(context.get_app_root().abs_path),
                max_age=self.settings['SessionApp']['cookie_test_age'])
            context.add_header('Set-Cookie', str(c))
            query = urllib.urlencode(
                {'return': return_path,
                 'sid': context.session.sid(),
                 'framed': '1'})
            ctest = URI.from_octets('ctest?' + query).resolve(
                context.get_app_root())
            return self.redirect_page(context, ctest)
        # so cookies were blocked in the frame but now we're in a new
        # window, suddenly, they appear.  Merge our new session into the
        # old one if the old one was already established
        self.set_session(context)
        if (context.session.established() and qsession is not None):
            # established, matching session.  Merge!
            context.session.absorb(qsession)
        # now we finally have a session
        if context.session.sid() == sid:
            # this session id was exposed in the query, change it
            self._update_session_key(context)
        return self.redirect_page(context, return_path)

    def check_redirect(self, context, target_path):
        """Checks a target path for an open redirect

        target_path
            A string or :class:`~pyslet.rfc2396.URI` instance.

        Returns True if the redirect is *safe*.

        The test ensures that the canonical root of our application
        matches the canonical root of the target.  In other words, it
        must have the same scheme and matching authority (host/port)."""
        if target_path:
            if not isinstance(target_path, URI):
                target_path = URI.from_octets(target_path)
            if (target_path.get_canonical_root() !=
                    context.get_app_root().get_canonical_root()):
                # catch the open redirect here, nice try!
                logger.warn("%s\nSecurity threat intercepted; "
                            "external redirect, possible phishing attack\n"
                            "requested redirect to %s",
                            str(context.get_url()), str(target_path))
                return False
            else:
                return True
        else:
            return False
