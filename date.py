from datetime import datetime

from sopel import plugin


# https://www.euro.who.int/en/health-topics/health-emergencies/coronavirus-covid-19/news/news/2020/3/who-announces-covid-19-outbreak-a-pandemic
EPOCH = datetime(day=1, month=3, year=2020)

@plugin.commands("date")
def what_day_in_march(bot, trigger):
    dt = datetime.today() - EPOCH
    bot.say(f"Today is {dt.days + 1} March, 2020")
