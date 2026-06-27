import re


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "doctor",
    "dr",
    "for",
    "from",
    "help",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "please",
    "provide",
    "the",
    "to",
    "we",
    "what",
    "want",
    "when",
    "where",
    "with",
    "you",
    "your",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def normalize_score(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return min(value / max_value, 1.0)


def tokenize_with_ngrams(text: str, max_n: int = 3) -> list[str]:
    tokens = tokenize(text)
    if max_n <= 1:
        return tokens

    terms = list(tokens)
    for n in range(2, max_n + 1):
        for index in range(0, max(len(tokens) - n + 1, 0)):
            terms.append(" ".join(tokens[index:index + n]))
    return terms
