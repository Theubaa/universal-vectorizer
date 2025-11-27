import re
from typing import Iterable, Iterator, List


class TextCleaner:
    def __init__(self, lowercase: bool = False):
        self.lowercase = lowercase

    def clean(self, text: str) -> str:
        if not text:
            return ""
        processed = text.replace("\r", " ")
        processed = re.sub(r"\s+", " ", processed)
        if self.lowercase:
            processed = processed.lower()
        return processed.strip()

    def clean_stream(self, stream: Iterable[str]) -> Iterator[str]:
        for block in stream:
            cleaned = self.clean(block)
            if cleaned:
                yield cleaned


def normalize_text_blocks(blocks: List[str]) -> List[str]:
    cleaner = TextCleaner()
    return [cleaner.clean(block) for block in blocks if block.strip()]


