from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[a-z0-9]+")

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def ngrams(tokens: list[str], max_n: int = 3) -> set[str]:
    values = set(tokens)
    for n in range(2, max_n + 1):
        for index in range(0, len(tokens) - n + 1):
            values.add(" ".join(tokens[index:index + n]))
    return values

def terms(text: str) -> set[str]:
    return ngrams(tokenize(text), max_n=3)
