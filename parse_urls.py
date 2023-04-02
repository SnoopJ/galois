import functools
from urllib.parse import urlparse

import lxml.html
import requests
import sopel
from sopel import plugin

# based on RFC 1808 https://www.w3.org/Addressing/rfc1808.txt
# courtesy of http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
URL_REGEX = (
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
MAXSIZE = 2 ** 20

REQUEST_PARAMS = {
    "verify": False,
    "timeout": (22, 10),
    "headers": {"User-Agent": "terribot"},
}

# never parse URLs containing these strings in their hostname
FORBIDDEN_HOSTS = {
    "dpaste.de",
    "wikipedia",
    "twitter",
    "youtube",
    "doi.org",
}


def defer_to(*nicks):
    """
    If any of the given nicks are present in a channel, don't trigger this action.
    """
    nicks = {nick.casefold() for nick in nicks}

    def defer_decorator(func):
        @functools.wraps(func)
        def _defer(bot, trigger, *args, **kwargs):
            if trigger.sender.startswith("#"):
                users_here = list(bot.privileges[trigger.sender].keys())
            else:
                users_here = [trigger.sender]

            if any(str(n).casefold() in nicks for n in users_here):
                return
            else:
                return func(bot, trigger, *args, **kwargs)

        return _defer

    return defer_decorator


@plugin.rate(1)
@plugin.rule(".*({re})".format(re=URL_REGEX))
@defer_to("kmath")
def get_title(bot, trigger):
    """ Get the title of the page referred to by a chat message URL """
    DOMAIN_REMAPS = [("mobile.twitter.com", "twitter.com")]
    url = trigger.group(1)
    for substr, repl in DOMAIN_REMAPS:
        url = url.replace(substr, repl)

    host = urlparse(url).hostname
    if any(badhost.lower() in host.lower() for badhost in FORBIDDEN_HOSTS):
        return False
    try:
        with requests.get(url, stream=True, **REQUEST_PARAMS) as response:
            if not response.ok:
                return

            # only read the first MAXSIZE bytes to find the <title>
            content = ""
            for chunk in response.iter_content(MAXSIZE, decode_unicode=True):
                content += chunk
                if len(content) >= MAXSIZE:
                    break

            if "encoding" in content:
                content = content.encode("utf-8")

            try:
                doc = lxml.html.fromstring(content)
                title = doc.find(".//title").text
                bot.say("title: {title}".format(title=title.strip()))
            except:
                return

    except TypeError:
        return False
