"""Text cleaning and preprocessing ported from notebook cell 3."""

import re


def clean_text(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def preprocess_responses(
    texts: list[str], min_length: int = 2
) -> tuple[list[str], dict]:
    original_count = len(texts)
    cleaned = [clean_text(t) for t in texts]
    cleaned = [t for t in cleaned if t and t.lower() not in ("", "nan", "none", "n/a")]
    after_empty = len(cleaned)
    length_filtered = [t for t in cleaned if len(t.split()) >= min_length]

    stats = {
        "original_count": original_count,
        "after_empty_removal": after_empty,
        "empty_removed": original_count - after_empty,
        "short_removed": after_empty - len(length_filtered),
        "final_count": len(length_filtered),
    }
    return length_filtered, stats
