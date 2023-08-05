# -*- coding:utf-8 -*-

import string
import calendar

from email.utils import parsedate_tz
from email.header import decode_header
from email.base64mime import body_encode


def full_decode_header(header):
    """Return the header fully decoded as text"""
    return " ".join(
        p[0].decode(p[1] or "latin1")
        for p in decode_header(header)
    )


def get_header(message, header):
    """Return the header as text, or list if it is not unique"""
    retv = [full_decode_header(v) for v in message.get_all(header)]
    if len(retv) == 1:
        return retv[0]
    return retv


def dict_headers(message, headers=None):
    """Build a dict extracting the specified headers from the
    message, and converting the date if included"""
    keys = {string.capwords(k, "-") for k in message.keys()}
    if headers:
        keys.intersection_update([string.capwords(k, "-") for k in headers])
    retv = {
        header: get_header(message, header)
        for header in keys
    }
    if "Date" in retv:
        date_tuple = parsedate_tz(retv["Date"])
        retv["Date"] = calendar.timegm(date_tuple)
        # TODO: CHECK IF IT IS NEEDED TO SUBTRACT THE TIMEZONE d_t[9]
    return retv


def dettach_payloads(message, payloads=None, path=None):
    if path is None:
        path = [0]
        payloads = {}
    if message.is_multipart():
        for i, att in enumerate(message.get_payload()):
            dettach_payloads(att, payloads, path + [i])
    elif message.get_content_maintype() != "text":
        att = message.get_payload(decode=True)
        if len(att) > 2048:
            payloads[tuple(path)] = att
            message.set_payload("")
    return payloads


def attach_payloads(message, payloads, path=None):
    if path is None:
        path = [0]
    if message.is_multipart():
        for i, att in enumerate(message.get_payload()):
            attach_payloads(att, payloads, path + [i])
    elif message.get_content_maintype() != "text":
        att = payloads.get(tuple(path))
        if att is not None:
            if message["Content-Transfer-Encoding"] == "base64":
                att = body_encode(att)
            message.set_payload(att)


def _get_decoded_payload(part):
    cset = part.get_content_charset("latin1")
    payload = part.get_payload(decode=True)
    try:
        payload = payload.decode(cset)
    except:
        payload = payload.decode("latin1")
    return payload


def _ensure_readable(text):
    non_ascii = sum(1 if ord(c) > 127 else 0 for c in text)
    if non_ascii > len(text) / 2:
        return "[garbled message]"
    return text


def extract_snippet(message):
    """Scan all mail parts for text to summarize the message"""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            payload = _get_decoded_payload(part)
            retv = u" ".join(payload[:200].split())[:100].strip()
            if retv:
                return _ensure_readable(retv)
    try:
        from html import unescape
    except:
        import HTMLParser
        unescape = HTMLParser.HTMLParser().unescape
    for part in message.walk():
        if part.get_content_type() == "text/html":
            payload = _get_decoded_payload(part)
            import re
            retv = u" ".join(
                u" ".join(unescape(word) for word in words.split())
                for words in re.split("(?s)<.*?>", payload[:2000])
                if words.strip()
            )[:100]
            if retv:
                return _ensure_readable(retv)
    return u""
