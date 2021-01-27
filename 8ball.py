import random
import re

from sopel import module

responses = ["yes", "no"]


@module.commands("8")
@module.example("!8 is this the real life?")
def howmany(bot, trigger):
    """ Ask the bot a yes or no question """
    if not trigger.group(2):
        bot.reply(random.choice(responses))
        return
    else:
        text = trigger.group(2).lower()

    if text.startswith("are you sure"):
        bot.reply("Did I stutter?")
    else:
        bot.reply(random.choice(responses))
