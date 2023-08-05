from python_version cimport PY_MAJOR_VERSION
from cpython cimport int as cint, str, bool, bytes as cbytes


if PY_MAJOR_VERSION < 3:
    import cStringIO
    StringIO = BytesIO = cStringIO.StringIO
    bytes = str

    def b(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        elif isinstance(s, str):
            return s

        raise TypeError("Expect unicode or str not '%s'" % type(s))

    def u(s):
        if isinstance(s, str):
            return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
        elif isinstance(s, unicode):
            return s

        raise TypeError("Expect unicode or str not '%s'" % type(s))

else:
    from io import StringIO, BytesIO
    unicode = str
    bytes = bytes

    def b(s):
        if isinstance(s, bytes):
            return s
        elif isinstance(s, str):
            return s.encode("latin-1")
        raise TypeError("Expect bytes or str not '%s'" % type(s))

    def u(s):
        if isinstance(s, str):
            return s
        elif isinstance(s, bytes):
            return s.decode('utf-8')

        raise TypeError("Expect bytes or str not '%s'" % type(s))


bchr = lambda i: b(chr(i))

string_types = str, bytes


def byte2int(byte):
    if isinstance(byte, int):
        return byte

    return ord(b(byte))


def int2byte(cint n):
    return b(chr(n))


def str2bytes(str s):
    return b(s)


def str2unicode(str s):
    return u(s)


def bytes2str(cbytes b):
    return str(b)


def decodebytes(cbytes b, str encoding):
    return b.decode(encoding)


def advance_iterator(it):
    return next(it)
