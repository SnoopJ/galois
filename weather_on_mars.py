from sopel import module

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
import requests


HERE = Path(__file__).parent.resolve()
INSIGHT_WEATHER_URL = "https://mars.nasa.gov/rss/api/?feed=weather&category=insight_temperature&feedtype=json&ver=1.0"
CURIOSITY_WEATHER_URL = "https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json"
PERSEVERANCE_WEATHER_URL = "https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json"

TIMEOUT_CACHE = lru_cache(1)


@dataclass
class InstrumentData:
    av: float
    ct: int
    mn: float
    mx: float
    name: str
    unit: str = ""

    @property
    def avg(self): return self.av

    @property
    def count(self): return self.ct

    @property
    def min(self): return self.mn

    @property
    def max(self): return self.mx


@TIMEOUT_CACHE
def _weather(date):
    insight_response = requests.get(INSIGHT_WEATHER_URL)
    curiosity_response = requests.get(CURIOSITY_WEATHER_URL)
    perseverance_response = requests.get(PERSEVERANCE_WEATHER_URL)

    result = {
            "insight": insight_response.json(),
            "curiosity": curiosity_response.json(),
            "perseverance": perseverance_response.json(),
    }
    return result


def weather():
    return _weather(date.today())


@module.commands("mars\s*(insight|curiosity|perseverance)")
def mars_weather(bot, trigger):
    if trigger.group(2) == "insight":
        insight_weather(bot, trigger)
    elif trigger.group(2) == "curiosity":
        curiosity_weather(bot, trigger)
    elif trigger.group(2) == "perseverance":
        perseverance_weather(bot, trigger)
    else:
        bot.say("Usage: !mars (insight|curiosity|perseverance)")

CURIOSITY_WEATHER_MONTHS = {
        "Month 1": "fall",
        "Month 2": "fall",
        "Month 3": "fall",
        "Month 4": "winter",
        "Month 5": "winter",
        "Month 6": "winter",
        "Month 7": "spring",
        "Month 8": "spring",
        "Month 9": "spring",
        "Month 10": "summer",
        "Month 11": "summer",
        "Month 12": "summer",
}

def insight_weather(bot, trigger):
    try:
        data = weather().get("insight", {})
        days = sorted(data.get("sol_keys", []), key=lambda day: int(day))
        if not days:
            bot.say("No data available :(")
            return False

        sol = int(days[-1])
        lastday = data[days[-1]]
        observations = [
            InstrumentData(**lastday["AT"], name="Temp", unit="°F"),
            InstrumentData(**lastday["HWS"], name="Wind", unit=" m/s"),
            InstrumentData(**lastday["PRE"], name="Pressure", unit=" Pa"),
        ]

        bot.say(f"Sol {sol}: It is {lastday['Season']} at Elysium Planitia.")
        for obs in observations:
            avg = f"{obs.avg:>6.1f}{obs.unit:<3}"
            min = f"{obs.min:>6.1f}{obs.unit:<3}"
            max = f"{obs.max:>6.1f}{obs.unit:<3}"
            name = f"Avg {obs.name}"
            bot.say(f"{name:<12}: {avg:<10}    Min: {min:<10}   Max: {max:<10}")
    except Exception as exc:
        bot.say(f"Exception occurred: {exc!r}")
        return False


def curiosity_weather(bot, trigger):
    try:
        response = weather().get("curiosity", {})
        data = {int(datum.get("sol", -1)): datum for datum in response.get("soles", [])}
        days = sorted(data.keys(), reverse=True)

        if not days:
            bot.say("No data available :(")
            return False

        sol = days[0]
        lastday = data[sol]
        min_temp = float(lastday["min_temp"])
        max_temp = float(lastday["max_temp"])
        pressure = float(lastday["pressure"])
        season = CURIOSITY_WEATHER_MONTHS[lastday["season"]]

        bot.say(f"Sol {sol}: It is {season} at Gale Crater:")
        bot.say(f"Temperature:\tMin: {min_temp:.1f} °F    Max: {max_temp:.1f} °F")
        bot.say(f"Pressure   :\t     {pressure} Pa")
    except Exception as exc:
        bot.say(f"Exception occurred: {exc!r}")
        return False


def perseverance_weather(bot, trigger):
    try:
        response = weather().get("perseverance", {})
        data = {int(datum.get("sol", -1)): datum for datum in response.get("sols", [])}
        days = sorted(data.keys(), reverse=True)

        if not days:
            bot.say("No data available :(")
            return False

        sol = days[0]
        lastday = data[sol]
        min_temp = float(lastday["min_temp"])
        max_temp = float(lastday["max_temp"])
        pressure = float(lastday["pressure"])
        season = lastday["season"]

        bot.say(f"Sol {sol}: It is {season} at Jezero Crater:")
        bot.say(f"Temperature:\tMin: {min_temp:.1f} °F    Max: {max_temp:.1f} °F")
        bot.say(f"Pressure   :\t     {pressure} Pa")
    except Exception as exc:
        bot.say(f"Exception occurred: {exc!r}")
        return False
