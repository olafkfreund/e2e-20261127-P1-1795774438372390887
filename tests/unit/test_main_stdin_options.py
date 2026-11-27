# AC#3: main reads sys.stdin by default or '-', honors --case-sensitive, --top, --min-len; returns 0
#
# Subtask: main-stdin-and-options
# Verify main reads stdin by default or when path is '-', honors --case-sensitive,
# --top and --min-len, and returns 0 with TSV ending in a newline.

import io
import sys

import pytest

from wordfreq.cli import main


STDIN_TEXT = "The the THE cat cat dog a an apple apple apple\n"


@pytest.fixture
def stdin_text(monkeypatch):
    """Replace sys.stdin with an in-memory stream holding STDIN_TEXT."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(STDIN_TEXT))
    return STDIN_TEXT


def _data_lines(output):
    return [line for line in output.splitlines() if line.strip()]


def test_main_reads_stdin_by_default_returns_zero(stdin_text, capsys):
    rc = main([])
    assert rc == 0


def test_main_reads_stdin_by_default_outputs_words(stdin_text, capsys):
    main([])
    out = capsys.readouterr().out
    assert "apple" in out


def test_main_reads_stdin_when_path_is_dash_returns_zero(stdin_text, capsys):
    rc = main(["-"])
    assert rc == 0


def test_main_reads_stdin_when_path_is_dash_outputs_words(stdin_text, capsys):
    main(["-"])
    out = capsys.readouterr().out
    assert "apple" in out


def test_main_case_sensitive_counts_capitalisation_separately(stdin_text, capsys):
    main(["--case-sensitive"])
    out = capsys.readouterr().out
    words = [line.split("\t")[0] for line in _data_lines(out)]
    assert "The" in words and "the" in words


def test_main_default_case_folding_merges_capitalisation(stdin_text, capsys):
    main([])
    out = capsys.readouterr().out
    words = [line.split("\t")[0] for line in _data_lines(out)]
    assert words.count("the") == 1 and "The" not in words


def test_main_top_limits_output_to_one_row(stdin_text, capsys):
    main(["--top", "1"])
    out = capsys.readouterr().out
    assert len(_data_lines(out)) == 1


def test_main_top_limits_output_to_two_rows(stdin_text, capsys):
    main(["--top", "2"])
    out = capsys.readouterr().out
    assert len(_data_lines(out)) == 2


def test_main_min_len_excludes_short_words(stdin_text, capsys):
    main(["--min-len", "4"])
    out = capsys.readouterr().out
    words = [line.split("\t")[0] for line in _data_lines(out)]
    assert "cat" not in words and "dog" not in words and "a" not in words


def test_main_min_len_keeps_words_meeting_threshold(stdin_text, capsys):
    main(["--min-len", "4"])
    out = capsys.readouterr().out
    words = [line.split("\t")[0] for line in _data_lines(out)]
    assert "apple" in words


def test_main_output_ends_with_newline(stdin_text, capsys):
    main([])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_output_is_tab_separated(stdin_text, capsys):
    main([])
    out = capsys.readouterr().out
    assert all("\t" in line for line in _data_lines(out))
