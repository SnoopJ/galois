import itertools
import sys
from typing import List, Tuple

import unicodedata2 as unicodedata

from sopel import module


MAX_LEN = 16


NAME_TO_CODEPOINT = {unicodedata.name(chr(n), ''): n for n in range(sys.maxunicode)}
NAME_TO_CODEPOINT.pop('')


# TODO: !u:no-latin Brünner Männergesangverein → ü: U+00fc LATIN SMALL LETTER U WITH DIAERESIS
@module.rule(r"u:search")
def search_subcmd(bot, trigger):
    MAX_MATCHES = 10
    NUM_PUBLIC_MATCHES = 2

    cmd, *rest = trigger.groups()[1:]
    query = " ".join(word for word in rest if word)

    # TODO: is it silly to recombine the query above, then split() it again? it might be silly.
    matches = [(name, codepoint) for (name, codepoint) in NAME_TO_CODEPOINT.items() if all(term.casefold() in name.casefold() for term in query.split())]
    N_match = len(matches)
    if N_match == 0:
        bot.say("No results")
        return False
    elif N_match > MAX_MATCHES:
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
            bot.say(f"{N_excess} other results, sending you the full list in PM")
            _say_matches(matches, dest=trigger.nick)


def _describe_char(bot, char):
    try:
        bot.say(f"{char}: U+{ord(char):0>4x} ({unicodedata.category(char)}) {unicodedata.name(char)}")
    except ValueError:
        bot.say(
            f"No info for U+{ord(char):0>4x} in Unicode {unicodedata.unidata_version}"
        )


@module.commands("u", "unicode")
def unicode_summarize(bot, trigger):
    s = "".join(cmd for cmd in trigger.groups()[2] if cmd)

    prefix, rest = s[:2].lower(), s[2:]
    if prefix in ("u+", "0x", r"\u"):
        codept = int(rest.strip(), base=16)
        _describe_char(bot, chr(codept))
        return True

    len_overrides = {"#kspacademia"}
    if not trigger.sender.is_nick() and trigger.sender not in len_overrides and len(s) > MAX_LEN:
        bot.say(f"Whoa now, that's too many characters, hoss (max {MAX_LEN})")
        return False

    for c in s:
        _describe_char(bot, c)


@module.commands("decompose")
def unicode_decompose(bot, trigger):
    bot.say(
        "The !decompose command has been deprecated. Use !NFKD for the old behavior (see also: !NFC, !NFD, !NFKC)"
    )
    return False


@module.commands("(NFC|NFD|NFKD|NFKC)")
def normalized_forms(bot, trigger):
    norm = trigger.groups()[1]
    s = "".join(cmd for cmd in trigger.groups()[2] if cmd)

    normalized = list(
        itertools.chain.from_iterable(unicodedata.normalize(norm.upper(), s))
    )

    if trigger.sender != "#kspacademia" and len(normalized) > MAX_LEN:
        bot.say(f"Can only decompose up to {MAX_LEN} characters at a time")
        return False

    for char in normalized:
        _describe_char(bot, char)
