from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import socket
import ipaddress

from six.moves.urllib.parse import parse_qs, parse_qsl, urlencode

from werkzeug import urls
from werkzeug.datastructures import OrderedMultiDict

import six

from pathlib import Path

if not six.PY2:
    unicode = str  # pragma: no cover


def to_text(x):  # pragma: no cover
    if isinstance(x, six.text_type):
        return x

    elif isinstance(x, six.binary_type):
        return x.decode('utf-8')


class URL(object):
    """This is the main class you want to be using to work with URLs.

    Internally it reuses the URL class from werkzeug. To access the internal
    werkzeug object for each URL, use the _wurl property.

    By default, this class uses the usual parsing where you need to have
    decently formed URLs. But you also have the option of loosely parsing
    URLs the way a browser would, for instance:

    >>> URL('google.com', parse_like_browser=True)
    URL(scheme='http', netloc='google.com', path='', ...

    Whereas the default won't give you what you want:

    >>> URL('google.com')
    URL(scheme='', netloc='', path='google.com', ...

    """

    def __init__(self, url, parse_like_browser=False):
        self._original = url

        self._wurl = urls.url_parse(url)

        if parse_like_browser:
            if not self.scheme and not self.netloc:
                if str(self).startswith('/'):
                    modified = 'file://' + str(self)
                elif str(self).startswith(':/'):
                    modified = str(self).lstrip(':')
                    modified = modified.lstrip('/').lstrip('/')
                    modified = 'http://' + modified
                elif str(self).startswith(':'):
                    modified = str(self)
                else:
                    modified = 'http://' + str(self)
                self._wurl = urls.url_parse(modified)
        self.set_query_omd()

    def set_query_omd(self):
        self._query_omd = OrderedMultiDict(self.qsl)

    def set_query_from_omd(self):
        self.query = urlencode(list(self._query_omd.items(multi=True)))

    def __getattr__(self, name):
        return getattr(self._wurl, name)

    def __str__(self):
        return str(self._wurl)

    def __repr__(self):
        return repr(self._wurl)

    def __eq__(self, other):
        return str(self) == str(other)

    @property
    def scheme(self):
        """Scheme portion of url. Returns '' (empty string)
        if not present.
        """
        return self._wurl.scheme

    @property
    def netloc(self):
        """Network location of URL, eg 'example.com:443'.
        Returns '' (empty string) if not present.
        """
        return self._wurl.netloc

    @property
    def path(self):
        """Path component of url, eg '/images/photo.jpg'.
        """
        return self._wurl.path

    @property
    def query(self):
        """Query portion of URL, eg 'a=b&b=c'.
        Returns '' (empty string) if not present.
        """
        return self._wurl.query

    @property
    def fragment(self):
        """Fragment portion of url. Returns '' (empty string)
        if not present.
        """
        return self._wurl.fragment

    @property
    def qs(self):
        """Query parameters as a dictionary,
        as per parse_qs from the stdlib.
        """
        return parse_qs(self.query)

    @property
    def qsl(self):
        """Query parameters as a list of key-value pairs,
        as per parse_qs from the stdlib.
        """
        return parse_qsl(self.query)

    @property
    def query_omd(self):
        """Get the query portion of the URL as a werkzeug
        OrderedMultiDict"""
        return self._query_omd

    def remove_param(self, name):
        """Removes all params with a certain key from the query
        portion of the URL."""
        self._query_omd.pop(name)
        self.set_query_from_omd()

    def set_param(self, name, value):
        """Sets a particular key to a particular value in the query portion
        of the URL, removing all other values for that key.
        """
        self.query_omd[name] = value
        self.set_query_from_omd()

    def add_param(self, name, value):
        """Adds a value for a particular key to the query part of the URL.
        Unlike ".set_param", doesn't remove other values.
        """

        self.query_omd.add(name, value)
        self.set_query_from_omd()

    @property
    def relative_url(self):
        u2 = URL(str(self))
        u2.scheme = ''
        u2.netloc = ''
        return u2

    @property
    def base_url(self):
        u2 = URL(str(self))
        u2.path = ''
        u2.query = ''
        u2.fragment = ''
        return u2

    @property
    def pathlib_path(self):
        return Path(self.path)

    @property
    def hostname(self):
        """Alias of .host property. Returns '' (empty string)
        if not present.
        """
        return self._wurl.host

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        elif name in ('username', 'password', 'hostname', 'host', 'port'):
            if name == 'host':
                name = 'hostname'

            current = {
                'username': self.username,
                'password': self.password,
                'hostname': self.hostname,
                'port': self.port
            }

            current[name] = value

            netloc = new_netloc(**current)
            self._wurl = self._wurl.replace(**{'netloc': netloc})
        else:
            self._wurl = self._wurl.replace(**{name: value})

    @property
    def ip_address(self):
        ip_addr = socket.gethostbyname(self.hostname or '')
        return ipaddress.ip_address(to_text(ip_addr))


def new_netloc(username, password, hostname, port):
    netloc = username or ''
    if password:
        netloc += ':{}'.format(password)

    if netloc:
        netloc += '@'

    hostname = hostname or ''

    netloc += hostname

    if port:
        port = int(port)
        netloc += ':{}'.format(port)
    return netloc
