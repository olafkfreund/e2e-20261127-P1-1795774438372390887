# AC#3: `main` terminates non-empty TSV and --json output with a final \n,
# writing nothing for empty TSV output.

import io
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def run_main(monkeypatch, capsys):
    def _run(stdin_text, argv):
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_text))
        code = main(argv)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param([], id="tsv-default"),
        pytest.param(["--top", "2"], id="tsv-top-2"),
        pytest.param(["--case-sensitive"], id="tsv-case-sensitive"),
    ],
)
def test_main_tsv_output_nonempty_ends_with_newline(run_main, argv):
    code, out, _ = run_main("the cat the dog\n", argv)
    assert out.endswith("\n")


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["--json"], id="json-default"),
        pytest.param(["--json", "--top", "1"], id="json-top-1"),
    ],
)
def test_main_json_output_ends_with_single_newline(run_main, argv):
    code, out, _ = run_main("the cat the dog\n", argv)
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_main_tsv_empty_input_writes_nothing(run_main):
    code, out, _ = run_main("", [])
    assert out == ""


def test_main_tsv_empty_input_returns_zero(run_main):
    code, out, _ = run_main("", [])
    assert code == 0
