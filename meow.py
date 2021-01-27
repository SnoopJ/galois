import random

from sopel import module

meows = ["喵", "猫･ﾟ「にゃあああー」", "(^=◕ᴥ◕=^)"]


@module.commands("meow")
def meow(bot, trigger):
    bot.say(random.choice(meows))
