from sopel import module


@module.rule(".*bad bot")
def imsorrysenpai(bot, trigger):
    bot.say("=[")


@module.rule(".*good bot")
def senpainoticedme(bot, trigger):
    bot.say("=]")
