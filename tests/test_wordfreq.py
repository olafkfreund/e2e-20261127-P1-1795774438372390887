"""Tests for the wordfreq package: counting, formatting, and the CLI."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_count_words_breaks_ties_alphabetically() -> None:
    # "pear" and "fig" both appear twice; "apple" and "banana" once each.
    text = "pear fig apple fig pear banana"
    assert count_words(text) == [
        ("fig", 2),
        ("pear", 2),
        ("apple", 1),
        ("banana", 1),
    ]


def test_count_words_tie_order_ignores_input_order() -> None:
    forward = "zeta alpha mu alpha zeta"
    backward = " ".join(reversed(forward.split()))
    assert count_words(forward) == count_words(backward)


def test_count_words_top_keeps_alphabetical_tie_winners() -> None:
    assert count_words("pear fig apple fig pear banana", top=2) == [
        ("fig", 2),
        ("pear", 2),
    ]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Apple APPLE apple") == [("apple", 3)]


def test_count_words_ignore_case_false_keeps_case_distinct() -> None:
    assert count_words("Apple apple", ignore_case=False) == [
        ("Apple", 1),
        ("apple", 1),
    ]


def test_count_words_tokens_are_ascii_alphanumeric_runs() -> None:
    assert count_words("snake_case x2y") == [("case", 1), ("snake", 1), ("x2y", 1)]


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a bb ccc bb", min_len=2) == [("bb", 2), ("ccc", 1)]


def test_count_words_rejects_min_len_below_one() -> None:
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words("text", min_len=0)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words("text", top=-1)


def test_count_words_top_zero_returns_no_rows() -> None:
    assert count_words("a b", top=0) == []


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


def test_cli_breaks_ties_alphabetically(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("pear fig apple fig pear banana", encoding="utf-8")
    assert main([str(sample), "--top", "2"]) == 0
    assert capsys.readouterr().out == "fig\t2\npear\t2\n"


def test_cli_case_sensitive_flag_keeps_case_distinct(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple APPLE apple", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t4\n"
    assert main([str(sample), "--case-sensitive"]) == 0
    assert capsys.readouterr().out == "apple\t2\nAPPLE\t1\nApple\t1\n"


@pytest.mark.parametrize("argv", [[], ["-"]])
def test_cli_reads_stdin_by_default_or_with_dash(
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("red green red\n"))
    assert main(argv) == 0
    assert capsys.readouterr().out == "red\t2\ngreen\t1\n"


def test_cli_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("b a b", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "b\t2\na\t1\n"


def test_cli_empty_tsv_output_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "empty.txt"
    sample.write_text("", encoding="utf-8")
    assert main([str(sample)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_json_output_is_list_of_objects_with_trailing_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("b a b", encoding="utf-8")
    assert main([str(sample), "--json"]) == 0
    expected = '[{"word": "b", "count": 2}, {"word": "a", "count": 1}]\n'
    assert capsys.readouterr().out == expected


def test_cli_json_empty_input_prints_empty_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "empty.txt"
    sample.write_text("", encoding="utf-8")
    assert main([str(sample), "--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


@pytest.mark.parametrize(
    ("extra_args", "message"),
    [
        (["--min-len", "0"], "min_len must be >= 1"),
        (["--top", "-1"], "top must be >= 0"),
    ],
)
def test_cli_rejects_out_of_range_options(
    extra_args: list[str],
    message: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("a b", encoding="utf-8")
    assert main([str(sample), *extra_args]) == 2
    captured = capsys.readouterr()
    assert message in captured.err
    assert captured.out == ""


@pytest.mark.parametrize("extra_args", [["--top", "many"], ["--min-len", "x"]])
def test_cli_rejects_non_integer_options(
    extra_args: list[str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("a b", encoding="utf-8")
    assert main([str(sample), *extra_args]) == 2
    captured = capsys.readouterr()
    assert captured.err != ""
    assert captured.out == ""


def test_cli_missing_file_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("wordfreq: error: cannot read ")
    assert str(missing) in captured.err


def test_cli_directory_path_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(tmp_path)]) == 2
    assert capsys.readouterr().err != ""


def test_cli_invalid_utf8_input_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "binary.txt"
    sample.write_bytes(b"\xff\xfe\xfd")
    assert main([str(sample)]) == 2
    assert capsys.readouterr().err != ""


def test_python_m_wordfreq_reads_stdin() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq"],
        input="b a b\n",
        capture_output=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "b\t2\na\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_missing_file_returns_2(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", str(missing)],
        capture_output=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""
