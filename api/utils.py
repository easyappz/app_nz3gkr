from __future__ import annotations

from typing import List, Tuple

from .models import BannedWord


SEPARATORS = set(
    list(" \t\n\r")
    + list(
        ",.;:!?()[]{}\"'<>/\\|@#$%^&*-_+=~`"
    )
)


def _split_text(text: str) -> List[Tuple[bool, str]]:
    """
    Split text into a list of tokens preserving separators.
    Returns list of tuples: (is_word, token_text)
    is_word=True for alphanumeric sequences, False for separators.
    No regex is used.
    """
    tokens: List[Tuple[bool, str]] = []
    buf: List[str] = []
    buf_is_word = None

    def flush():
        nonlocal buf, buf_is_word
        if buf:
            tokens.append((bool(buf_is_word), "".join(buf)))
            buf = []
            buf_is_word = None

    for ch in text:
        is_sep = ch in SEPARATORS
        is_word_char = not is_sep
        if buf_is_word is None:
            buf_is_word = is_word_char
            buf.append(ch)
            continue
        if buf_is_word == is_word_char:
            buf.append(ch)
        else:
            flush()
            buf_is_word = is_word_char
            buf.append(ch)
    flush()
    return tokens


def censor_profanity(text: str) -> str:
    """
    Replace words that contain banned substrings with asterisks of the same length.
    Case-insensitive. Uses BannedWord.is_active=True. No regex.
    """
    banned = list(BannedWord.objects.filter(is_active=True).values_list("word", flat=True))
    banned = [w.strip().lower() for w in banned if w and w.strip()]
    if not banned:
        return text

    tokens = _split_text(text)
    censored_parts: List[str] = []

    for is_word, token in tokens:
        if not is_word:
            censored_parts.append(token)
            continue
        lower_token = token.lower()
        should_censor = False
        for bw in banned:
            if bw and bw in lower_token:
                should_censor = True
                break
        if should_censor:
            censored_parts.append("*" * len(token))
        else:
            censored_parts.append(token)

    return "".join(censored_parts)
