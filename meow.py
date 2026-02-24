import random

from sopel import plugin

meows = ["喵", "猫･ﾟ「にゃあああー」", "(^=◕ᴥ◕=^)", "mew mew mew", "[bites you]"]


@plugin.commands("meow", "猫", "mew")
def meow(bot, trigger):
    bot.say(random.choice(meows))
