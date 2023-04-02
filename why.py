from sopel import plugin


@plugin.commands("why", "whynot")
@plugin.example("!why do you hate me?")
def why(bot, trigger):
    """ why something """
    bot.reply("because reasons")
