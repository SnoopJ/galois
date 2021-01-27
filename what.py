import re
from datetime import datetime

from sopel import module

SUBWAY_SANDWICHES = [
    "Sweet Onion Chicken Teriyaki",
    "Oven Roasted Chicken",
    "Turkey Breast",
    "Italian B.M.T.",
    "Tuna",
    "Black Forest Ham",
    "Meatball Marinara",
]


@module.commands("what", "wat")
def what(bot, trigger):
    if trigger.group(2) and re.match(
        r"is the subway(\s?(.+?)?\s?(sub)? of the day)?", trigger.group(2).lower()
    ):
        dayofweek = datetime.now().weekday()
        bot.reply(
            "The Subway sub of the day is {}".format(SUBWAY_SANDWICHES[dayofweek])
        )
    elif trigger.group(2) == "do you want?":
        bot.reply("I don't know what you want human.")
    else:
        bot.reply("I only know about subway subs")
