import itertools
import unicodedata2 as unicodedata

from sopel import module

MAX_LEN = 16


def _describe_char(bot, char):
    try:
        bot.say(f"{char}: U+{ord(char):0>4x} ({unicodedata.category(char)}) {unicodedata.name(char)}")
    except ValueError:
        bot.say(
            f"No info for U+{ord(char):0>4x} (I only know about Unicode up to {unicodedata.unidata_version})"
        )


@module.commands("u", "unicode")
def unicode_summarize(bot, trigger):
    s = "".join(cmd for cmd in trigger.groups()[1] if cmd)
    if trigger.sender != "#kspacademia" and len(s) > MAX_LEN:
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
