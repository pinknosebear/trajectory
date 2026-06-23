import math

from calculations import composite_score, gmi, pearson_r, percent_delta, time_in_range


def test_gmi_formula():
    assert gmi(154) == 3.31 + 0.02392 * 154


def test_time_in_range():
    assert time_in_range([65, 70, 100, 180, 181]) == 60


def test_percent_delta_zero_and_missing_prior():
    assert percent_delta(10, 0) is None
    assert percent_delta(10, None) is None
    assert percent_delta(90, 100) == -10


def test_composite_score_excludes_missing_values():
    assert composite_score([80, None, 70]) == 75
    assert composite_score([None]) is None


def test_pearson_correlation():
    assert math.isclose(pearson_r([1, 2, 3], [2, 4, 6]), 1)
    assert math.isclose(pearson_r([1, 2, 3], [6, 4, 2]), -1)
    assert pearson_r([1, 1, 1], [2, 3, 4]) is None
