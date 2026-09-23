# Code and manuscript readiness review

Repository reviewed: `DeckardShaw31/Eureka-2026`, branch `main`  
Review date: 2026-09-23

## Overall verdict

The repository is well structured and substantially follows `design.md`. The data folders, manifests, processed panels, diagnostics, model scripts, tests, tables, and figures are all present. The manuscript can be started for the introduction, literature review, data description, and provisional methods.

The empirical results are **not yet manuscript-ready**. Several issues below can change coefficients, standard errors, and the conclusions assigned to H2--H4. The current README and `summary_findings.json` should therefore be treated as provisional rather than as validated findings.

## Blocking issues

### 1. Missing Vietnam 2024 Comtrade data are converted to zero

Severity: **Critical**

Relevant code:

- `src/build_bilateral_panel.py`, lines 46--49: every unmatched Comtrade observation is filled with `0.0`.
- `outputs/diagnostics/source_comparison.csv`: Vietnam 2024 has Comtrade exports of `0.0`, while ASEANstats reports approximately USD 403.24 billion.

This is not a genuine zero-trade observation. It is a missing reporter-year extract. Consequently, about 24 Vietnam--partner observations in 2024 are incorrectly entered as zero and included in PPML.

Required correction:

1. Re-download Vietnam bilateral exports for 2024.
2. Add a reporter-year coverage table before creating the balanced grid.
3. Distinguish three states:
   - observed positive trade;
   - confirmed reported zero;
   - missing/unavailable record.
4. Do not fill unmatched rows with zero unless the reporter-year query is known to be complete.
5. Make validation fail if a reporter-year has partner coverage below a predetermined threshold.

Suggested fields:

```text
trade_usd_raw
trade_observed
reporter_year_complete
zero_trade_confirmed
missing_reason
```

### 2. The full structural-gravity specification is not estimated

Severity: **Critical**

The design specified:

\[
E(X_{ijt}) = \exp[\beta\ln(LSBCI_{ijt}) + \delta_{ij} + \alpha_{it} + \gamma_{jt}].
\]

This requires all three sets of fixed effects:

- country-pair fixed effects;
- exporter-year fixed effects;
- importer-year fixed effects.

None of G1--G5 contains all three simultaneously. G1 has pair and year effects only. G3 and G4 contain only one side of the country-year effects and omit pair effects.

Required correction:

```python
trade_million ~ ln_lsbci + C(pair_id) + C(exporter_year) + C(importer_year)
```

This specification should be the main gravity result. G1 can remain as a simpler comparison. The current claim that the analysis implements a structural gravity model is too strong until this model has been estimated and checked for convergence/separation.

### 3. The significant placebo result contradicts a causal interpretation

Severity: **Critical for interpretation**

The future value of LSCI has a coefficient of approximately `1.000` with reported `p < 0.001`. A future explanatory variable strongly predicting current exports indicates persistent trends, reverse causality, omitted variables, or an invalid placebo design.

The result must not be presented as a successful robustness test. At present it weakens claims that LSCI itself causes export growth.

Required correction:

- Present the study as associational unless a credible identification design is added.
- Add country-specific linear trends as a sensitivity test.
- Consider first-difference or growth specifications.
- Test multiple leads and lags rather than interpreting one lead in isolation.
- State explicitly that lagging LSCI does not by itself solve endogeneity.

### 4. Inference is unreliable with only 9 country clusters

Severity: **High**

Country-panel standard errors are clustered by country, but there are only nine clusters. The CLMV subgroup has only three countries. Default cluster-robust normal approximations can substantially overstate significance with so few clusters.

Required correction:

- Report the number of clusters prominently.
- Use small-sample cluster inference where supported (`use_t=True` and finite-sample correction).
- Prefer a wild cluster bootstrap for the key LSCI and interaction coefficients.
- Treat the three-country CLMV-only regression as descriptive, not confirmatory.
- Do not print `p = 0.0000`; use `p < 0.001`.

### 5. H3 is not robust across the repository's own specifications

Severity: **High**

M5 reports a positive interaction of about `0.660`. However, separate subgroup models report an LSCI coefficient around `0.309` for ASEAN-6 and `0.131` for coastal CLMV. Those subgroup estimates do not support the simple statement that the CLMV elasticity is larger.

The interaction model and subgroup models are not identical estimands, but the apparent contradiction must be investigated rather than marking H3 as “confirmed.”

Required correction:

- Calculate and report the total CLMV marginal effect: `beta_lsci + beta_interaction`.
- Test that linear combination directly.
- Plot marginal effects with confidence intervals.
- Re-estimate with small-cluster inference.
- Change the current H3 status to `INCONCLUSIVE` until these checks are complete.

### 6. HS 25--97 is not equivalent to manufacturing

Severity: **High**

The current “manufacturing” group includes mineral products and fuels, especially HS 25--27. This is consequential: Brunei's value in the group is almost its entire export value, which reflects petroleum exports rather than manufacturing.

Required correction:

Choose one of the following:

1. Relabel HS 25--97 as “non-agricultural merchandise” and revise H4; or
2. Use a defensible concordance from HS/BEC to manufacturing; or
3. As a time-constrained approximation, use HS 28--96 and clearly document its limitations, with fuels HS 27 reported separately.

H4 must be rerun after recoding. The current H4 conclusion is not manuscript-ready.

## Important methodological issues

### 7. Strong multicollinearity is detected but not resolved

The reported VIFs are extremely high: approximately 32.7 for LSCI, 250.9 for GDP, and 218.4 for population. In addition, the current VIF calculation omits a constant, so the values are not computed in the standard way.

Actions:

- Recompute VIF after adding a constant.
- Report within-country correlations or assess collinearity after fixed-effect demeaning.
- Do not automatically include both GDP and population in every specification.
- Consider GDP per capita plus population, or GDP alone, depending on the theoretical model.
- Use a transparent sequence of parsimonious specifications.

### 8. Missing Comtrade rows cannot automatically be interpreted as zero trade

The raw bilateral file contains 3,072 observations, while the balanced panel contains 3,240. The pipeline fills all unmatched rows with zero. UN Comtrade extraction failures, missing reporter-years, and genuine zero flows must be distinguished.

Actions:

- Store API request metadata and row counts by reporter-year.
- Assert complete reporter-year extraction before zero completion.
- Add a test that no reporter-year total is zero when the country-level source shows positive exports.

### 9. Model results are hard-coded into the export summary

`src/export_results.py` manually embeds coefficients, p-values, hypothesis statuses, and interpretations. These values can become stale when a model or dataset changes.

Actions:

- Save machine-readable model results from each estimation script.
- Build `summary_findings.json` from those files.
- Do not automatically assign `CONFIRMED`; make hypothesis status depend on prespecified decision rules and robustness checks.

### 10. The configuration file is not the source of truth

`config/project_config.json` exists, but most scripts use hard-coded years, thresholds, paths, and cluster variables.

Actions:

- Add a shared configuration loader.
- Pass start/end years and coverage thresholds from the JSON file.
- Make table captions and titles read the actual estimation sample.

### 11. The title and estimation period need clearer alignment

The title says 2010--2025, while the main regressions use 2010--2024. This is acceptable only if the paper consistently says that 2025 is used for descriptive analysis and 2010--2024 for estimation.

Safer title if the regression sample remains unchanged:

> Kết nối vận tải biển và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN giai đoạn 2010--2024: Bằng chứng từ PPML và mô hình trọng lực mở rộng

### 12. Partner counts are easy to misstate

`config/partners.csv` contains 25 rows: 10 ASEAN economies and 15 external partners. Each exporter has 24 potential partners after excluding itself. The LSBCI estimation sample then drops Laos because bilateral maritime connectivity is unavailable, leaving 207 observed directed pairs.

The manuscript should describe the selection precisely instead of saying simply “24 partner countries.”

## Reproducibility and testing gaps

The existing tests verify dimensions, key uniqueness, nonnegative values, and retention of some zero flows. Add tests for:

1. SHA-256 values in `manifest.csv` against files that are present.
2. Country/year coverage for every raw source.
3. Reporter-year Comtrade completeness.
4. No country with positive aggregate exports but zero bilateral total.
5. ASEANstats world-partner filtering.
6. Exactly one HS classification/version per analysis.
7. Successful model convergence.
8. No perfect prediction/separation in PPML.
9. Full structural-gravity fixed effects included in the main model.
10. Automatically generated results matching published tables.

The large-data `.gitignore` choice is reasonable. However, reproducibility also requires direct retrieval instructions. Generic portal links plus checksums are useful but may not be enough to recreate the exact files. Add a `data/raw/README.md` containing exact filters, export options, download dates, units, and HS revision for each manually downloaded file.

## What is already aligned well

- Repository organization closely matches `design.md`.
- Raw/interim/processed separation is clear.
- Data provenance manifest includes file sizes and SHA-256 values.
- Country and bilateral panels use explicit keys.
- LSCI is aggregated from quarterly observations with coverage flags.
- The country panel preserves a balanced country-year frame.
- PPML is used with the dependent variable in levels.
- Pair clustering is used in bilateral models.
- Tables, figures, diagnostics, and LaTeX outputs are generated systematically.
- 2025 coverage is explicitly audited.
- Large raw files are omitted from Git while their metadata remain documented.

## Manuscript readiness

### Can be written now

- Introduction and motivation.
- Literature review.
- Conceptual mechanism linking maritime connectivity and trade.
- Data-source description, subject to exact HS revision confirmation.
- Research design, written as a planned/final specification rather than a description of the currently incomplete gravity model.
- Descriptive discussion for 2010--2025.
- Limitations and data-governance sections.

### Must wait for corrected results

- Abstract results and numerical findings.
- Hypothesis acceptance/rejection.
- Main regression tables.
- Causal or policy claims based on coefficients.
- H2 structural-gravity conclusion.
- H3 ASEAN-6/CLMV comparison.
- H4 manufacturing comparison.

## Recommended repair order

1. Repair/re-download Vietnam 2024 Comtrade data and add reporter-year validation.
2. Recode product groups and rerun H4.
3. Estimate the full pair + exporter-year + importer-year PPML model.
4. Implement small-cluster inference for country models.
5. Investigate the significant lead/placebo and weaken causal language.
6. Reconcile H3 using marginal-effect tests.
7. Recompute VIF correctly and simplify controls.
8. Generate summaries dynamically rather than hard-coding results.
9. Rerun tests, all models, tables, and figures from a clean state.
10. Freeze a validated results release, then write the empirical-results sections.

## Go/no-go decision

**Go** for drafting the non-results sections of the manuscript.  
**No-go** for publishing or submitting the current numerical results until blocking items 1--6 are resolved.