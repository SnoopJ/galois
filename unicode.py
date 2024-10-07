import logging
import itertools
import sys
from typing import List, Tuple

from sopel import plugin

logger = logging.getLogger(__name__)

try:
    import unicodedata2 as unicodedata
except ImportError:
    import unicodedata
    logger.warning(
        "Could not load unicodedata2, using built-in unicodedata. "
        "Unicode database will likely be out of date"
    )
    logger.debug("Exception details:", exc_info=True)


# from CPython Objects/unicodectype.c:_PyUnicode_IsPrintable()
NONPRINTABLE_CATEGORIES = {
  "Cc",  # Other, Control
  "Cf",  # Other, Format
  "Cs",  # Other, Surrogate
  "Co",  # Other, Private Use
  "Cn",  # Other, Not Assigned
  "Zl",  # Separator, Line
  "Zp",  # Separator, Paragraph
  "Zs",  # Separator, Space (other than ASCII space('\x20')).
}

def isprintable(s: str) -> bool:
    """
    Replacement for str.isprintable() that supports a newer UCD
    """
    return all(unicodedata.category(c) not in NONPRINTABLE_CATEGORIES for c in s)



MAX_LEN = 16

NAME_TO_CODEPOINT = {unicodedata.name(chr(n), ''): n for n in range(sys.maxunicode)}
NAME_TO_CODEPOINT.pop('')

UNICODE_V1_NAMES = {
    0x0000: "NULL",
    0x0001: "START OF HEADING",
    0x0002: "START OF TEXT",
    0x0003: "END OF TEXT",
    0x0004: "END OF TRANSMISSION",
    0x0005: "ENQUIRY",
    0x0006: "ACKNOWLEDGE",
    0x0007: "BELL",
    0x0008: "BACKSPACE",
    0x0009: "CHARACTER TABULATION",
    0x000A: "LINE FEED (LF)",
    0x000B: "LINE TABULATION",
    0x000C: "FORM FEED (FF)",
    0x000D: "CARRIAGE RETURN (CR)",
    0x000E: "SHIFT OUT",
    0x000F: "SHIFT IN",
    0x0010: "DATA LINK ESCAPE",
    0x0011: "DEVICE CONTROL ONE",
    0x0012: "DEVICE CONTROL TWO",
    0x0013: "DEVICE CONTROL THREE",
    0x0014: "DEVICE CONTROL FOUR",
    0x0015: "NEGATIVE ACKNOWLEDGE",
    0x0016: "SYNCHRONOUS IDLE",
    0x0017: "END OF TRANSMISSION BLOCK",
    0x0018: "CANCEL",
    0x0019: "END OF MEDIUM",
    0x001A: "SUBSTITUTE",
    0x001B: "ESCAPE",
    0x001C: "INFORMATION SEPARATOR FOUR",
    0x001D: "INFORMATION SEPARATOR THREE",
    0x001E: "INFORMATION SEPARATOR TWO",
    0x001F: "INFORMATION SEPARATOR ONE",
    0x007F: "DELETE",
    0x0082: "BREAK PERMITTED HERE",
    0x0083: "NO BREAK HERE",
    0x0085: "NEXT LINE (NEL)",
    0x0086: "START OF SELECTED AREA",
    0x0087: "END OF SELECTED AREA",
    0x0088: "CHARACTER TABULATION SET",
    0x0089: "CHARACTER TABULATION WITH JUSTIFICATION",
    0x008A: "LINE TABULATION SET",
    0x008B: "PARTIAL LINE FORWARD",
    0x008C: "PARTIAL LINE BACKWARD",
    0x008D: "REVERSE LINE FEED",
    0x008E: "SINGLE SHIFT TWO",
    0x008F: "SINGLE SHIFT THREE",
    0x0090: "DEVICE CONTROL STRING",
    0x0091: "PRIVATE USE ONE",
    0x0092: "PRIVATE USE TWO",
    0x0093: "SET TRANSMIT STATE",
    0x0094: "CANCEL CHARACTER",
    0x0095: "MESSAGE WAITING",
    0x0096: "START OF GUARDED AREA",
    0x0097: "END OF GUARDED AREA",
    0x0098: "START OF STRING",
    0x009A: "SINGLE CHARACTER INTRODUCER",
    0x009B: "CONTROL SEQUENCE INTRODUCER",
    0x009C: "STRING TERMINATOR",
    0x009D: "OPERATING SYSTEM COMMAND",
    0x009E: "PRIVACY MESSAGE",
    0x009F: "APPLICATION PROGRAM COMMAND",
}

NPUA_HI_SURR = range(0xD800, 0xDB74 + 1)  # Non Private Use High Surrogate
PUA_HI_SURR = range(0xDB80, 0xDBFF + 1)  # Private Use High Surrogate
LO_SURR = range(0xDC00, 0xDFFF + 1)  # Low Surrogate

TANGUT_IDEO = range(0x17000, 0x187F7 + 1)  # TANGUT IDEOGRAPH-N
TANGUT_IDEO_SUPP = range(0x18D00, 0x18D08 + 1)  # TANGUT IDEOGRAPH-N

def _char_name(char: str) -> Tuple[str, str]:
    codept = ord(char)
    notation = f"U+{codept:0>4x}".upper()
    category = unicodedata.category(char)

    if isprintable(char):
        char_sym = char
    else:
        char_sym = repr(char)
    try:
        name = unicodedata.name(char)
    except ValueError:
        if codept in UNICODE_V1_NAMES:
            name = UNICODE_V1_NAMES[codept]
        elif category == "Co":
            name = "PRIVATE USE AREA"
        elif codept in NPUA_HI_SURR:
            name = "NON PRIVATE USE HIGH SURROGATE"
        elif codept in PUA_HI_SURR:
            name = "PRIVATE USE HIGH SURROGATE"
        elif codept in LO_SURR:
            name = "LOW SURROGATE"
        elif codept in TANGUT_IDEO or codept in TANGUT_IDEO_SUPP:
            name = "TANGUT IDEOGRAPH-" + notation[2:]
        else:
            name = "<NO NAME>"

    return char_sym, name


def _describe_char(char: str) -> str:
    codept = ord(char)
    notation = f"U+{codept:0>4x}".upper()
    category = unicodedata.category(char)
    try:
        import unicode_age  # https://pypi.org/project/unicode-age/
        major, minor = unicode_age.version(codept)
        ver_str = f"v{major}.{minor} "
    except:
        ver_str = ""

    try:
        char_sym, name = _char_name(char)
        return f"{char_sym}: {notation} {ver_str}({category}) {name}"
    except ValueError:
        return f"No info for {notation} in Unicode {unicodedata.unidata_version}"


def do_search(bot, trigger, query):
    MAX_MATCHES = 10
    NUM_PUBLIC_MATCHES = 2

    is_channel = trigger.sender and not trigger.sender.is_nick()

    matches = [(name, codepoint) for (name, codepoint) in NAME_TO_CODEPOINT.items() if all(term.casefold() in name.casefold() for term in query.split())]
    N_match = len(matches)
    if N_match == 0:
        bot.say("No results")
        return False
    elif is_channel and N_match > MAX_MATCHES:
        bot.say(f"Maximum number of results ({MAX_MATCHES}) exceeded, got {N_match}, giving up")
        return False
    else:
        bot.say(f"{N_match} results:")

    names, codepoints = zip(*matches)

    def _say_matches(matches: List[Tuple[str, int]], dest=None):
        for (name, codepoint) in matches:
            bot.say(f"{chr(codepoint)} U+{codepoint:04x} {name}", destination=dest)

    if trigger.sender.is_nick():
        _say_matches(matches)
    else:
        _say_matches(matches[:NUM_PUBLIC_MATCHES])

        N_excess = N_match - NUM_PUBLIC_MATCHES
        if N_excess > 0:
            bot.say(f"{N_excess} other results")
#             bot.say(f"{N_excess} other results, sending you the full list in PM")
#             _say_matches(matches, dest=trigger.nick)


def describe_string(bot, chars: str, no_ascii: bool = False):
    if no_ascii:
        s = "".join(c for c in chars if ord(c) not in range(128))
    else:
        s = chars

    for c in s:
        msg = _describe_char(c)
        bot.say(msg)


# TODO: less clumsy ZWJ sequence handling
@plugin.commands("u", "unicode", "u:search", "u:noascii")
def unicode_summarize(bot, trigger):
    cmd = trigger.group(1)
    s = trigger.group(0)[len(cmd)+2:].replace(" ", "")

    if cmd == "u:search":
        return do_search(bot, trigger, query=s)

    prefix, rest = s[:2].lower(), s[2:]
    if prefix in ("u+", "0x", r"\u"):
        codept = int(rest.strip(), base=16)
        msg = _describe_char(chr(codept))
        bot.say(msg)
        return True

    len_overrides = {"#kspacademia"}
    if not trigger.sender.is_nick() and trigger.sender not in len_overrides and len(s) > MAX_LEN:
        bot.say(f"Whoa now, that's too many characters, hoss (max {MAX_LEN})")
        return False

    if cmd == "u:noascii":
        describe_string(bot, chars=s, no_ascii=True)
    else:
        describe_string(bot, chars=s)


@plugin.commands("decompose")
def unicode_decompose(bot, trigger):
    bot.say(
        "The !decompose command has been deprecated. Use !NFKD for the old behavior (see also: !NFC, !NFD, !NFKC)"
    )
    return False


@plugin.commands("NFC", "NFD", "NFKD", "NFKC")
def normalized_forms(bot, trigger):
    form = trigger.group(1)
    s = trigger.group(2)

    normalized = list(
        itertools.chain.from_iterable(unicodedata.normalize(form.upper(), s))
    )

    if trigger.sender != "#kspacademia" and len(normalized) > MAX_LEN:
        bot.say(f"Can only decompose up to {MAX_LEN} characters at a time")
        return False

    for char in normalized:
        msg = _describe_char(char)
        bot.say(msg)
