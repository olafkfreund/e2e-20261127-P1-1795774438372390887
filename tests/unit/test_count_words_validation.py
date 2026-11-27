# AC#1: count_words raises ValueError("min_len must be >= 1") when min_len < 1,
# or ValueError("top must be >= 0") when top < 0.

import pytest

from wordfreq.cli import _validate_options


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -10],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_ten"],
)
def test_validate_options_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError) as excinfo:
        _validate_options(min_len=min_len, top=10)
    assert str(excinfo.value) == "min_len must be >= 1"


@pytest.mark.parametrize(
    "top",
    [-1, -100],
    ids=["top_minus_one", "top_minus_hundred"],
)
def test_validate_options_top_below_zero_raises_value_error(top):
    with pytest.raises(ValueError) as excinfo:
        _validate_options(min_len=1, top=top)
    assert str(excinfo.value) == "top must be >= 0"
