import random

import sopel
from sopel import plugin


def setup(bot):
    if not bot.memory.contains("karma"):
        bot.memory["karma"] = sopel.tools.SopelMemory()


@plugin.require_admin()
@plugin.commands("resetkarma")
def resetKarma(bot, trigger):
    if trigger.group(2) is not None:
        bot.memory["karma"][trigger.group(2).strip().lower()] = 0
        bot.reply("Karma for user %s set to 0" % trigger.group(2).strip())
    else:
        bot.memory["karma"] = {}
        bot.reply("Karma for all users has been reset")


@plugin.commands("karma")
def getKarma(bot, trigger):
    """ Show karma for a given username """
    if trigger.group(2) is not None:
        who = trigger.group(2).strip()
    else:
        who = trigger.nick

    whokey = who.lower()

    bot.reply("%s has %i karma" % (who, bot.memory["karma"].get(whokey, 0)))


@plugin.commands("check")
def checkKarma(bot, trigger):
    """ Show karma for a given username, but more betterer """
    if trigger.group(2) is not None:
        who = trigger.group(2).strip()
    else:
        who = trigger.nick

    whokey = who.lower()

    karma = bot.memory["karma"].get(whokey, 0)
    if karma >= -1:
        bot.reply("probably aight")
    else:
        bot.reply("kinda sketchy")


@plugin.rule("(\w+)[:,]?\s*(\+\+|--)")
@plugin.rate(60)
def addKarma(bot, trigger):
    who = trigger.group(1).strip()
    whokey = who.lower()
    if trigger.is_privmsg:
        whoshere = [str(trigger.sender)]
    else:
        whoshere = [str(s).lower() for s in bot.privileges[trigger.sender]]

    if trigger.group(2) == "++":
        karma_adj = 1
    elif trigger.group(2) == "--":
        karma_adj = -1
    else:
        karma_adj = 0

    print(who, trigger.nick, whoshere)

    if who == str(trigger.nick) or whokey not in whoshere:
        return False

    bot.memory["karma"][whokey] = bot.memory["karma"].get(whokey, 0) + karma_adj
