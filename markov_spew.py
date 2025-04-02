from itertools import accumulate
import json
import random
import time
from pathlib import Path

from markovify import Chain

from sopel import plugin


HERE = Path(__file__).parent.resolve()

def setup(bot):
    bot.memory["hn_markov_model"] = Chain.from_json(Path(HERE, "hn_markov.json").read_text())
    bot.memory["hn_altman_markov_model"] = Chain.from_json(Path(HERE, "hn_markov_altman.json").read_text())


def _should_reply(bot, trigger):
    thanked = 'thank' in trigger.raw.lower()
    greeted = trigger.raw.strip().startswith(bot.nick + "!")
    if thanked or greeted:
        # kludge: don't spew if we were thanked or greeted
        return False
    elif '?' in trigger.raw and random.random() < QUESTION_REPLY_CHANCE:
        # questions get a higher reply chance
        return True
    elif random.random() < REPLY_CHANCE:
        return True
    else:
        return False


REPLY_CHANCE = 0.05
QUESTION_REPLY_CHANCE = 0.3
@plugin.rate(5)
@plugin.rule(".*$nickname.*")
def prompted_markov(bot, trigger):
    if _should_reply(bot, trigger):
        markov_model = bot.memory["hn_markov_model"]
        msg = markov_freestyle(markov_model, maxlen=128)
        bot.say(msg)


def _valid_word(word: str):
    return (not word.startswith("!,") and
            not "http://" in word
            )


def _genmarkov(markov_model: Chain, maxlen=None, max_attempts=10):
    for _ in range(max_attempts):
        msg = ' '.join(word for word in markov_model.gen() if _valid_word(word))
        msg = limit_message(msg, maxlen=maxlen)
        if msg:
            break
    else:
        return None

    return msg


def limit_message(msg: str, maxlen: int = None) -> str:
    if maxlen is None:
        return msg
    else:
        words = msg.split()
        cumlen = list(accumulate(words, func=lambda acc, s: acc+len(s), initial=0))
        idx = next((i for i, L in enumerate(cumlen) if L > maxlen), None)
        if idx is None or idx <= 1:
            return msg
        return " ".join(words[:idx-1])


def markov_freestyle(markov_model: Chain, maxlen=None, max_attempts=10):
    msg = _genmarkov(markov_model, maxlen=maxlen, max_attempts=max_attempts)
    msg = limit_message(msg, maxlen=maxlen)

    return msg


@plugin.commands("spew", "spit", "piss", "spoot")
def hackernews_freestyle(bot, trigger, maxlen=None):
    # TODO: use scrollback to seed a chain? start in the middle and walk outwards, maybe. complicated!
    markov_model = bot.memory["hn_markov_model"]
    msg = markov_freestyle(markov_model)

    bot.say(msg)


@plugin.commands("altman")
def altman_freestyle(bot, trigger, maxlen=None):
    markov_model = bot.memory["hn_altman_markov_model"]
    msg = markov_freestyle(markov_model)

    bot.say(msg)



SPEW_CHANNELS = (
    "##python-offtopic",
    "##uncomment",
    "##terribot-testing",
)
MIN_TO_SEC = 60
HR_TO_SEC = 60*MIN_TO_SEC
SPEW_QUIET_TIME = 4*HR_TO_SEC # channel must be quiet for this many seconds before we can spew
SPEW_COOLDOWN_TIME = 5*HR_TO_SEC  # minimum amount of time between spontaneous spews
SPEW_INTERVAL = 30*MIN_TO_SEC # time between checks in seconds
SPEW_CHANCE = 0.1  # probability of a spew on any given check
@plugin.interval(SPEW_INTERVAL)
def babble_in_quiet_channels(bot):
    for chan in SPEW_CHANNELS:
        last_msg_time = bot.db.get_channel_value(chan, "last_message_timestamp")
        last_spew_time = bot.db.get_channel_value(chan, "last_spew_timestamp", 0)

        if not last_msg_time:
            continue

        now = time.monotonic()
        quiet_time = now - last_msg_time
        spew_time = now - last_spew_time

        if quiet_time < SPEW_QUIET_TIME or spew_time < SPEW_COOLDOWN_TIME:
            continue

        if random.random() > SPEW_CHANCE:
            continue

        markov_model = bot.memory["hn_markov_model"]
        msg = _genmarkov(markov_model)
        bot.say(msg, destination=chan)

        bot.db.set_channel_value(chan, "last_spew_timestamp", now)


@plugin.thread(False)
@plugin.rule("(.*)")
@plugin.priority("low")
@plugin.unblockable
@plugin.require_chanmsg
def update_channel_activity(bot, trigger):
    bot.db.set_channel_value(trigger.sender, "last_message_timestamp", time.monotonic())
