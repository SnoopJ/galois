from sopel import plugin


@plugin.rule(".*bad bot")
def imsorrysenpai(bot, trigger):
    bot.say("=[")


@plugin.rule(".*good bot")
def senpainoticedme(bot, trigger):
    bot.say("=]")
