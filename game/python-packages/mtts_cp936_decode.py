# -*- coding: utf-8 -*-
"""Private CP936 decoder used by MTTS.

The public ``cp936_decode`` package is shipped by both submods and can be
overwritten when the other submod is installed later.  MTTS therefore keeps
the entry point under a unique module name, while reusing the checked-in map
to preserve CP936 extensions that the platform ``gbk`` codec does not match.
"""

try:
    from cp936_decode.cp936_map import CP936_MAP as _CP936_MAP
except Exception:
    _CP936_MAP = {}

_TEXT_TYPE = str
_PY2 = False
_INTEGER_TYPES = (int,)
_UNICHAR = chr


def _byte_value(value):
    if isinstance(value, _INTEGER_TYPES):
        return value
    return ord(value)


def _bytes_from_values(values):
    return bytes(bytearray(values))


def _coerce_bytes(data):
    if isinstance(data, bytearray):
        return _bytes_from_values([_byte_value(value) for value in data])

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
    """Decode CP936 bytes, replacing malformed sequences with U+FFFD."""
    if isinstance(data, _TEXT_TYPE):
        return data

    data = _coerce_bytes(data)
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(
            "decode_cp936 expects bytes or text, got %s"
            % type(data).__name__
        )

    output = []
    index = 0
    while index < len(data):
        first = _byte_value(data[index])
        if first <= 0x80:
            mapped = _CP936_MAP.get("0x%02X" % first)
            if mapped is not None:
                output.append(_codepoint(mapped))
            else:
                output.append(_UNICHAR(first))
            index += 1
            continue
        if index + 1 >= len(data):
            output.append(u"\ufffd")
            index += 1
            continue

        second = _byte_value(data[index + 1])
        mapped = _CP936_MAP.get("0x%02X%02X" % (first, second))
        if mapped is not None:
            output.append(_codepoint(mapped))
            index += 2
        else:
            # Consume only the invalid lead so a following ASCII byte remains
            # visible to the caller.
            output.append(u"\ufffd")
            index += 1

    return u"".join(output)


__all__ = ["decode_cp936"]
