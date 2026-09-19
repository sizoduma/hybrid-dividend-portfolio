"""Core portfolio calculations.

The model deliberately keeps scenario assumptions separate from verified market
data. Percentages are decimal fractions (0.15 = 15%).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Iterable


@dataclass(frozen=True)
class Holding:
    ticker: str
    name: str
    category: str
    target_weight: float
    forward_yield: float
    role: str


def load_holdings(path: str | Path) -> list[Holding]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [Holding(row["ticker"], row["name"], row["category"],
                        float(row["target_weight"]), float(row["forward_yield"]),
                        row["role"]) for row in csv.DictReader(handle)]


def weight_total(holdings: Iterable[Holding]) -> float:
    return sum(h.target_weight for h in holdings)


def validate_investable(holdings: Iterable[Holding], tolerance: float = 1e-9) -> None:
    total = weight_total(holdings)
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Weights total {total:.4%}; an investable portfolio must total 100%.")


def normalize_weights(holdings: list[Holding]) -> list[float]:
    total = weight_total(holdings)
    if total <= 0:
        raise ValueError("Weight total must be positive")
    return [h.target_weight / total for h in holdings]


def gross_yield(holdings: list[Holding], weights: list[float]) -> float:
    return sum(h.forward_yield * weight for h, weight in zip(holdings, weights))


def tax_waterfall(gross_income: float, us_withholding: float = .15,
                  sa_rate: float = .20) -> dict[str, float]:
    """Illustrative waterfall with a foreign-tax-credit floor at zero.

    This does not determine legal tax liability. It applies the user's simplified
    assumption: SA tax equals gross income * sa_rate and US withholding is a
    credit limited to that SA amount.
    """
    us_tax = gross_income * us_withholding
    sa_assessed = gross_income * sa_rate
    credit = min(us_tax, sa_assessed)
    residual_sa = max(sa_assessed - credit, 0.0)
    return {"gross": gross_income, "us_withholding": us_tax,
            "sa_assessed": sa_assessed, "foreign_tax_credit": credit,
            "residual_sa": residual_sa,
            "final_cash": gross_income - us_tax - residual_sa}


def optimize_weights(holdings: list[Holding]) -> list[float]:
    """Maximize stated yield under explicit, simple policy constraints.

    Constraints: long-only; each position 0.25%-10%; SCHD 10%-20%; CASH 3%-8%;
    MO <= 8%; real assets EPD/O/ENB 20%-30%; Kings 40%-60%. This is not a
    mean-variance, drawdown, liquidity, or tax-aware optimizer.
    """
    try:
        from scipy.optimize import linprog
    except ImportError as exc:
        raise RuntimeError("Install scipy for --view optimized") from exc
    n = len(holdings)
    ix = {h.ticker: i for i, h in enumerate(holdings)}
    bounds = [(0.0025, 0.10)] * n
    bounds[ix["SCHD"]] = (0.10, 0.20)
    bounds[ix["CASH"]] = (0.03, 0.08)
    bounds[ix["MO"]] = (0.0025, 0.08)
    real = {"EPD", "O", "ENB"}
    kings = {"MO", "FRT", "NWN", "KMB", "JNJ", "DOV", "EMR", "PH", "NDSN", "HTO", "PG", "KO"}
    def indicator(group): return [1.0 if h.ticker in group else 0.0 for h in holdings]
    real_i, king_i = indicator(real), indicator(kings)
    result = linprog([-h.forward_yield for h in holdings],
        A_ub=[real_i, [-x for x in real_i], king_i, [-x for x in king_i]],
        b_ub=[.30, -.20, .60, -.40], A_eq=[[1.0] * n], b_eq=[1.0],
        bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    return list(result.x)
