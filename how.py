import random
import re

from textblob import Word

from sopel import plugin


CUSTOM_PLURALIZATIONS = {
    "🎵": "🎶",
    "🏠": "🏘️",
}


def _maybe_pluralize(thing: str) -> str:
    custom_plural = CUSTOM_PLURALIZATIONS.get(thing)
    if custom_plural is not None:
        plural = custom_plural
    else:
        try:
            plural = Word(thing).pluralize()
        except Exception as exc:
            pass

    if plural[-2:] == "ss":
        # double-s plural is wrong more often than it's right, we failed to pluralize
        return thing
    else:
        return plural


def _thing_grp(trigger):
    if not trigger.group(2):
        return None

    HOW_PATT = r"(\s?many|\s?much)?(\s*(?P<thing>\S+))?"
    m = re.match(HOW_PATT, trigger.group(2))

    if not m:
        return None

    thing_grp = m.group('thing')
    if thing_grp:
        thing_grp = thing_grp.strip()
    else:
        thing_grp = None

    return thing_grp


@plugin.example("!how much spam")
@plugin.command("how")
def howmany(bot, trigger):
    """ Ask how many/how much of something """

    qty = random.randint(0, 1000)

    thing_grp = _thing_grp(trigger)

    if thing_grp is None:
        thing = ""
    # special case: !how many are [whatever predicate]?
    elif thing_grp == ("are"):
        bot.reply(str(qty))
        return
    else:
        thing = thing_grp.rstrip("?").split()[0]

        if qty != 1:
            thing = _maybe_pluralize(thing)

        thing = " " + thing

    bot.reply(f"{qty}{thing}")


いくら = ["いくら", "幾ら", "ikura"]
どれ程 = ["どれほど", "どれ程", "dorehodo"]
どんなに = ["どんなに", "donnani"]

助数詞 = [
    "つ",
    "番目",
    "羽"
]

@plugin.example("!how:jp much spam")
@plugin.command("how:jp", *いくら, *どれ程, *どんなに)
def howmany_jp(bot, trigger):
    """
    質問は「番号何ですか？」

    Ask how many/how much of something
    """

    qty = random.randint(0, 1000)
    counter = random.choice(助数詞)

    bot.reply(f"{qty}{counter}")
