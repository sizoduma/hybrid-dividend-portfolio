# Hybrid Dividend Portfolio

A reproducible, auditable Python model for the supplied **$23 million Hybrid Expanded Dividend Strategy**, with a local evidence/RAG scaffold for refreshing market, fund, issuer, and tax assumptions.

> **Important:** This is research software, not investment, legal, or tax advice. The scenario data is transcribed from the supplied narrative and is not live data. Validate every yield, distribution, credit claim, treaty assumption, MLP tax treatment, and South African tax conclusion with current primary sources and qualified advisers before investing.

## What this repository does

- Represents every holding, target weight, yield, category, and strategic role in a versioned CSV.
- Reconciles the narrative's capital, weights, and income calculations.
- Detects the narrative's **102% weight inconsistency** rather than silently hiding it.
- Provides three transparent views:
  1. **Narrative view**: preserves the supplied weights and shows the resulting $23.46m implied investment.
  2. **Normalized view**: scales the supplied weights to 100% so they can be invested with exactly $23m.
  3. **Constrained optimizer**: maximizes stated gross yield subject to explicit, inspectable concentration and sleeve constraints. This is a yield optimizer, not a risk optimizer.
- Calculates a clearly labeled illustrative US-withholding / South African tax waterfall.
- Provides a deterministic local keyword RAG retriever over dated evidence notes. An LLM may explain retrieved evidence, but it must not invent missing facts.
- Includes tests for arithmetic, validation, tax credit treatment, and retrieval.

## Quick start

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'

python -m dividend_portfolio --view all
pytest
```

If you do not want the package install, run:

```bash
PYTHONPATH=src python -m dividend_portfolio --view normalized
```

## Examples

```bash
# Show the uninvestable narrative exactly as supplied and flag its 102% total
python -m dividend_portfolio --view narrative

# Scale the scenario to a $23m investable portfolio
python -m dividend_portfolio --view normalized --csv-output outputs/normalized.csv

# Solve the stated yield maximization problem
python -m dividend_portfolio --view optimized

# Retrieve local evidence before asking an LLM a research question
python -m dividend_portfolio.rag "What must be verified about EPD tax treatment?"
```

The optimizer uses SciPy when installed. Without SciPy, narrative and normalized
views still work; the CLI reports that the optional optimizer dependency is missing.

## Source hierarchy and RAG guardrails

Put dated documents or notes under `evidence/`. Prefer, in order:

1. issuer filings and investor-relations releases;
2. fund prospectuses and official fact sheets;
3. IRS and SARS publications;
4. broker statements and tax reports;
5. reputable secondary research, clearly labeled as secondary.

The RAG layer is intentionally conservative: it returns passages and metadata,
not an answer masquerading as verified advice. Every LLM prompt should require:
source citations, an as-of date, separation of fact/assumption/inference, and an
`UNKNOWN` label when the evidence is absent. Never place account numbers,
identity documents, or other personal information in evidence files or prompts.

## Key caveats discovered in the narrative

- The listed weights total **102%**, implying $23.46m when applied to $23m.
- The listed income figures are therefore not directly comparable with a fully
  invested $23m portfolio unless the weights are normalized or capital is changed.
- EPD is an MLP: K-1, state filing, withholding, UBTI/ECI, and account-type
  implications require specialist review.
- REIT, partnership, ordinary-dividend, qualified-dividend, and return-of-capital
  tax character can differ; a flat rate is not a tax determination.
- A 15% US treaty withholding assumption requires valid documentation and may not
  apply identically to every distribution type.
- Yields, credit ratings, payout ratios, dividend streaks, and GPC corporate
  actions are time-sensitive and must be refreshed.

See `docs/methodology.md` for the formulas, assumptions, and interpretation.
