# Explanatory Modeling: Clinical Impact of PIMs and Hospital Readmissions

This page presents our analysis quantifying the clinical impact of potentially inappropriate medications (PIMs) on hospital readmissions among post-stroke patients, with attention to disparities by aphasia status.

For key observations and a detailed interpretation of these results, please refer to the specific Key Takeaways section found [here](./key-takeaways#explanatory-modeling-takeaways).

---

## Study Population

**Full Post-Stroke Cohort:** 53,068 patients
- With Aphasia: 8,265 (15.57%)
- Without Aphasia: 44,803 (84.43%)

Our initial analysis used a "high-risk" subset selected based on medication-diagnosis discordance criteria. However, this created circular definition issues (cohort selection included PIM-related criteria), potentially biasing PIM effect estimates. To avoid this, the final analysis used the complete post-stroke cohort, providing more generalizable findings about PIM associations across all stroke survivors.

---

## Methods
See [Methodology](./methodology#explanatory-modeling-methodology) for more details.

### Logistic Regression Model
```
logit(P(readmission)) = β₀ + β₁(aphasia) + β₂(PIM) +
                        β₃(depression) + β₄(anxiety) + β₅(PTSD) +
                        β₆(bipolar) + β₇(schizophrenia) +
                        β₈(psychotic disorder) + β₉(seizure)
```

**Outcome:** Hospital readmission within 180 days of stroke

### Key Predictors
- Aphasia status (binary)
- Any PIM exposure during observation period (binary)
- Seven mental health comorbidities (confounders)

**Note:** Interaction term (aphasia × PIM) was tested but found non-significant (p > 0.95) and removed from the final model.

### Statistical Methods
* L1 regularization (α = 0.01) to handle quasi-separation
* Bootstrap confidence intervals (1,000 iterations) for predicted probabilities
* G-computation for marginal effects decomposition

All analyses can be performed in `src/clinical_impact/run_analysis.py` with automated result generation and visualization.

---

## Quasi-Separation

A notable data pattern emerged during our analysis. 68% of patients were able to be perfectly predicted by a simple rule. This quasi-separation manifested as:

- Patients **without PIMs** had near-zero readmission rates across the full cohort
- Patients **with PIMs** showed substantial readmission rates (21-26%)

This pattern persisted even when analyzing the full 53,068-patient cohort, indicating it reflects true data structure rather than cohort selection artifacts.

The extreme separation suggests that PIM exposure is an exceptionally strong marker of readmission risk, though the magnitude likely reflects that PIMs prescribed to sicker patients already at high readmission risk (confounding by indication) rather than a purely causal effect.

---

## Observed Readmission Rates

Unadjusted 180-day readmission rates by aphasia status and PIM exposure:

| Group | Readmission Rate | PIM Prescription Rate |
|-------|------------------|----------------------|
| No Aphasia (N=44,803) | 7.50% | 31.48% |
| Aphasia (N=8,265) | 10.48% | 34.71% |

- Aphasia patients showed 2.98 percentage points higher readmission rate
- PIM prescription rates were modestly elevated in aphasia group (+3.24pp)
- Absolute disparity: +29.8 events per 1,000 patients

*An interactive graph (Observed Readmission Rates) to view the observed readmission rates can be seen in the visualization page [here](./visualizations#observed-readmission-rates). Toggle the display mode to view between readmission rates and PIM prescription rates.*

---

## Model Results

### Odds Ratios

| Variable | Odds Ratio | 95% CI | P-value | Significance |
|----------|-----------|---------|---------|--------------|
| **PIM Exposure** | **289,059** | **[7.4, 1.13×10¹⁰]** | **0.020** | **\*** |
| Seizure Disorder | 1.90 | [1.74, 2.07] | <0.001 | \*\*\* |
| Psychotic Disorder | 2.02 | [1.60, 2.56] | <0.001 | \*\*\* |
| Depression | 1.43 | [1.33, 1.54] | <0.001 | \*\*\* |
| Bipolar Disorder | 1.41 | [1.19, 1.67] | <0.001 | \*\*\* |
| **Aphasia** | **1.29** | **[1.17, 1.41]** | **<0.001** | **\*\*\*** |
| Anxiety | 1.12 | [1.04, 1.21] | 0.002 | \*\* |
| PTSD | 0.97 | [0.78, 1.21] | 0.796 | |
| Schizophrenia | 0.81 | [0.55, 1.20] | 0.292 | |

\*p<0.05, \*\*p<0.01, \*\*\*p<0.001

*An interactive forest plot (Forest Plot for Odds Ratios) can be seen in the visualizations page [here](./visualizations#forest-plot). The extreme odds ratio for PIM Exposure makes it difficult to visualize the other predictors on a standard scale, so you can toggle the display mode to look at either the log scale (with all predictors), the log scale excluding PIM (clearer comparison), or linear scale (compressed).*

**Model Fit:**
- Pseudo R² (McFadden): 0.371
- AIC: 18,571.8
- BIC: 18,660.6

The extreme OR for PIM exposure (289,059) reflects the quasi-separation pattern described earlier. While statistically significant, this should be interpreted as a very strong association rather than a causal effect estimate.

---

## Predicted Probabilities

Model-predicted 180-day readmission probabilities by aphasia status and PIM exposure, marginalizing over observed mental health confounder distributions.

| Scenario | Predicted Probability | 95% CI |
|----------|----------------------|---------|
| Aphasia + PIM | 26.09% | [24.55%, 27.71%] |
| Aphasia + No PIM | 0.26% | [0.00%, 0.03%] |
| No Aphasia + PIM | 21.61% | [20.83%, 22.41%] |
| No Aphasia + No PIM | 0.26% | [0.00%, 0.02%] |

- PIM exposure is associated with ~100-fold increase in readmission probability.
- Aphasia patients with PIMs show modestly higher readmission risk (+4.48pp) compared to non-aphasia patients with PIMs.
- Readmission risk is nearly identical across aphasia status when PIMs are absent.

---

## Expected Events per 1,000 Patients
As suggested, we also translated the predicted probabilities into expected readmission events per 1,000 patients.

| Scenario | Events per 1,000 | 95% CI |
|----------|------------------|---------|
| Aphasia + PIM | 260.9 | [245.5, 277.1] |
| Aphasia + No PIM | 2.6 | [0.0, 0.3] |
| No Aphasia + PIM | 216.1 | [208.3, 224.1] |
| No Aphasia + No PIM | 2.6 | [0.0, 0.2] |

- Among 1,000 aphasia patients with PIMs, expect ~261 readmissions within 180 days.
- Among 1,000 aphasia patients without PIMs, expect ~3 readmissions.
- PIM-associated excess risk: ~258 additional events per 1,000 aphasia patients.

*Click [here](./visualizations#events-per-1000-graph) to see the visualization of expected events per 1,000 Patients (Expected Events Per 1000 Patients).*


---

## Risk Differences

### Within-Group Comparisons (PIM vs No PIM)

| Group | Absolute Risk Difference | Relative Risk Difference |
|-------|-------------------------|-------------------------|
| Aphasia | +258.2 per 1,000 | +9,778% |
| No Aphasia | +213.5 per 1,000 | +8,221% |

### Between-Group Comparisons (Aphasia vs No Aphasia)

| PIM Status | Absolute Risk Difference | Relative Risk Difference |
|------------|-------------------------|-------------------------|
| With PIMs | +44.7 per 1,000 | +20.7% |
| Without PIMs | +0.0 per 1,000 | +1.7% |

- PIM exposure appears to associate with massive absolute risk increases in both groups.
- Aphasia's additional contribution is modest when PIMs are present (+45 events per 1,000)
- Aphasia effect is negligible when PIMs are absent

---

## Marginal Effects Decomposition

Decomposition of the 29.8 per 1,000 readmission disparity between aphasia and non-aphasia groups.

| Component | Contribution (per 1,000) | % of Disparity | Our Interpretation |
|-----------|-------------------------|----------------|----------------|
| Baseline Risk | 0.0 | 0.0% | Readmission risk without aphasia or PIMs |
| **Differential PIM Exposure** | **7.0** | **23.4%** | Due to higher PIM prescription rates in aphasia group |
| Independent Aphasia Effect | 0.0 | 0.0% | Direct effect of aphasia without PIMs |
| **Interaction Effect** | **44.5** | **149.0%** | Differential response to PIMs between groups |

**Note:** Components sum to 22.4 per 1,000 (model-predicted disparity) versus 29.8 per 1,000 observed, reflecting model fit.

- Differential PIM prescription accounts for ~23% of the disparity (aphasia patients prescribed PIMs at higher rates).
- Interaction effect dominates (149%), suggesting aphasia patients experience greater readmission risk when exposed to PIMs.
- Independent aphasia effect is minimal (0%) when PIM exposure is controlled.

*Click [here](./visualizations#marginal-effects-graph) to view the bar chart (Marginal Effects Decomposition) showing the decomposition components. There is a toggle to switch between absolute contributions (per 1,000) and percentage of disparity.*

---

## Reproducibility and Technical Details
All analyses are fully reproducible using scripts in the project repository:

**Analysis Script:** `src/clinical_impact/run_analysis.py`

**Outputs:**
- Model coefficients and odds ratios: `data/clinical_impact_model_results.csv`
- Predicted probabilities: `data/clinical_impact_predicted_probabilities.csv`
- Risk differences: `data/clinical_impact_risk_differences.csv`
- Marginal effects decomposition: `data/clinical_impact_marginal_effects_decomposition.csv`
- Visualizations: `figs/clinical_impact_*.png`

---

**Last Updated:** December 2, 2025