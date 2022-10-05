from sopel import plugin


@plugin.rule("$nickname!+")
def hello_yourself(bot, trigger):
    bot.say(f"{str(trigger.nick)}! \o/")
