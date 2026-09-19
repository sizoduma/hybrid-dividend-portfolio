# Methodology and implementation notes

## Portfolio arithmetic

For holding *i*:

- allocation = capital × weight
- annual gross income = allocation × forward yield
- blended yield = Σ(weight × forward yield)

The narrative's target weights total 102%. At $23m, preserving those weights
represents $23.46m, not $23m. The normalized view divides every weight by 1.02.
This changes the dollar allocation and income, so it must not be presented as the
same portfolio. The narrative view is retained for reconciliation.

## Tax scenario

The illustrative waterfall is:

1. gross income = model income;
2. US withholding = gross income × assumed 15%;
3. SA assessed amount = gross income × assumed 20%;
4. foreign-tax credit = min(US withholding, SA assessed amount);
5. residual SA amount = max(SA assessed amount − credit, 0);
6. final cash = gross income − US withholding − residual SA amount.

This is only the supplied simplified scenario. It does not calculate tax law.
Distribution character, treaty eligibility, forms, ECI/K-1 obligations, tax
residency, deductions, exemptions, rebates, exchange rates, and timing can all
change the result. Obtain a South African and US cross-border tax review.

## Optimizer

The optional linear program maximizes stated forward yield subject to:

- long-only positions;
- each position between 0.25% and 10%;
- SCHD between 10% and 20%;
- cash between 3% and 8%;
- MO no greater than 8%;
- EPD/O/ENB between 20% and 30%;
- the named Kings sleeve between 40% and 60%.

These are policy constraints, not estimated risk. There is no covariance matrix,
drawdown control, valuation model, liquidity model, currency hedge, inflation
model, ESG score, or tax-aware objective. A professional version should add
scenario returns, volatility, correlations, stress tests, turnover, bid/ask
costs, tax lots, and minimum cash-flow requirements.

## RAG/LLM protocol

1. Ingest only dated, permissioned source notes.
2. Retrieve the top passages using `rag.py`.
3. Ask the LLM to quote/cite the passage and provide an as-of date.
4. Require separate sections: verified fact, scenario assumption, inference,
   uncertainty, and action for human review.
5. Reject unsupported claims and label them `UNKNOWN`.
6. Re-run the model when a yield, distribution, filing, or tax rule changes.
