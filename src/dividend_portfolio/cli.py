from __future__ import annotations

import argparse
import csv
from pathlib import Path
from .model import load_holdings, normalize_weights, optimize_weights, gross_yield, tax_waterfall

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "holdings.csv"


def print_view(name, holdings, weights, capital, withholding, sa_rate):
    income = capital * gross_yield(holdings, weights)
    tax = tax_waterfall(income, withholding, sa_rate)
    print(f"\n{name.upper()} VIEW")
    print(f"Weight total: {sum(weights):.4%}")
    print(f"Capital represented: ${capital * sum(weights):,.0f}")
    print(f"Blended gross yield: {income / (capital * sum(weights)):.2%}")
    print(f"Gross income: ${income:,.0f} (${income/12:,.0f}/month)")
    print(f"US withholding assumption: ${tax['us_withholding']:,.0f}")
    print(f"Residual SA tax assumption: ${tax['residual_sa']:,.0f}")
    print(f"Illustrative final cash: ${tax['final_cash']:,.0f} (${tax['final_cash']/12:,.0f}/month)")
    print("\nTicker  Weight  Allocation  Yield  Gross income  Role")
    for h, w in zip(holdings, weights):
        print(f"{h.ticker:5} {w:7.2%} ${capital*w:11,.0f} {h.forward_yield:6.2%} ${capital*w*h.forward_yield:12,.0f}  {h.role}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hybrid dividend portfolio scenario model")
    parser.add_argument("--capital", type=float, default=23_000_000)
    parser.add_argument("--view", choices=["narrative", "normalized", "optimized", "all"], default="all")
    parser.add_argument("--withholding", type=float, default=.15)
    parser.add_argument("--sa-rate", type=float, default=.20)
    parser.add_argument("--csv-output", type=Path)
    args = parser.parse_args(argv)
    holdings = load_holdings(DATA)
    views = []
    if args.view in ("narrative", "all"):
        views.append(("narrative", [h.target_weight for h in holdings]))
    if args.view in ("normalized", "all"):
        views.append(("normalized", normalize_weights(holdings)))
    if args.view in ("optimized", "all"):
        try:
            views.append(("optimized", optimize_weights(holdings)))
        except RuntimeError as error:
            print(f"Optimizer unavailable: {error}")
    for name, weights in views:
        print_view(name, holdings, weights, args.capital, args.withholding, args.sa_rate)
    if args.csv_output and views:
        name, weights = views[-1]
        with args.csv_output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["view", "ticker", "weight", "allocation", "forward_yield", "gross_income"])
            for h, w in zip(holdings, weights):
                writer.writerow([name, h.ticker, w, args.capital*w, h.forward_yield, args.capital*w*h.forward_yield])


if __name__ == "__main__":
    main()
