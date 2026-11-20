# delimited_number_parser

Parse strings containing numbers with locale-specific thousands separators and decimal markers into numeric values.

```python
from delimited_number_parser import parse_number

parse_number("1,234.56")                      # 1234.56
parse_number("1.234,56", decimal_sep=",", thousands_sep=".")  # 1234.56
parse_number("1,234")                          # 1234 (int)
```

## Why this exists

Parsing user-entered numbers is fiddly because the same string means different
things in different locales. `"1,234"` is one thousand two hundred thirty-four in
en-US but one point two three four in de-DE. Rather than guess, this library makes
the separators explicit arguments. The trade-off is that callers must know their
locale; the benefit is that the behaviour is never ambiguous and never depends on
the host machine's locale settings.

## The awkward edge

A string with no decimal separator is returned as an `int`, and a string with one
is returned as a `float`. This means `parse_number("1,234")` gives `1234` while
`parse_number("1,234.0")` gives `1234.0`. If you need a consistent type, convert
the result yourself.

## API

### `parse_number(text, *, decimal_sep='.', thousands_sep=',')

Returns an `int` or `float`. Raises `NumberParseError` (a subclass of
`ValueError`) for malformed input, non-string input, or invalid separators.

### `NumberParseError`

Raised when parsing fails.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

