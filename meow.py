import random

from sopel import plugin

meows = ["喵", "猫･ﾟ「にゃあああー」", "(^=◕ᴥ◕=^)"]


@plugin.commands("meow")
def meow(bot, trigger):
    bot.say(random.choice(meows))
