from sopel import module


@module.commands("source")
def share_source(bot, trigger):
    bot.say("Hack the planet ✊: https://github.com/SnoopJeDi/galois")
