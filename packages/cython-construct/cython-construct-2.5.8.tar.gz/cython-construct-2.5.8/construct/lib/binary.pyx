# encoding: utf-8
from cpython cimport bool, int, dict, list, str, tuple, bytes

from .py3compat import b, string_types


def int_to_bin(int number, int width=32):
    r"""
    :param number:
    :param width:

    Convert an integer into its binary representation in a bytes object.
    Width is the amount of bits to generate. If width is larger than the actual
    amount of bits required to represent number in binary, sign-extension is
    used. If it's smaller, the representation is trimmed to width bits.
    Each "bit" is either '\x00' or '\x01'. The MSBit is first.

    Examples:

        >>> int_to_bin(19, 5)
        '\x01\x00\x00\x01\x01'
        >>> int_to_bin(19, 8)
        '\x00\x00\x00\x01\x00\x00\x01\x01'
    """
    if number < 0:
        number += 1 << width

    cdef int i = width - 1
    cdef list bits = ["\x00"] * width

    while number and i >= 0:
        bits[i] = "\x00\x01"[number & 1]
        number >>= 1
        i -= 1

    return b("".join(bits))

# heavily optimized for performance

def to_int(x):
    if isinstance(x, int):
        return x
    elif isinstance(x, string_types):
        return ord(x)

    raise TypeError("Invalid type: %s" % type(x))


def bin_to_int(bytes bits, bool signed_value=False):
    r"""
    Logical opposite of int_to_bin. Both '0' and '\x00' are considered zero,
    and both '1' and '\x01' are considered one. Set sign to True to interpret
    the number as a 2-s complement signed integer.
    :param bits:
    :param signed_value:
    """

    _bits = b("".join(map(lambda x: "01"[to_int(x) & 1], bits)))

    if signed_value and _bits[0] == "1":
        _bits = _bits[1:]
        bias = 1 << len(_bits)
    else:
        bias = 0

    return int(_bits, 2) - bias


cdef tuple CHAR_TO_BIN = tuple(
    map(
        lambda x: int_to_bin(x, 8),
        range(256)
    )
)

cdef dict BIN_TO_CHAR = dict(
    map(
        lambda x: (int_to_bin(x, 8), b(chr(x))),
        range(256)
    )
)


def encode_bin(bytes data):
    """
    Create a binary representation of the given b'' object. Assume 8-bit
    ASCII. Example:

        >>> encode_bin('ab')
        b"\x00\x01\x01\x00\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x01\x00"

        :param data:
    """

    return b("").join(map(lambda x: CHAR_TO_BIN[x], data))


def decode_bin(bytes data):
    if len(data) & 7:
        raise ValueError("Data length must be a multiple of 8")

    cdef int i = 0
    cdef int j = 0

    l = len(data) // 8

    chars = list([b("")] * l)

    while j < l:
        chars[j] = BIN_TO_CHAR[data[i:i + 8]]
        i += 8
        j += 1

    return b("").join(chars)


def swap_bytes(bytes bits, int bytesize=8):
    r"""
    Bits is a b'' object containing a binary representation. Assuming each
    bytesize bits constitute a bytes, perform a endianness byte swap. Example:

        >>> swap_bytes(b'00011011', 2)
        b'11100100'

        :param bytesize:
        :param bits:
    """
    i = 0
    l = len(bits)
    output = [b("")] * ((l // bytesize) + 1)
    j = len(output) - 1
    while i < l:
        output[j] = bits[i: i + bytesize]
        i += bytesize
        j -= 1
    return b("").join(output)
