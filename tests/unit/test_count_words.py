# Acceptance criterion (AC#1): count_words extracts tokens, lowercases by default,
# preserves case when ignore_case=False, filters by min_len, sorts by (-count, word)
# and applies top.
#
# Subtask: count-words-tokenize-sort
# Target:  wordfreq/cli.py::count_words

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alphanumeric_tokens_only():
    text = "hello, world! 42 foo_bar"

    result = count_words(text)

    words = {word for word, _ in result}
    assert words == {"hello", "world", "42", "foo", "bar"}


def test_count_words_default_lowercases_tokens():
    text = "Hello HELLO hello"

    result = count_words(text)

    assert result == [("hello", 3)]


def test_count_words_ignore_case_false_preserves_case():
    text = "Hello hello HELLO"

    result = count_words(text, ignore_case=False)

    counts = dict(result)
    assert counts == {"Hello": 1, "hello": 1, "HELLO": 1}


@pytest.mark.parametrize(
    "min_len,expected_words",
    [
        (1, {"a", "bb", "ccc"}),
        (2, {"bb", "ccc"}),
        (3, {"ccc"}),
    ],
    ids=["min_len_1_keeps_all", "min_len_2_drops_single_char", "min_len_3_keeps_only_longest"],
)
def test_count_words_min_len_filters_short_tokens(min_len, expected_words):
    text = "a bb ccc"

    result = count_words(text, min_len=min_len)

    words = {word for word, _ in result}
    assert words == expected_words


def test_count_words_sorts_by_descending_count_then_word():
    text = "b a b c c"

    result = count_words(text)

    assert result == [("b", 2), ("c", 2), ("a", 1)]


def test_count_words_sort_ties_broken_alphabetically():
    text = "zeta alpha mid"

    result = count_words(text)

    assert [word for word, _ in result] == ["alpha", "mid", "zeta"]


def test_count_words_top_limits_result_to_first_n_entries():
    text = "b a b c c d d d"

    result = count_words(text, top=2)

    assert result == [("d", 3), ("b", 2)]
