# AC#3: main and `python -m wordfreq` read from sys.stdin by default when no
# path argument is given (or when path is "-"), terminate non-empty TSV output
# with a final "\n", return 0 on success, and return 2 with non-empty stderr
# on missing files.

import io
import subprocess
import sys
from pathlib import Path

import pytest

import wordfreq
from wordfreq.cli import main


PIPED_INPUT = "b a b c a b\n"
EXPECTED_TSV = "b\t3\na\t2\nc\t1\n"
PROJECT_ROOT = Path(wordfreq.__file__).resolve().parent.parent


def test_python_m_wordfreq_piped_stdin_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq"],
        input=PIPED_INPUT,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0


def test_python_m_wordfreq_piped_stdin_prints_ranked_tsv():
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq"],
        input=PIPED_INPUT,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PROJECT_ROOT,
    )
    assert result.stdout == EXPECTED_TSV


def test_python_m_wordfreq_missing_file_exits_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", str(missing)],
        input="",
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 2


def test_python_m_wordfreq_missing_file_writes_stderr(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", str(missing)],
        input="",
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PROJECT_ROOT,
    )
    assert result.stderr != ""


def test_main_default_reads_sys_stdin_returns_zero(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(PIPED_INPUT))
    assert main([]) == 0


def test_main_default_reads_sys_stdin_prints_ranked_tsv(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(PIPED_INPUT))
    main([])
    assert capsys.readouterr().out == EXPECTED_TSV


def test_main_dash_path_reads_sys_stdin_prints_ranked_tsv(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(PIPED_INPUT))
    main(["-"])
    assert capsys.readouterr().out == EXPECTED_TSV


def test_main_missing_file_returns_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    assert main([str(missing)]) == 2


def test_main_missing_file_writes_non_empty_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    main([str(missing)])
    assert capsys.readouterr().err != ""
