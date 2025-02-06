"""
Various filters to modify transcript word lists to improve comparison.  

These filters MUST not alter the word count because that would cause misalignment
when rendering the original text.
"""
import re


def strip_case(words: list[str]) -> list[str]:
    """Convert things to lower case"""
    return [x.lower() for x in words]


def remove_punctuation(words: list[str]) -> list[str]:
    """Remove punctuation"""
    return [depunctuate_word(x) for x in words]


def remove_numeric_commas(words: list[str]) -> list[str]:
    """Remove comma separators from numbers"""
    return [re.sub(r'(\d),(\d)', r'\1\2', x) for x in words]


def depunctuate_word(word: str) -> str:
    """Remove punctuation symbols from the start/end of a word"""
    while word != '' and not word[0].isalnum():
        word = word[1:]
    while word != '' and not word[-1].isalnum():
        word = word[:-1]
    return word