import json
import os
import random

from sopel import plugin


def setup(self):
    fn = self.nick + "-" + self.config.core.host + ".firmwares.json"
    self.memory["firmware_filename"] = os.path.join(self.config.core.homedir, fn)

    try:
        with open(self.memory["firmware_filename"], "r") as f:
            self.memory["firmwares"] = json.load(f)
    except:
        self.memory["firmwares"] = []


def add_firmware(bot, grp):
    firmwares = bot.memory["firmwares"]

    cmd, _, url = grp.partition(" ")
    url = url.strip()
    needs_serialize = False

    if cmd == "-add":
        if url in firmwares:
            bot.say("Entry already exists!")
        else:
            firmwares.append(url)
            bot.say("Added")
            needs_serialize = True
    elif cmd == "-del":
        if url not in firmwares:
            bot.say("Entry does not exist.")
        else:
            firmwares.remove(url)
            bot.say("Deleted")
            needs_serialize = True
    else:
        bot.say("Invalid command")

    if needs_serialize:
        # if we made it down here, the database needs to be updated on disk
        with open(bot.memory["firmware_filename"], "w") as f:
            json.dump(firmwares, f, indent=4)


@plugin.commands("firmware", "fw")
def firmware_gatcha(bot, trigger):
    """Give a random firmware, or add one"""

    firmwares = bot.memory["firmwares"]
    cmd, grp, *rest = trigger.groups()

    if grp and grp.startswith("-"):
        add_firmware(bot, grp)
    else:
        if not firmwares:
            bot.say("No firmware available")
            return False

        bot.say(random.choice(firmwares))
