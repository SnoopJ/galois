import random
import re

from textblob import Word

from sopel import plugin


def howmany_rule(settings):
    prefix = settings.core.prefix
    return [re.compile(rf"{prefix}how(\s?many|\s?much)?(\s*(?P<thing>\S+))?")]



CUSTOM_PLURALIZATIONS = {
    "🎵": "🎶",
    "🏠": "🏘️",
}


def _maybe_pluralize(thing: str) -> str:
    custom_plural = CUSTOM_PLURALIZATIONS.get(thing)
    import q; q.q(thing, custom_plural)
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


@plugin.rule_lazy(howmany_rule)
@plugin.example("!how much spam")
def howmany(bot, trigger):
    """ Ask how many/how much of something """
    thing_grp = trigger.group('thing')
    if thing_grp:
        thing_grp = thing_grp.strip()
    else:
        thing_grp = None

    qty = random.randint(0, 1000)
    if thing_grp is None:
        thing = ""
    # special case: !how many are [whatever predicate]?
    elif thing_grp.startswith("are "):
        bot.reply(str(qty))
        return
    else:
        thing = thing_grp.rstrip("?").split()[0]

        if qty != 1:
            thing = _maybe_pluralize(thing)

        thing = " " + thing

    bot.reply(f"{qty}{thing}")
