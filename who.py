import random
import re

from sopel import module


@module.commands("who", "whose")
def who(bot, trigger):
    """ Choose from users in this channel """
    # Ideally this should use bot.channels[trigger.sender].users, but it
    # seems that list is not actually properly kept up to date...
    #NOTE:20210126:SnoopJ: I have no idea if that's still the case, but this works
    whoIsHere = list(bot.privileges[trigger.sender].keys())
    who = random.choice(whoIsHere)
    bot.reply(str(who))
