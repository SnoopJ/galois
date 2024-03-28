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


@plugin.example("!how much spam")
@plugin.command("how")
def howmany(bot, trigger):
    """ Ask how many/how much of something """
    HOW_PATT = r"(\s?many|\s?much)?(\s*(?P<thing>\S+))?"
    m = re.match(HOW_PATT, trigger.group(2))

    thing_grp = m.group('thing')
    if thing_grp:
        thing_grp = thing_grp.strip()
    else:
        thing_grp = None

    qty = random.randint(0, 1000)
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
