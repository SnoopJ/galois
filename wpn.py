import functools
import json
import os
import random

from sopel import plugin


def setup(self):
    fn = self.nick + "-" + self.config.core.host + ".wpns.json"
    self.wpn_filename = os.path.join(self.config.core.homedir, fn)

    try:
        with open(self.wpn_filename, "r") as f:
            self.memory["wpns"] = json.load(f)
    except:
        self.memory["wpns"] = {
            "wpn": ["trout", "rubber chicken"],
            "adj": ["superluminal", "divergent"],
        }


ATTACH_PROBABILITY = 0.2


def make_wpn(wpndb):
    numadj = random.randint(0, 2)
    adjs = random.sample(wpndb["adj"], numadj)
    if random.random() < ATTACH_PROBABILITY:
        atmt = random.choice(wpndb["wpn"])
        article = "an" if atmt[0].lower() in "aeiou" else "a"
        attachment = " with {article} {atmt} attachment".format(
            article=article, atmt=atmt
        )
    else:
        attachment = ""
    wpn = (" " if adjs else "") + random.choice(wpndb["wpn"])
    return "{adj}{wpn}{attachment}".format(
        adj=" ".join(adjs), wpn=wpn, attachment=attachment
    )


@module.commands("wpn")
def wpn(bot, trigger):
    """ Give a random wpn, or add one """

    wpndb = bot.memory["wpns"]
    if not trigger.group(2) or trigger.group(2)[0] != "-":
        who = (trigger.group(2) or str(trigger.nick)).strip()
        wpn = make_wpn(wpndb)
        article = "an" if wpn[0].lower() in "aeiou" else "a"
        bot.action(
            "gives {nick} {article} {wpn}".format(nick=who, article=article, wpn=wpn)
        )
        return True

    cmd = trigger.groups()[1]
    cmd, _, thing = cmd.partition(" ")
    thing = thing.strip()
    cmd, _, t = cmd.partition(":")
    cmd = cmd.lower()

    if cmd == "-add" and t in ("wpn", "adj"):
        if thing in wpndb[t]:
            bot.say("Entry already exists!")
            return False
        else:
            wpndb[t].append(thing)
            bot.say("Added {} '{}'".format(t, thing))
    elif cmd == "-del" and t in ("wpn", "adj"):
        if thing not in wpndb[t]:
            bot.say("Entry does not exist.")
            return False
        else:
            wpndb[t].remove(thing)
            bot.say("Deleted {} '{}'".format(t, thing))
    else:
        bot.say(
            "Invalid command. Valid forms: !wpn, !wpn someone, !wpn -add:wpn morphism, !wpn -add:adj IEEE 754, !wpn -del:wpn trout, !wpn -del:adj symmetric"
        )
        return False

    # if we made it down here, the database needs to be updated on disk
    with open(bot.wpn_filename, "w") as f:
        json.dump(wpndb, f, indent=4)
