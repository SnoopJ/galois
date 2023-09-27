import random
import re

from textblob import Word

from sopel import plugin


def howmany_rule(settings):
    prefix = settings.core.prefix
    return [re.compile(rf"{prefix}how(\s?many|\s?much)?(\s*(\S+))?")]


@plugin.rule_lazy(howmany_rule)
@plugin.example("!how much spam")
def howmany(bot, trigger):
    """ Ask how many/how much of something """
    if trigger.group(3):
        thing_grp = trigger.group(3).lstrip()
    else:
        thing_grp = None

    qty = random.randint(0, 1000)
    if thing_grp is not None:
        # special case: !how many
        if thing_grp is None:
            bot.reply(str(qt))
        # special case: !how many are [whatever predicate]?
        elif thing_grp.startswith("are "):
            bot.reply(str(qty))
            return
        thing = thing_grp.rstrip("?").split()[0]

        if qty != 1 and thing.isalpha():
            try:
                plural = Word(thing).pluralize()
            except Exception as exc:
                pass
            if plural[-2:] == "ss":
                # double-s plural is wrong more often than it's right
                pass
            else:
                thing = plural

    else:
        thing = ""
    bot.reply(f"{qty} {thing}")
