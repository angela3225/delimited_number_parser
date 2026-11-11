"""Core parsing logic for locale-formatted numbers.

Design decisions:
- We accept an explicit thousands separator and decimal separator. This avoids
  guessing and keeps the library predictable. Callers who want locale detection
  can layer it on top.
- A string with no decimal separator is returned as int. A string with a decimal
  separator is returned as float. This matches how Python's int() and float()
  behave and avoids surprising type changes.
- The thousands separator is only allowed between groups of exactly three digits
  in the integer part, with the first group being one to three digits. This is
  the common convention for en-US, de-DE, and many others. We do not accept
  Indian grouping (e.g. 1,00,000) because it would require a separate rule and
  the brief asks for one clear interpretation.
- Leading and trailing whitespace is stripped. Internal whitespace is an error.
- A leading sign is allowed. A trailing sign is not.
"""

from __future__ import annotations

import re


class NumberParseError(ValueError):
    """Raised when a string cannot be parsed as a delimited number."""


# Matches an optional sign, then either:
#   - a plain integer: \d+
#   - a grouped integer: \d{1,3}(?:<thousands>\d{3})+
#   - the above followed by <decimal><digits>
# We build the pattern dynamically because the separators are configurable.
def _build_pattern(thousands_sep: str, decimal_sep: str) -> re.Pattern[str]:
    # Escape separators so that regex metacharacters are treated literally.
    t = re.escape(thousands_sep)
    d = re.escape(decimal_sep)
    integer = rf"(?:\d+|\d{{1,3}}(?:{t}\d{{3}})+)"
    number = rf"[+-]?{integer}(?:{d}\d+)?"
    return re.compile(rf"^{number}$")


def parse_number(
    text: str,
    *,
    decimal_sep: str = ".",
    thousands_sep: str = ",",
) -> int | float:
    """Parse *text* as a number using the given separators.

    Args:
        text: The string to parse. Leading/trailing whitespace is ignored.
        decimal_sep: The character that separates the fractional part.
        thousands_sep: The character that groups the integer part.

    Returns:
        An ``int`` if *text* contains no decimal separator, otherwise a ``float``.

    Raises:
        NumberParseError: If *text* is not a valid delimited number, or if the
            separators are not single characters, or if they are equal.
    """
    if not isinstance(text, str):
        raise NumberParseError(f"expected str, got {type(text).__name__}")
    if len(decimal_sep) != 1 or len(thousands_sep) != 1:
        raise NumberParseError("separators must be single characters")
    if decimal_sep == thousands_sep:
        raise NumberParseError("decimal and thousands separators must differ")

    stripped = text.strip()
    if not stripped:
        raise NumberParseError("empty string")

    pattern = _build_pattern(thousands_sep, decimal_sep)
    if not pattern.match(stripped):
        raise NumberParseError(f"invalid number format: {text!r}")

    # Normalise to a form Python's int()/float() understand.
    normalised = stripped
    if thousands_sep in normalised:
        normalised = normalised.replace(thousands_sep, "")

    if decimal_sep in normalised:
        # Replace the locale decimal separator with '.', which float() accepts.
        normalised = normalised.replace(decimal_sep, ".")
        try:
            return float(normalised)
        except ValueError as exc:  # pragma: no cover - pattern should prevent this
            raise NumberParseError(f"invalid number format: {text!r}") from exc

    try:
        return int(normalised)
    except ValueError as exc:  # pragma: no cover - pattern should prevent this
        raise NumberParseError(f"invalid number format: {text!r}") from exc
