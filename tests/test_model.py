import pytest
from dividend_portfolio.model import Holding, gross_yield, normalize_weights, tax_waterfall, weight_total


def sample():
    return [Holding("A", "A", "x", .6, .05, "x"), Holding("B", "B", "x", .4, .10, "y")]


def test_normalization_and_yield():
    hs = sample()
    assert normalize_weights(hs) == [.6, .4]
    assert gross_yield(hs, [.6, .4]) == pytest.approx(.07)


def test_normalization_fixes_overweight_scenario():
    hs = [Holding("A", "A", "x", .7, .05, "x"), Holding("B", "B", "x", .5, .10, "y")]
    assert sum(normalize_weights(hs)) == pytest.approx(1.0)


def test_tax_credit_cannot_exceed_assessed_tax():
    result = tax_waterfall(100, us_withholding=.30, sa_rate=.20)
    assert result["foreign_tax_credit"] == 20
    assert result["residual_sa"] == 0
    assert result["final_cash"] == 70


def test_narrative_total_is_102_percent():
    assert weight_total([Holding("A", "A", "x", .7, .05, "x"), Holding("B", "B", "x", .32, .1, "y")]) == pytest.approx(1.02)
