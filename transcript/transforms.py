"""
Transcript transforms

Transforms are for modifying the transcript in ways that can clarify the the
transcription.  Expanding contractions, removing utterances, etc.

The transforms may work across multiple words.

These may safely alter the word count.  In many ways, this is similar to
the role of Typerighter used at The Guardian.

https://www.theguardian.com/info/2021/jan/26/how-we-made-typerighter-the-guardians-style-guide-checker
"""
import logging
from num2words import num2words
import re

def numbers_to_words(words: list[str]) -> list[str]:
    "covert small words into numbers:  0 - 21, plus multiples of powers of 10."
    full_text = " ".join(words)

    def fix_number(match: re.Match) -> str:
        group = match.group(0)
        if group.startswith('0') and len(group) > 1:
            new = group
        else:
            num = int(group)
            if num < 21:
                new = num2words(num)
            else:
                p = 10
                new = str(num)
                while True:
                    if num % p == 0 and num < p * 100:
                        new = num2words(num)
                    p *= 10
                    if p > num or p > 1_000_000_000:
                        break
        return new

    full_text = re.sub(r',(?=\d{3}\D)', '', full_text)
    full_text = re.sub(r'(?<!\$\.\,\:)\b\d+(?!\.\d|\,\d|:\d)', fix_number, full_text)

    return full_text.split()


def currency(words: list[str]) -> list[str]:
    """Handle simple currency to words:
    $0.xx => xx cents
    $xx => xx dollars
    """
    def fix_dollars(match: re.Match):
        num = match.group(1).replace(",", "")
        num = " ".join(numbers_to_words([num]))
        return f"{num} dollar{'s' if num != 'one' else ''}"


    def fix_cents(match: re.Match):
        num = num2words(int(match.group(1)))
        return f"{num} cent{'s' if num != 'one' else ''}"

    full_text = " ".join(words)
    full_text = re.sub(r'\$(\d+(,\d+)*)(?!\.\d*)', fix_dollars, full_text)
    full_text = re.sub(r'\$0\.(\d{2})', fix_cents, full_text)
    return full_text.split()


def dehyphenate(words: list[str]) -> list[str]:
    """Split hyphenated words into two or more words."""
    new_words = []
    for w in words:
        if re.search(r'\w-\w', w):
            new_words.extend(w.split('-'))
        else:
            new_words.append(w)
    return new_words


def okay(words: list[str]) -> list[str]:
    """change OK -> okay"""
    return [re.sub(r'\bok\b', 'okay', w, flags=re.IGNORECASE) for w in words]    
    

def ampersands(words: list[str]) -> list[str]:
    """change & and &amp; to 'and' """
    new_words = []
    for w in words:
        if '&amp;' in w:
            w = w.replace('&amp;', '&')
        new_words.extend(' and '.join(w.split('&')).split())
    return new_words
