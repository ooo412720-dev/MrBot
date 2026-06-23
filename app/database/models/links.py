import re

URL_REGEX = re.compile(
    r"(https?://|t\.me/)"
)
def contains_link(text):

    return bool(
        URL_REGEX.search(text)
    )