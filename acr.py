import functools
import json
import os
import pprint

import requests
from sopel import module


def setup(self):
    fn = self.nick + "-" + self.config.core.host + ".acr.json"
    self.acr_filename = os.path.join(self.config.core.homedir, fn)

    with open(self.acr_filename, "r") as f:
        try:
            self.memory["acrs"] = json.load(f)
        except:
            self.memory["acrs"] = {}


@module.commands("acr")
@module.example("!acr LOL, !acr -add:SWaG Survey of Water and Ammonia in Galaxies")
def acr(bot, trigger):
    """Define an acronym or add a definition"""

    db = bot.memory["acrs"]
    if len(trigger.groups()) < 2:
        bot.say("Syntax: !acr -add:LOL Lots Of Lagrangians")
        return False
    cmd = trigger.groups()[1]
    cmd, _, defn = cmd.partition(" ")
    cmd, _, a = cmd.partition(":")
    cmd = cmd.lower()

    if cmd == "-add" and defn:
        if not a.strip():
            bot.say("Acronym must be nonempty")
            return False
        if a in db:
            bot.say("Acronym already defined! Try !acr -redef:WTF When Taylor Fails")
            return False
        else:
            db[a] = defn
            bot.say("Definition added!")
    elif cmd == "-redef" and defn:
        db[a] = defn
        bot.say("Definition added!")
    elif cmd == "-del" and a:
        if a not in db:
            bot.say("Acronym not defined")
            return False
        else:
            db.pop(a)
            bot.say("Definition deleted!")
    else:
        bot.say(
            "Invalid command. Valid forms: !acr -add:LMAO Lagrange Made Awesome Orbits, !acr -redef:ROFL Rare Occultations for Life, !acr -del:IEEE"
        )
        return False

    # if we made it down here, the database needs to be updated on disk
    with open(bot.acr_filename, "w") as f:
        json.dump(db, f, indent=4)


@module.rule(r"(\S+)\?")
def get_acr(bot, trigger):
    db = bot.memory["acrs"]

    a = trigger.group(1)
    if a in db:
        bot.say("{a}: {defn}".format(a=a, defn=db[a]))
