"""Delimited Number Parser: parse locale-formatted number strings into numbers.

Public API:
    parse_number(text, *, decimal_sep='.', thousands_sep=',') -> int | float
    NumberParseError
"""

from .core import NumberParseError, parse_number

__all__ = ["parse_number", "NumberParseError"]
