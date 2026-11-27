# AC#2: format_table formats (word, count) rows as word\tcount lines separated by \n
# and returns "" for empty input.

from wordfreq.cli import format_table


def test_format_table_multiple_rows_joined_with_newline_and_tab_separated():
    rows = [("apple", 3), ("banana", 1)]

    result = format_table(rows)

    assert result == "apple\t3\nbanana\t1"


def test_format_table_multiple_rows_has_no_trailing_newline():
    rows = [("apple", 3), ("banana", 1)]

    result = format_table(rows)

    assert not result.endswith("\n")


def test_format_table_empty_input_returns_empty_string():
    result = format_table([])

    assert result == ""
