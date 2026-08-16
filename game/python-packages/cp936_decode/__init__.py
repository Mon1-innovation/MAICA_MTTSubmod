# -*- coding: utf-8 -*-
"""Small, dependency-free CP936/GBK decoder.

The Ren'Py builds supported by MTTS include both Python 2 and Python 3.  The
representation of an item from a byte string differs between those runtimes
(``str`` versus an integer), so relying on ``ord(data[index])`` breaks on
Python 3.  The decoder deliberately uses the checked-in mapping table instead
of the platform codec: this preserves the CP936 ``0x80`` Euro sign mapping,
which the stock Python ``gbk`` codec does not provide consistently.
"""

from .cp936_map import CP936_MAP as _CP936_MAP

try:
    _TEXT_TYPE = unicode
except NameError:
    _TEXT_TYPE = str

try:
    _INTEGER_TYPES = (int, long)
except NameError:
    _INTEGER_TYPES = (int,)

try:
    _UNICHAR = unichr
except NameError:
    _UNICHAR = chr


def _one_byte(value):
    """Build a one-byte string on either supported Python runtime."""
    if _TEXT_TYPE is str:
        return bytes((value,))
    return chr(value)


def _byte_value(value):
    """Return an integer for either Python 2 or Python 3 byte items."""
    if isinstance(value, _INTEGER_TYPES):
        return value
    return ord(value)


def _coerce_bytes(data):
    """Normalize bytearray/memoryview inputs without coercing text."""
    if isinstance(data, bytearray):
        # Iterating a bytearray yields one-character strings on Python 2 and
        # integers on Python 3.  Building the result through byte values is
        # portable across both runtimes.
        values = [_byte_value(value) for value in data]
        if not values:
            return b""
        return b"".join(_one_byte(value) for value in values)

    # ``memoryview.tobytes`` is Python 3-only; the fallback keeps Python 2
    # compatible buffer-like objects working where available.
    tobytes = getattr(data, "tobytes", None)
    if callable(tobytes):
        return tobytes()
    tostring = getattr(data, "tostring", None)
    if callable(tostring):
        return tostring()
    return data


def _codepoint(value):
    try:
        return _UNICHAR(int(value, 16))
    except (TypeError, ValueError):
        return u"\ufffd"


def decode_cp936(data):
    """Decode CP936/GBK bytes and replace malformed sequences.

    ``unicode`` input is already decoded and is returned unchanged.  Byte
    input is decoded one code point at a time so an invalid lead byte does not
    consume a valid following ASCII byte.  Unknown or truncated sequences are
    represented by U+FFFD, matching the usual ``errors='replace'`` contract.
    """
    if isinstance(data, _TEXT_TYPE):
        return data

    data = _coerce_bytes(data)
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("decode_cp936 expects bytes or text, got %s" % type(data).__name__)

    out = []
    index = 0
    length = len(data)

    while index < length:
        first = _byte_value(data[index])

        # ASCII and CP936's single-byte Euro sign are represented directly in
        # the table.  Check the single-byte key before looking for a pair.
        single_key = "0x%02X" % first
        if first <= 0x80 and single_key in _CP936_MAP:
            out.append(_codepoint(_CP936_MAP[single_key]))
            index += 1
            continue

        # Bytes above 0x80 are normally a two-byte lead.  A missing trail or
        # unknown pair consumes only the lead, preserving any valid next byte.
        if index + 1 >= length:
            out.append(u"\ufffd")
            index += 1
            continue

        second = _byte_value(data[index + 1])
        pair_key = "0x%02X%02X" % (first, second)
        if pair_key in _CP936_MAP:
            out.append(_codepoint(_CP936_MAP[pair_key]))
            index += 2
        else:
            out.append(u"\ufffd")
            index += 1

    return u"".join(out)


__all__ = ["decode_cp936"]
