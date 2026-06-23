import re

BAD_WORDS = {
    "word1",
    "word2",
    "word3"
}


def toxicity_score(
    text: str
) -> tuple[int, list[str]]:

    score = 0
    matches = []

    text = text.lower()

    for word in BAD_WORDS:

        pattern = rf"\b{re.escape(word)}\b"

        if re.search(pattern, text):

            score += 25
            matches.append(word)

    return score, matches
    