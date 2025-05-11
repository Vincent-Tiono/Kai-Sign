"""Module with functions to change casing of a string."""

__all__ = (
    "get_words",
    "to_camel",
    "to_dot",
    "to_kebab",
    "to_pascal",
    "to_snake",
    "to_title",
)

import re
import warnings

from typing import Union


def to_camel(string: str) -> str:
    """Return a version of the string in camelCase format."""
    preserve_upper = not string.isupper()
    words = get_words(string)
    first_word = ""
    if len(words) > 0:
        first_word = (
            words[0] if words[0].isupper() and preserve_upper else words[0].lower()
        )
    return first_word + "".join(_capitalize(w, preserve_upper) for w in words[1:])


def to_dot(string: str) -> str:
    """Return a version of the string in dot.case format."""
    return ".".join(map(lambda w: w.lower(), get_words(string)))


def to_kebab(string: str) -> str:
    """Return a version of the string in kebab-case format."""
    return "-".join(map(lambda w: w.lower(), get_words(string)))


def to_pascal(string: str) -> str:
    """Return a version of the string in PascalCase format."""
    preserve_upper = not string.isupper()
    return "".join(_capitalize(w, preserve_upper) for w in get_words(string))


def to_path(string: str) -> str:
    """Return a version of the string in path/case format."""
    return "/".join(map(lambda w: w.lower(), get_words(string)))


def to_snake(string: str) -> str:
    """Return a version of the string in snake_case format."""
    return "_".join(map(lambda w: w.lower(), get_words(string)))


def to_title(string: str) -> str:
    """Return a version of the string in Title Case format."""
    preserve_upper = not string.isupper()
    return " ".join(_capitalize(w, preserve_upper) for w in get_words(string))


def to_upper_dot(string: str) -> str:
    """Return a version of the string in UPPER.DOT.CASE format."""
    warnings.warn(
        f"to_upper_dot(...) is Deprecated. Use to_dot(...).upper() instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return ".".join(map(lambda w: w.upper(), get_words(string)))


def to_upper_kebab(string: str) -> str:
    """Return a version of the string in UPPER-KEBAB-CASE format."""
    warnings.warn(
        f"to_upper_kebab(...) is Deprecated. Use to_kebab(...).upper() instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return "-".join(map(lambda w: w.upper(), get_words(string)))


def to_upper_snake(string: str) -> str:
    """Return a version of the string in UPPER_SNAKE_CASE format."""
    warnings.warn(
        f"to_upper_snake(...) is Deprecated. Use to_snake(...).upper() instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return "_".join(map(lambda w: w.upper(), get_words(string)))


def get_words(string: str) -> list[str]:
    """Get a list of the words in a string in the order they appear."""
    words = [it for it in re.split(r"\b|_", string) if re.match(r"\w", it)]
    # Split on lower then upper: "oneTwo" -> ["one", "Two"]
    words = _split_words_on_regex(words, re.compile(r"(?<=[a-z])(?=[A-Z])"))
    # Split on upper then upper + lower: "JSONWord" -> ["JSON", "Word"]
    words = _split_words_on_regex(words, re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])"))
    # Split on number + letter: "TO1Cat23dog" -> ["TO1", "Cat23", "dog"]
    words = _split_words_on_regex(words, re.compile(r"(?<=\d)(?=[A-Za-z])"))
    return words


def _capitalize(word: str, preserve_upper: bool) -> str:
    return word if preserve_upper and word.isupper() else word.capitalize()


def _split_words_on_regex(words: list[str], regex: Union[re.Pattern, str]) -> list[str]:
    words = words.copy()
    for i, word in enumerate(words):
        split_words = re.split(regex, word)
        if len(split_words) > 1:
            words.pop(i)
            for j, sw in enumerate(split_words):
                words.insert(i + j, sw)
    return words
