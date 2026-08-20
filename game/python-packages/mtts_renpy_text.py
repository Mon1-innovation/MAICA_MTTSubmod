# -*- coding: utf-8 -*-
"""Helpers for displaying untrusted values through Ren'Py text nodes."""

import sys


try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)


def to_unicode(value):
    if value is None:
        return u""
    try:
        bytearray_type = bytearray
    except NameError:
        bytearray_type = ()
    if bytearray_type and isinstance(value, bytearray_type):
        try:
            return value.decode("utf-8")
        except (UnicodeDecodeError, TypeError):
            return value.decode("utf-8", "replace")
    if sys.version_info[0] >= 3 and isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("utf-8", "replace")
    if isinstance(value, string_types):
        if sys.version_info[0] == 2 and not isinstance(value, unicode):
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return value.decode("utf-8", "replace")
        return value
    try:
        return unicode(value)
    except NameError:
        return str(value)


RENPY_DIALOGUE_SUBSTITUTIONS = (
    u"[mas_get_player_nickname()]",
    u"[player]",
    u"[m_name]",
)


def escape_renpy_text(value, allowed_substitutions=(), interpolation_passes=1):
    """Escape external text for one or more Ren'Py interpolation passes."""
    source = to_unicode(value)
    interpolation_passes = int(interpolation_passes)
    if interpolation_passes < 1:
        raise ValueError("interpolation_passes must be at least 1")

    literal_opening = u"[" * (2 ** interpolation_passes)
    trusted_opening = u"[" * (2 ** (interpolation_passes - 1))
    allowed = sorted(
        (to_unicode(item) for item in allowed_substitutions if item),
        key=len,
        reverse=True,
    )

    escaped = []
    index = 0
    while index < len(source):
        char = source[index]
        if char == u"[":
            matched = None
            for substitution in allowed:
                if source.startswith(substitution, index):
                    matched = substitution
                    break
            if matched is not None:
                escaped.append(trusted_opening + matched[1:])
                index += len(matched)
                continue
            escaped.append(literal_opening)
        elif char == u"{":
            escaped.append(u"{{")
        else:
            escaped.append(char)
        index += 1
    return u"".join(escaped)


def trim_unclosed_renpy_markers(value):
    """Drop a trailing fragment that begins an unclosed marker."""
    text = to_unicode(value)
    pairs = ((u"[", u"]"), (u"{", u"}"))

    while text:
        cut_at = len(text)
        for opening, closing in pairs:
            openings = []
            for index, char in enumerate(text):
                if char == opening:
                    openings.append(index)
                elif char == closing and openings:
                    openings.pop()
            if openings:
                cut_at = min(cut_at, openings[0])
        if cut_at == len(text):
            break
        text = text[:cut_at]
    return text


def build_renpy_text_preview(value, limit, allowed_substitutions=()):
    """Create a bounded, display-safe preview without partial markers."""
    source = to_unicode(value)
    limit = max(0, int(limit))
    truncated = len(source) > limit
    preview = source[:limit].replace(u"\r", u"").replace(u"\n", u"")
    preview = trim_unclosed_renpy_markers(preview)
    preview = escape_renpy_text(preview, allowed_substitutions)
    return preview + (u"..." if truncated else u"")


def escape_exception_text(value, max_chars=120):
    """Bound and escape an exception before passing it to a Ren'Py notify."""
    text = to_unicode(value)
    if max_chars and len(text) > max_chars:
        text = text[:max_chars - 1] + u"\u2026"
    return escape_renpy_text(text)
