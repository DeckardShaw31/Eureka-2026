# Second review of commit `1f90606`

Review date: 2026-09-23

## Verdict

The implementation materially improves the repository and resolves most engineering issues from the first audit. It is now suitable for drafting the introduction, literature review, data section, methods, descriptive results, and the H1 discussion.

It is not yet appropriate to label every hypothesis “confirmed.” Four corrections remain before freezing the empirical manuscript.

## Verified improvements

1. Vietnam 2024 bilateral observations remain missing instead of being converted to false zeros.
2. The bilateral panel now contains `trade_observed`, `zero_trade_confirmed`, `reporter_year_complete`, and `missing_reason`.
3. G1 includes pair, exporter-year, and importer-year fixed effects simultaneously.
4. The product split now separates HS 25--27, HS 28--96, and HS 01--24.
5. Country-model inference uses clustered covariance with `use_t=True`.
6. M5 calculates the total CLMV slope and its standard error.
7. Standard and within-country VIF calculations include a constant.
8. Model estimates are stored in JSON and read by `export_results.py`.
9. The seven current data-contract tests cover basic dimensions, keys, values, zero retention, Vietnam 2024, and LSBCI validity.

## Remaining blocker 1 -- H3 uses the wrong rejection rule

H3 states that the LSCI effect is **larger for CLMV than for ASEAN-6**.

The relevant test is therefore:

\[
H_0:\beta_{LSCI\times CLMV}=0.
\]

The interaction estimate is `0.660`, with `p = 0.073`. At the conventional 5% level, the difference between groups is not statistically significant. The test of

\[
H_0:\beta_{LSCI}+\beta_{LSCI\times CLMV}=0
\]

only establishes whether the total CLMV slope differs from zero. It does **not** establish that the CLMV slope is larger than the ASEAN-6 slope.

Required change:

- Replace `CONFIRMED` with `WEAKLY SUPPORTED AT 10%` or `INCONCLUSIVE AT 5%`.
- Base the H3 status on the interaction p-value, not the total-effect p-value.
- Report both results: CLMV total slope `1.186` (`p = 0.002`) and between-group difference `0.660` (`p = 0.073`).
- Do not say “cao hơn đáng kể” without specifying the 10% significance level.

## Remaining blocker 2 -- H4 requires a direct coefficient-difference test

The current logic declares H4 confirmed because the manufacturing coefficient is significant while the agriculture and fuels coefficients are not. A significant coefficient in one regression and a nonsignificant coefficient in another do not prove that the two coefficients differ statistically.

Required change:

1. Reshape the three product outcomes into a long `country-year-product_group` panel.
2. Estimate a pooled PPML with product-group interactions:

\[
E(Export_{ikt}) = \exp[\beta_1\ln LSCI_{it}
+ \beta_2(\ln LSCI_{it}\times Manufacturing_k)
+ \beta_3(\ln LSCI_{it}\times Fuels_k)
+ FE + controls].
\]

3. Test directly:
   - manufacturing slope minus agriculture slope;
   - manufacturing slope minus fuels slope.
4. Cluster by country and describe the nine-cluster limitation.

Until these difference tests are run, H4 should be described as “suggestive evidence” rather than “confirmed.”

## Remaining blocker 3 -- H2 is not supported by the preferred specification

The preferred structural-gravity model G1 estimates:

```text
beta_LSBCI = -0.195
p = 0.422
```

The simpler G2 model estimates a positive coefficient of `0.770` with `p = 0.004`. Because G1 provides the theoretically preferred multilateral-resistance controls, the primary conclusion should follow G1.

Required interpretation:

> The positive LSBCI association appears in the less saturated pair-and-year fixed-effect model, but it is not robust to the preferred structural-gravity specification. H2 is therefore not supported in the main specification.

Do not state that the LSBCI variation was “absorbed completely.” The coefficient remains identified and estimated; it simply becomes negative and statistically indistinguishable from zero after the richer controls.

## Remaining blocker 4 -- estimation-sample metadata are inconsistent

`summary_findings.json` reports:

```text
3,216 bilateral observations
216 pairs
144 zero observations
```

The gravity result JSON reports the actual estimation sample:

```text
3,082 bilateral observations
207 pairs
142 zero observations
```

The difference arises because `export_results.py` filters on observed trade but not on observed `ln_lsbci`. Manuscript metadata must use the exact model sample.

Required correction:

```python
b_sample = df_bilateral[
    (df_bilateral['year'] <= 2024)
    & df_bilateral['trade_usd'].notna()
    & df_bilateral['ln_lsbci'].notna()
]
```

Alternatively, read `n_obs`, `n_pairs`, and `zero_obs` directly from the G1 JSON output.

## Important caveats

### Reporter-year completeness remains heuristic

`reporter_year_complete` is set to one when at least 15 partner rows are present. This fixes the obvious Vietnam 2024 failure but does not prove that every omitted partner observation is a genuine zero. Preserve an API request log or extraction-success flag for each reporter-year and explain the rule in the data section.

### Nine-cluster inference remains fragile

`use_t=True` is an improvement, but it is not equivalent to a wild cluster bootstrap. Results based on nine clusters, and especially subgroup estimates based on three or six clusters, require cautious wording. A wild cluster bootstrap for the main LSCI and interaction coefficients would strengthen the paper.

### The lead test still rejects the placebo condition

The significant future LSCI coefficient remains evidence of persistence, anticipation, reverse causality, or common trends. Country-specific trends are a useful robustness check, but they do not explain which mechanism causes the lead result. The paper must consistently use associational language.

### Automated output is only partially reliable

The numeric inputs are now read dynamically, but the hypothesis-status rules encode invalid logic for H3 and H4. “Dynamic” does not automatically mean statistically correct. README prose also remains a manually maintained artifact.

## Recommended hypothesis table after the current evidence

| Hypothesis | Defensible current conclusion |
|---|---|
| H1 | Supported as a robust positive association, not a causal effect |
| H2 | Not supported in the preferred structural-gravity model; positive only in G2 |
| H3 | Weak evidence at 10%; inconclusive at 5% |
| H4 | Suggestive evidence; requires direct coefficient-difference tests |

## Manuscript decision

**Begin writing now:** introduction, theory, literature review, data, methods, descriptive evidence, H1, limitations.

**Do not freeze yet:** abstract findings, H2--H4 conclusions, final regression discussion, and policy recommendations.

Once the four blockers above are corrected, the empirical manuscript can be finalized.