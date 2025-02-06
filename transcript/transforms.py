"""
Transcript transforms

Transforms are for modifying the transcript in ways that can clarify the the
transcription.  Expanding contractions, removing utterances, etc.

The transforms may work across multiple words.

These may safely alter the word count
"""
from num2words import num2words
import re

def numbers_to_words(words: list[str]) -> list[str]:
    "covert small words into numbers:  0 - 21, [3456789]0"
    full_text = " ".join(words)

    def fix_number(match: re.Match) -> str:
        num = int(match.group(0))
        if num < 21:
            return num2words(num)
        elif num % 10 == 0 and num < 100:
            return num2words(num)
        else:        
            return str(num)

    full_text = re.sub(r'\b\d+\b', fix_number, full_text)

    return full_text.split()