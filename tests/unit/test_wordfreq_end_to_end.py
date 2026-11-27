# Criterion (AC#4): Verify the CLI end to end through main on a mixed-case
# sample so the suite in tests/test_wordfreq.py has a consistent baseline.
# pytest -q passes across tests/test_wordfreq.py.

import pytest

from wordfreq.cli import main


MIXED_CASE_SAMPLE = "The quick Brown fox. the QUICK brown Fox, THE end.\n"


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text(MIXED_CASE_SAMPLE, encoding="utf-8")
    return path


def test_main_mixed_case_sample_exits_zero(sample_file):
    exit_code = main([str(sample_file)])
    assert (exit_code or 0) == 0


def test_main_mixed_case_sample_produces_output(sample_file, capsys):
    main([str(sample_file)])
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_main_mixed_case_sample_no_stderr(sample_file, capsys):
    main([str(sample_file)])
    captured = capsys.readouterr()
    assert captured.err == ""
