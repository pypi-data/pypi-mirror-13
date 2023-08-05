from __future__ import absolute_import, print_function, division

import warnings

import six

from .. import encoding, utils


CONTENT_MISSING = 0

if six.PY2:  # pragma: nocover
    _native = lambda x: x
    _always_bytes = lambda x: x
else:
    # While the HTTP head _should_ be ASCII, it's not uncommon for certain headers to be utf-8 encoded.
    _native = lambda x: x.decode("utf-8", "surrogateescape")
    _always_bytes = lambda x: utils.always_bytes(x, "utf-8", "surrogateescape")


class MessageData(object):
    def __eq__(self, other):
        if isinstance(other, MessageData):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Message(object):
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.data == other.data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def headers(self):
        """
        Message headers object

        Returns:
            netlib.http.Headers
        """
        return self.data.headers

    @headers.setter
    def headers(self, h):
        self.data.headers = h

    @property
    def content(self):
        """
        The raw (encoded) HTTP message body

        See also: :py:attr:`text`
        """
        return self.data.content

    @content.setter
    def content(self, content):
        self.data.content = content
        if isinstance(content, bytes):
            self.headers["content-length"] = str(len(content))

    @property
    def http_version(self):
        """
        Version string, e.g. "HTTP/1.1"
        """
        return _native(self.data.http_version)

    @http_version.setter
    def http_version(self, http_version):
        self.data.http_version = _always_bytes(http_version)

    @property
    def timestamp_start(self):
        """
        First byte timestamp
        """
        return self.data.timestamp_start

    @timestamp_start.setter
    def timestamp_start(self, timestamp_start):
        self.data.timestamp_start = timestamp_start

    @property
    def timestamp_end(self):
        """
        Last byte timestamp
        """
        return self.data.timestamp_end

    @timestamp_end.setter
    def timestamp_end(self, timestamp_end):
        self.data.timestamp_end = timestamp_end

    @property
    def text(self):
        """
        The decoded HTTP message body.
        Decoded contents are not cached, so accessing this attribute repeatedly is relatively expensive.

        .. note::
            This is not implemented yet.

        See also: :py:attr:`content`, :py:class:`decoded`
        """
        # This attribute should be called text, because that's what requests does.
        raise NotImplementedError()

    @text.setter
    def text(self, text):
        raise NotImplementedError()

    def decode(self):
        """
            Decodes body based on the current Content-Encoding header, then
            removes the header. If there is no Content-Encoding header, no
            action is taken.

            Returns:
                True, if decoding succeeded.
                False, otherwise.
        """
        ce = self.headers.get("content-encoding")
        data = encoding.decode(ce, self.content)
        if data is None:
            return False
        self.content = data
        self.headers.pop("content-encoding", None)
        return True

    def encode(self, e):
        """
            Encodes body with the encoding e, where e is "gzip", "deflate" or "identity".

            Returns:
                True, if decoding succeeded.
                False, otherwise.
        """
        data = encoding.encode(e, self.content)
        if data is None:
            return False
        self.content = data
        self.headers["content-encoding"] = e
        return True

    # Legacy

    @property
    def body(self):  # pragma: nocover
        warnings.warn(".body is deprecated, use .content instead.", DeprecationWarning)
        return self.content

    @body.setter
    def body(self, body):  # pragma: nocover
        warnings.warn(".body is deprecated, use .content instead.", DeprecationWarning)
        self.content = body


class decoded(object):
    """
    A context manager that decodes a request or response, and then
    re-encodes it with the same encoding after execution of the block.

    Example:

    .. code-block:: python

        with decoded(request):
            request.content = request.content.replace("foo", "bar")
    """

    def __init__(self, message):
        self.message = message
        ce = message.headers.get("content-encoding")
        if ce in encoding.ENCODINGS:
            self.ce = ce
        else:
            self.ce = None

    def __enter__(self):
        if self.ce:
            self.message.decode()

    def __exit__(self, type, value, tb):
        if self.ce:
            self.message.encode(self.ce)