import decimal
import operator
import itertools
import bottle
import json
import codecs
import click
import inspect
import socket
import threading
import smtpd
import asyncore
import smtplib
import email
import six

from copy import copy
from collections import deque
from collections import OrderedDict
from werkzeug.serving import make_server
from decimal import Decimal
from helpful import ClassDict, ensure_type, padded_split
from bottle import Bottle, BottleException, HTTPError, HTTPResponse

if six.PY3: # pragma: nocover
    from urllib.parse import urlparse, urljoin
else: # pragma: nocover
    from urlparse import urlparse, urljoin


###########################################################
# Exceptions
###########################################################

class ParseError(BottleException):
    pass


###########################################################
# Media type handling and content negotiation
###########################################################

def cast_media_type(value):
    """
    Convert str/bytes to MediaType, or return if value
    is already an instance of MediaType

    >>> cast_media_type('text/html')
    MediaType('text/html')
    >>> m = MediaType('text/html')
    >>> cast_media_type(m)
    MediaType('text/html')
    """
    ensure_type(value, (str, bytes, MediaType))
    if isinstance(value, (str, bytes)):
        return MediaType(value)
    elif isinstance(value, MediaType):
        return value


class MediaType(dict):
    def __repr__(self):
        return "MediaType('{}')".format(str(self))

    def __str__(self):
        value = "{}/{}".format(self.type, self.subtype)
        if self.parameters:
            value += ";"
            parameters = ';'.join([ 
                '{0!s}={1!s}'.format(*x) for x in self.parameters.items() ])
            value += parameters
        return value

    def __init__(self, value):
        """
        Represents parsed media type

        >>> MediaType('text/html')
        MediaType('text/html')
        >>> MediaType(dict(type='text', subtype='html'))
        MediaType('text/html')
        >>> MediaType(dict(type='text', subtype='html', parameters={'q': 1}))
        MediaType('text/html;q=1')
        """
        super(MediaType, self).__init__()

        if isinstance(value, (str, bytes)):
            value = self._parse(value)
        ensure_type(value, dict)

        def load(type, subtype, parameters=None):
            self['type'] = type
            self['subtype'] = subtype

            if parameters is not None:
                ensure_type(parameters, dict)
                quality = parameters.get('q', None)
                if quality is not None:
                    ensure_type(quality, (str, bytes, int, float, Decimal))
                self['parameters'] = parameters
            else:
                self['parameters'] = {}

        load(**value)

    type = property(lambda self: self['type'])
    subtype = property(lambda self: self['subtype'])
    parameters = property(lambda self: self['parameters'])

    @property
    def suffix(self):
        # Allow suffix via "plus sign", see RFC3023
        subtype, suffix = padded_split(self.subtype, "+", 1)
        return suffix

    @property
    def quality(self):
        q = self.parameters.get('q', 1)
        return Decimal(q)

    @classmethod
    def _parse(self, value):
        """
        Parse media type string into components
        :attr value: Media type value 
                 e.g. text/html;level=2;q=0.4
        :type value: str, bytes
        :returns: MediaType instance
        """
        full_type, parameters = padded_split(value.strip(), ';', 1)
        full_type = '*/*' if full_type == '*' else full_type

        type, subtype = padded_split(full_type, '/', 1)
        if type is None or subtype is None:
            raise ParseError()

        # type can only be a wildcard with subtype
        if type == '*' and subtype != '*':
            raise ParseError()

        def fix_param(x):
            key, value = padded_split(x, '=', 1)
            if not key or not value:
                raise ParseError()
            if str.isdigit(value):
                value = int(value)
            return (key, value)

        parameters = OrderedDict([ fix_param(param) 
            for param in parameters.split(";") ]) if parameters else {}

        kwargs = dict(type=type, subtype=subtype, parameters=parameters)
        return kwargs

    def compare(self, other, ignore_quality=False, ignore_parameters=False):
        """
        Compare media types and determine ordering preference as
        defined by RFC7231.

        :type a: instance of MediaType
        :type b: instance of MediaType
        :type ignore_quality: bool
        :type ignore_parameters: bool
        :returns: int (-1, 0 or 1)
        """
        a = self
        b = other
        ensure_type(a, MediaType)
        ensure_type(b, MediaType)

        if a.type == '*' and b.type != '*':
            return -1
        elif a.type != '*' and b.type == '*':
            return 1
        elif a.subtype == '*' and b.subtype != '*':
            return -1
        elif a.subtype != '*' and b.subtype == '*':
            return 1

        if not ignore_parameters:
            a_len = len([ key for key in a.parameters.keys() if key != 'q' ])
            b_len = len([ key for key in b.parameters.keys() if key != 'q' ])
            if a_len < b_len:
                return -1
            elif a_len > b_len:
                return 1

        if not ignore_quality:
            if a.quality < b.quality:
                return -1
            elif a.quality > b.quality:
                return 1

        return 0

    def is_match(self, other, ignore_quality=False, ignore_parameters=False):
        """
        Compare media types and determine if they are an equal match

        For quality comparison, if A has a quality of 0.7 then B must
        have a quality of 0.7 or above to match.

        :type other: instance of MediaType
        :type ignore_quality: bool
        :type ignore_parameters: bool
        :returns: bool
        """

        a = self
        b = other

        # ensure type matches
        if a.type != '*' and b.type != '*' and a.type != b.type:
           return False

        # ensure subtype matches
        if (a.subtype != '*' and b.subtype != '*' 
            and a.subtype != b.subtype):
            return False

        # as specified by RFC7231, treat quality as a weight
        # q=0 means "not acceptable"
        if (not ignore_quality and 
            (a.quality == 0 or b.quality == 0 or a.quality > b.quality)):
            return False

        # ensure parameters match, where applicable
        if not ignore_parameters:
            a_dict = a.parameters.copy()
            a_dict.pop('q', None)
            b_dict = b.parameters.copy()
            b_dict.pop('q', None)
            if a_dict != b_dict:
                return False

        return True

    def __lt__(self, other):
        return self.compare(other) == -1

    def __gt__(self, other):
        return self.compare(other) == 1

    def __ge__(self, other):
        return self.compare( other) in (0, 1)

    def __le__(self, other):
        return self.compare(other) in (-1, 0)


class MediaTypeList(list):
    def __init__(self, items, *args, **kwargs):
        """
        Represent list of media types

        >>> MediaTypeList('html/text,html/xml')
        [MediaType('html/text'), MediaType('html/xml')]
        >>> MediaTypeList(['html/text', 'html/xml'])
        [MediaType('html/text'), MediaType('html/xml')]
        >>> MediaTypeList([MediaType('html/text'), \
            MediaType('html/xml')])
        [MediaType('html/text'), MediaType('html/xml')]
        """
        if isinstance(items, (str, bytes)):
            items = items.split(",")
        ensure_type(items, (list, set, tuple))
        items = [ cast_media_type(item) for item in items ]
        super(MediaTypeList, self).__init__(items, *args, **kwargs)

    def __setitem__(self, key, value):
        ensure_type(value, MediaType)
        super(MediaTypeList, self).__setitem__(key, value)

    def sorted_by_precedence(self):
        """Sort media types by precedence as defined in RFC2616"""
        # XXX: needs without_quality/without_parameters
        return sorted(self, reverse=True)

    def is_match(self, media_type, ignore_quality=False, ignore_parameters=False):
        """
        Check if media type is supported in this list
        :attr media_type: instance of MediaType

        >>> a = MediaTypeList(['text/html', 'text/xml'])
        >>> a.is_match(MediaType('text/html'))
        True
        >>> a.is_match(MediaType('text/plain'))
        False
        >>> a.is_match('text/html')
        True
        >>> a.is_match('text/plain')
        False
        """
        for a in self.sorted_by_precedence():
            if a.is_match(cast_media_type(media_type), 
                ignore_quality=ignore_quality,
                ignore_parameters=ignore_parameters):
                return True
        return False


    def best_match(self, other, ignore_quality=False, ignore_parameters=False):
        """
        Return media types based on best match as defined in RFC7231
        https://tools.ietf.org/html/rfc7231#section-5.3.1
        https://tools.ietf.org/html/rfc7231#section-5.3.2

        Preference order is based on "closest match", however RFC
        states that parameter matching is optional, and parameter
        matching can be disabled by using `ignore_parameters`.

        It may be desirable to ignore quality weighting, which can
        be done using `ignore_quality`

        Returns list of (media_type, matched_media_type)

        :attr other: instance of MediaTypeList
        """
        ensure_type(other, MediaTypeList)

        kwargs = dict(
            ignore_quality=ignore_quality, 
            ignore_parameters=ignore_parameters)
        matched = []
        remaining = copy(other)
        for a in self.sorted_by_precedence():
            if not len(remaining):
                break
            compared = [ ( b, a.is_match(b, **kwargs)) for b in remaining ]
            matched += [ (media_type, a) for media_type, match 
                in compared if match ]
            remaining = [ media_type for media_type, match 
                in compared if not match ]
        return matched

        
###########################################################
# Content negotiation decorators
###########################################################

class ContentNegotiation(object):
    def __init__(self, accept, content_types):
        """
        :attr accept: list of accepted request media types
        :type accept: list of str
        :attr content_types: List of supported response media types
        :type content_types: list of str
        """
        ensure_type(accept, (list, tuple))
        ensure_type(content_types, (list, tuple))
        self.accept = MediaTypeList(accept)
        self.content_types = MediaTypeList(content_types)

    def __call__(self, callback):
        self.callback = callback
        return self.apply

    def apply(self):
        request = bottle.request
        cneg = ClassDict()
        request.body_parsed = None
        request.content_negotiation = cneg

        cneg.cls = self
        cneg.client_accept = None
        cneg.client_content_type = None
        cneg.parser = None
        cneg.renderer = None
        cneg.body_parsed = None

        # parse client content type
        client_content_type = request.headers.get('Content-Type', None)
        if client_content_type:
            try:
                cneg.client_content_type = MediaType(client_content_type)
            except ParseError as e:
                raise HTTPError("400 Malformed Content-Type header",
                    exception=e)

            if not self.accept.is_match(cneg.client_content_type):
                raise HTTPError(415)

            cneg.parser = self.match_parser(cneg.client_content_type)
            if cneg.parser:
                body_raw = request._get_body_string().decode()
                if body_raw:
                    try:
                        cneg.body_parsed = cneg.parser(body_raw)
                    except (ValueError, TypeError) as e:
                        raise HTTPError("400 Malformed body", exception=e)

        # parse client accept
        client_accept = request.headers.get('Accept', None)
        if client_accept:
            try:
                cneg.client_accept = MediaTypeList(client_accept)
            except ParseError as e:
                raise HTTPError("400 Malformed Accept header", exception=e)

            matches = self.content_types.best_match(cneg.client_accept)
            if not matches:
                raise HTTPError(406)
            cneg.response_content_type = matches[0][0]
            cneg.renderer = self.match_renderer(
                cneg.response_content_type)

        resp = self.callback()
        ensure_type(resp, HTTPResponse)

        resp.headers['Content-Type'] = str(cneg.response_content_type)

        if cneg.renderer:
            resp.body = cneg.renderer(resp.body)

        return resp

    def match_parser(self, media_type):
        """
        Return matching parser method based on media type
        :attr media_type: e.g. text/html
        :type media_type: str or instance of MediaType
        """
        media_type = cast_media_type(media_type)
        full_type = "{type}/{subtype}".format(**media_type)
        if full_type == 'application/json' or media_type.suffix == 'json':
            return self.parse_json
        return None

    def parse_json(self, value):
        return json.loads(value)

    def match_renderer(self, media_type):
        """
        Return matching renderer method based on media type
        :attr media_type: e.g. text/html
        :type media_type: str or instance of MediaType
        """
        media_type = cast_media_type(media_type)
        full_type = "{type}/{subtype}".format(**media_type)
        if full_type == 'application/json' or media_type.suffix == 'json':
            return self.render_json
        return None

    def render_json(self, value):
        return json.dumps(value)


############################################################
# Management CLI
############################################################

@click.group()
def cli(): # pragma: no cover
    pass

@cli.command(name='runserver', help='Start development server')
@click.option('--host', '-h',
    default='127.0.0.1', type=str,
    help='Server hostname/IP')
@click.option('--port', '-p',
    default='8080', type=int,
    help='Server port')
@click.option('--use-reloader',
    type=bool, flag_value=True, default=True,
    help='should the server automatically restart the python '
         'process if modules were changed?')
@click.option('--use-debugger',
    type=bool, flag_value=True, default=True,
    help='should the werkzeug debugging system be used?')
@click.option('--use-evalex',
    type=bool, flag_value=True, default=True,
    help='should the exception evaluation feature be enabled?')
@click.option('--extra-files',
    type=click.Path(), default=None, 
    help='a list of files the reloader should watch additionally '
         'to the modules. For example configuration files.')
@click.option('--static',
    type=click.Path(), default=None, multiple=True,
    help='path to serve static files from via SharedDataMiddleware')
@click.option('--reloader-type',
    type=click.Choice(['stat', 'watchdog']), default=None, 
    help='the type of reloader to use. The default is auto detection.')
@click.option('--reloader-interval',
    type=Decimal, default=0.5, 
    help='the interval for the reloader in seconds')
@click.option('--passthrough-errors',
    type=bool, flag_value=True, default=True,
    help='set this to True to disable the error catching. '
         'This means that the server will die on errors but '
         'it can be useful to hook debuggers in (pdb etc.)')
@click.option('--threaded',
    type=bool, flag_value=True, default=False,
    help='should the process handle each request in a separate thread?')
@click.option('--processes',
    type=int, default=1, 
    help='if greater than 1 then handle each request in a new process up '
         'to this maximum number of concurrent processes.')
def cli_runserver(**kwargs): # pragma: no cover
    kwargs['application'] = None
    return run_simple(**kwargs)


@cli.command(name='ishell', help='Start IPython shell')
def cli_ishell(ctx): # pragma: no cover
    from IPython import start_ipython
    start_ipython(argv=[])


@cli.command(name='shell', help='Start python shell')
def cli_shell(ctx): # pragma: no cover
    code.interact(local=locals())


############################################################
# Live server thread
############################################################

class LiveServerThread(threading.Thread):
    """
    Start WSGI server in a thread, useful for testing

    >>> app = Bottle()
    >>> thread = LiveServerThread(host='127.0.0.1', port='0', app=app)
    >>> thread.start()
    >>> thread.url
    'http://localhost:...'
    >>> thread.stop()
    """

    def __init__(self, *args, **kwargs):
        super(LiveServerThread, self).__init__()
        self.daemon = True
        self.server = make_server(*args, **kwargs)
  
    @property
    def url(self):
        return "http://{}:{}".format(
            self.server.server_name, 
            self.server.server_port)
  
    def run(self):
        """Called inside thread once started"""
        self.server.serve_forever()
  
    def stop(self):
        """Called outside thread to shutdown"""
        self.server.shutdown_signal = True
        if self.server and self.is_alive():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(self.server.socket.getsockname()[:2])
            s.send(b'\r\n')
            s.close()

############################################################
# Dummy SMTP server
############################################################

class DummySMTPServer(smtpd.SMTPServer, object):
    """
    Dummy SMTP server with message inspection capabilities
    """
    max_messages = 1000
    shutdown_signal = None

    def __init__(self, addr=None):
        if addr is None:
            addr = ('127.0.0.1', 0)
        super(DummySMTPServer, self).__init__(addr, None)
        self.messages = deque([], self.max_messages)
        self.hostname = self.socket.getsockname()[0]
        self.port = self.socket.getsockname()[1]

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        e = email.parser.Parser().parsestr(data)
        e.original = ClassDict(peer=peer, mailfrom=mailfrom, 
            rcpttos=rcpttos, data=data)
        e.original.update(kwargs)
        self.messages.appendleft(e)

    # XXX: Annoyingly there's a bug with coverage that prevents us
    # excluding blocks of code for certain Python versions, this
    # needs raising as an issue. For now, we're just excluding both :(
    def handle_accepted(self, sock, addr): # pragma: nocover
        try:
            return super(DummySMTPServer, self).handle_accepted(sock, addr)
        finally:
            if self.shutdown_signal:
                self.close()

    def handle_accept(self): # pragma: nocover
        try:
            return super(DummySMTPServer, self).handle_accept()
        finally:
            if self.shutdown_signal:
                self.close()


class DummySMTPServerThread(threading.Thread):
    """Allow dummy SMTP server to run in the background"""
    def __init__(self, server=None):
        super(DummySMTPServerThread, self).__init__()
        self.daemon = True
        self.server = server if server else DummySMTPServer()
  
    def stop(self):
        self.server.shutdown_signal = True
        if self.server and self.is_alive():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.server.hostname, self.server.port))
            s.send(b'\r\n')
            s.close()

    def run(self):
        asyncore.loop()


############################################################
# Class views
############################################################

class View(object):
    def __init__(self, wildcards):
        self.wildcards = wildcards
        self.request = bottle.request

    def dispatch(self): # pragma: nocover
        raise NotImplementedError("Subclass must implement dispatch")

    @classmethod
    def as_callable(cls, **wildcards):
        return cls(wildcards).dispatch()



############################################################
# Bottle Cap mixin
############################################################

class RequestMixin(object):
    @property
    def base_url(self):
        """
        Return base URL constructed from current request
        """
        url = "{}://{}".format(
            bottle.request.urlparts.scheme,
            bottle.request.urlparts.hostname)
        port = bottle.request.urlparts.port
        if port and port not in (80, 443):
            url += ":{}".format(port)
        return url

    def get_full_url(self, routename, **kwargs):
        """
        Construct full URL using components from current
        bottle request, merged with get_url()

        For example:
        https://example.com/hello?world=1

        XXX: Needs UT
        """
        url = self.app.get_url(routename, **kwargs)
        return urljoin(self.base_url, url)


############################################################
# BottleCap application
############################################################

class BottleCap(bottle.Bottle):
    def __init__(self, *args, **kwargs):
        super(BottleCap, self).__init__(*args, **kwargs)
        self.add_hook('before_request', self.hook_before_request)

    def hook_before_request(self):
        bottle.request.base_url = RequestMixin.base_url
        bottle.request.get_full_url = RequestMixin.get_full_url

    def route(self, path=None, method='GET', callback=None,
        name=None, apply=None, skip=None, **config):
        route = super(BottleCap, self).route

        assert not inspect.isclass(path), \
            "Class views must have route() arguments"
        
        if callable(path):
            path, callback = None, path

        def decorator(callback):
            if inspect.isclass(callback):
                callback = callback.as_callable
            return route(path, method, callback, name, apply, skip, **config)
        return decorator(callback) if callback else decorator





