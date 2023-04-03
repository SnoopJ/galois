import ast
import json
from itertools import chain
from pathlib import Path
from typing import Callable
import unicodedata

from sopel import plugin


MAX_LEN = 16

HERE = Path(__file__).parent.resolve()
CLDR_FILE = Path(HERE, "cldr-annotations-v41.json")

# TODO: this needs to be in a setup()
with open(CLDR_FILE, "r") as f:
    data = json.load(f)

# dictionary whose keys are individual codepoints
CLDR_ANNOTS = data["annotations"]["annotations"]


def _codept_name(codept: str) -> str:
    codenum = ord(codept)
    try:
        import unicode_age  # https://pypi.org/project/unicode-age/
        major, minor = unicode_age.version(codenum)
        ver_str = f"v{major}.{minor} "
    except:
        ver_str = ""

    try:
        category = unicodedata.category(codept)
    except ValueError:
        category = ""

    return f"{codept}: U+{codenum:0>4x} {ver_str}({category})"


# TODO: moar CLDR features?
@plugin.commands("cldr")
def cldr(bot, trigger):
    chars = trigger.group(2)

    prefix, rest = chars[:2].lower(), chars[2:]
    if prefix in ("u+", "0x", r"\u"):
        codept = int(rest.strip(), base=16)
        chars = [chr(codept)]

    if trigger.sender != "#kspacademia" and len(chars) > MAX_LEN:
        bot.say(f"Whoa now, that's too many characters, hoss (max {MAX_LEN})")
        return False

    for ch in chars:
        if ch == " ":
            continue
        annots = CLDR_ANNOTS.get(ch, {}).get("default", [])

        if not annots:
            continue

        msg = _codept_name(ch) + " — " + "; ".join(note for note in annots)
        bot.say(msg, truncation="…")
