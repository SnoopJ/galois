import random
import re

from sopel import plugin

RESPONSES = {
    "en": {
        True: ["yes"],
        False: ["no"],
    },
    "ja": {
        True: ["はい", "ええ"],
        False: ["いいえ", "ない"],
    },
}


@plugin.commands("8", "8ball")
@plugin.example("!8 is this the real life?")
def howmany(bot, trigger):
    """ Ask the bot a yes or no question """
    ans = random.random() < 0.5
    response = random.choice(RESPONSES["en"][ans])

    if not trigger.group(2):
        bot.reply(response)
        return
    else:
        text = trigger.group(2).lower()

    if text.startswith("are you sure"):
        bot.reply("Did I stutter?")
    else:
        bot.reply(response)


@plugin.commands("何", "nan", "nani")
@plugin.example("!何　これは現実なのか？")
def 何(bot, trigger):
    """ Ask the bot a yes or no question """
    ans = random.random() < 0.5
    response = random.choice(RESPONSES["ja"][ans])

    if not trigger.group(2):
        bot.reply(response)
        return
    else:
        text = trigger.group(2).lower()

    if text.startswith("are you sure"):
        response = "何でこのバカ！"

    bot.reply(response)
