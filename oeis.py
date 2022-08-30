from dataclasses import dataclass
import random
from http import HTTPStatus

import lxml.html
import requests

from sopel import plugin


OEIS_URL = "http://oeis.org/"


@dataclass
class OEISSequence:
    seq: list[int]
    id: str
    desc: str


def random_sequence() -> OEISSequence:
    rand = random.randint(0, 2**32)
    response = requests.get(f"{OEIS_URL}/webcam", params={"fromjavascript": 1})
    response.raise_for_status()

    doc = lxml.html.fromstring(response.content)
    seq = [int(val) for val in doc.xpath("//tt")[0].text.split(",")]
    id = doc.xpath("//a")[0].attrib["href"].lstrip("/")
    desc = doc.xpath("//td[@valign]")[2].text.strip()
    return OEISSequence(seq, id, desc)


N_TERMS = 7

@plugin.commands("oeis")
def random_oeis_sequence(bot, trigger):
    try:
        seq = random_sequence()
        url = f"{OEIS_URL}{seq.id}"
        seq_display = ", ".join(str(term) for term in seq.seq[:N_TERMS]) + "…"
        bot.say(f"{seq.id}: {seq_display} ({url})")
    except requests.exceptions.HTTPError as exc:
        errcode = exc.response.status_code
        errname = HTTPStatus(errcode).name.replace("_", " ").title()
        bot.say(f"Error: HTTP {errcode} ({errname})")
