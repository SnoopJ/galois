from sopel import plugin


@plugin.commands("source")
def share_source(bot, trigger):
    bot.say("Hack the planet ✊: https://git.snoopj.dev/SnoopJ/galois")
