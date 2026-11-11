import unittest

from delimited_number_parser import NumberParseError, parse_number


class TestParseNumber(unittest.TestCase):
    def test_plain_integer(self):
        self.assertEqual(parse_number("123"), 123)
        self.assertIsInstance(parse_number("123"), int)

    def test_plain_float(self):
        self.assertEqual(parse_number("123.45"), 123.45)
        self.assertIsInstance(parse_number("123.45"), float)

    def test_negative(self):
        self.assertEqual(parse_number("-123"), -123)
        self.assertEqual(parse_number("-123.45"), -123.45)
        self.assertEqual(parse_number("+123"), 123)

    def test_thousands_separator(self):
        self.assertEqual(parse_number("1,234"), 1234)
        self.assertEqual(parse_number("1,234,567"), 1234567)
        self.assertEqual(parse_number("12,345"), 12345)
        self.assertEqual(parse_number("123,456"), 123456)

    def test_thousands_and_decimal(self):
        self.assertEqual(parse_number("1,234.56"), 1234.56)
        self.assertEqual(parse_number("-1,234.56"), -1234.56)

    def test_european_style(self):
        self.assertEqual(parse_number("1.234,56", decimal_sep=",", thousands_sep="."), 1234.56)
        self.assertEqual(parse_number("1.234", decimal_sep=",", thousands_sep="."), 1234)
        self.assertEqual(parse_number("1,5", decimal_sep=",", thousands_sep="."), 1.5)

    def test_whitespace_is_stripped(self):
        self.assertEqual(parse_number("  1,234.56  "), 1234.56)

    def test_invalid_formats(self):
        for bad in ["", "   ", "abc", "1,23", "1,2345", "1,234.5.6", "1.2.3", "--1", "1,", ",1", "1,234,"]:
            with self.subTest(bad=bad):
                with self.assertRaises(NumberParseError):
                    parse_number(bad)

    def test_separator_validation(self):
        with self.assertRaises(NumberParseError):
            parse_number("1,234", decimal_sep=",,")
        with self.assertRaises(NumberParseError):
            parse_number("1,234", thousands_sep="..")
        with self.assertRaises(NumberParseError):
            parse_number("1,234", decimal_sep=",", thousands_sep=",")

    def test_non_string_input(self):
        with self.assertRaises(NumberParseError):
            parse_number(123)  # type: ignore[arg-type]

    def test_zero(self):
        self.assertEqual(parse_number("0"), 0)
        self.assertEqual(parse_number("0.0"), 0.0)
        self.assertEqual(parse_number("0,000.00"), 0.0)

    def test_large_number(self):
        self.assertEqual(parse_number("1,000,000,000,000"), 1_000_000_000_000)

    def test_decimal_without_integer_part_is_rejected(self):
        # We require at least one digit before the decimal separator.
        with self.assertRaises(NumberParseError):
            parse_number(".5")

    def test_sign_only_is_rejected(self):
        with self.assertRaises(NumberParseError):
            parse_number("-")
        with self.assertRaises(NumberParseError):
            parse_number("+")


if __name__ == "__main__":
    unittest.main()
