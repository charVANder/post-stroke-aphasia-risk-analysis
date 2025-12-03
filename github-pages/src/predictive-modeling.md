# Predictive Modeling: Hospital Readmission Risk

This page presents the results of predictive models developed to identify stroke survivors at risk for hospital readmission within 180 days of their first potentially inappropriate medication (PIM) prescription.

For key observations and a more detailed interpretation of these results, please refer to the specific Key Takeaways section found [here](./key-takeaways#predictive-modeling-takeaways).

## Model Overview

**Objective:** Predict 180-day hospital readmissions using medication-related features, mental health comorbidities, and aphasia status.

**Study Population:** 16,971 patients with at least one PIM prescription
- With Aphasia: 2,869 (16.90%)
- Without Aphasia: 14,102 (83.10%)

**Outcome:** Hospital readmission (emergency department or inpatient visit) within 180 days of first PIM prescription

**Note:** The readmission window is configurable in the modeling script. Analysis can be performed for 30-day, 90-day, or 180-day readmissions by changing the `READMISSION_OUTCOME` variable in `src/predictive_modeling.py`.

**Statistical Methods:**
- Train/test split: 80/20 (stratified by outcome)
- Class weighting: Balanced (to handle class imbalance)
- Cross-validation: 5-fold stratified (Lasso model)
- Evaluation metrics: AUROC (primary), AUPRC, sensitivity, specificity

---

## Model Performance

Three models were trained and evaluated: Logistic Regression (interpretable baseline), Lasso Logistic Regression (feature selection), and XGBoost (ensemble method).

### Performance Comparison

| Model | AUROC | AUPRC | Optimal Threshold |
|-------|-------|-------|-------------------|
| Logistic Regression | 0.672 | 0.174 | 0.483 |
| Lasso Logistic Regression | 0.637 | 0.149 | 0.493 |
| XGBoost | 0.647 | 0.149 | 0.491 |

**Best Performing Model:** Logistic Regression (AUROC = 0.672)

The logistic regression model achieved the highest discrimination (AUROC = 0.672) while maintaining interpretability through odds ratios. This performance is consistent with published literature on hospital readmission prediction (typical range: 0.60-0.75).

*Click [here](./visualizations#roc-curve-graph) to see the visualization comparing ROC scores across models (ROC Curve Model Comparison).*

---

## Feature Importance

### Top 15 Predictors (Logistic Regression)

Features ranked by absolute coefficient magnitude, indicating strongest associations with 30-day readmission risk.

| Rank | Feature | Odds Ratio | Interpretation |
|------|---------|------------|----------------|
| 1 | aphasia_x_polypharm | 1.62 | Aphasia + polypharmacy interaction |
| 2 | has_anxiety | 1.45 | Anxiety disorder diagnosis |
| 3 | has_any_discordance | 1.38 | Any medication-diagnosis mismatch |
| 4 | hyp_sed_risk | 1.35 | Hypnotic/sedative without diagnosis |
| 5 | has_polypharmacy_all_meds | 1.31 | 5+ concurrent medications |
| 6 | anxiolytic_risk | 1.28 | Anxiolytic without diagnosis |
| 7 | has_seizure | 1.24 | Seizure disorder |
| 8 | mh_burden | 1.22 | Mental health condition count |
| 9 | has_any_mental_health_condition | 1.18 | Any mental health diagnosis |
| 10 | has_schizophrenia | 1.16 | Schizophrenia diagnosis |
| 11 | has_ptsd | 1.15 | PTSD diagnosis |
| 12 | has_bipolar | 1.12 | Bipolar disorder |
| 13 | has_depression | 1.10 | Depression diagnosis |
| 14 | has_aphasia | 1.08 | Aphasia diagnosis |
| 15 | total_med_count | 1.05 | Total medication count |

- The interaction between aphasia and polypharmacy is the strongest predictor (OR = 1.62), indicating that patients with both conditions face substantially elevated readmission risk.
- Medication-diagnosis discordance (prescriptions without corresponding diagnoses) shows strong association with readmission.
- Mental health burden demonstrates a dose-response relationship with readmission risk.

*Click [here](./visualizations#lr-odds-ratios-graph) to see the visualization of the Top 15 Predictors and their odds ratios (Top 15 Predictors (Logistic Regression)).*

### SHAP Feature Importance (XGBoost)

SHAP (SHapley Additive exPlanations) values provide model-agnostic interpretability by measuring each feature's contribution to individual predictions.

**Top 10 Features by Mean SHAP Value:**

| Rank | Feature | Mean Impact |
|------|---------|-------------|
| 1 | max_concurrent_meds | 0.245 |
| 2 | total_med_count | 0.198 |
| 3 | mh_burden | 0.142 |
| 4 | has_antipsychotic | 0.089 |
| 5 | has_seizure | 0.087 |
| 6 | has_polypharmacy_all_meds | 0.076 |
| 7 | has_aphasia | 0.068 |
| 8 | total_pim_count | 0.062 |
| 9 | antipsych_risk | 0.059 |
| 10 | max_concurrent_pims | 0.057 |

- Medication burden (max_concurrent_meds, total_med_count) shows the largest overall impact on readmission predictions.
- Mental health comorbidity burden ranks third in importance.
- Aphasia shows moderate but consistent impact across patients.

*Click on the links to see visualizations of the features by their SHAP values ([SHAP Values](./visualizations#shap-graph)) and mean SHAP values ([Mean SHAP Values](./visualizations#mean-shap-graph)).*

---

## Feature Engineering

To capture complex relationships and clinical patterns, 11 engineered features were created from the base dataset:

### Interaction Features
- **aphasia_x_mh:** Aphasia × mental health condition interaction
- **aphasia_x_highrisk:** Aphasia × high-risk status interaction
- **aphasia_x_polypharm:** Aphasia × polypharmacy interaction

### Burden Scores
- **mh_burden:** Count of distinct mental health conditions (0-7)
- **pim_diversity:** Count of distinct PIM categories (0-4)
- **med_dx_discordance:** Sum of medication-diagnosis mismatches (0-4)

### Binary Indicators
- **has_any_discordance:** Any medication without diagnosis
- **antidep_anxio_combo:** Concurrent antidepressant + anxiolytic use
- **multiple_discordances:** 2+ medication-diagnosis mismatches
- **high_med_burden:** 10+ total medications
- **complex_patient:** Aphasia + mental health condition + PIM

**Total Features:** 36 (25 original + 11 engineered)

---

## Subgroup Analysis

Model performance was evaluated separately for patients with and without aphasia to ensure fairness and identify potential disparities.

### Performance by Aphasia Status

| Subgroup | N | AUROC | AUPRC |
|----------|---|-------|-------|
| Aphasia | 574 | 0.659 | 0.162 |
| No Aphasia | 2,820 | 0.674 | 0.176 |
| Difference | - | -0.015 | -0.014 |

- Performance difference between subgroups is minimal (AUROC difference = 0.015).
- The model performs comparably across aphasia status, indicating no substantial bias.
- Slightly lower performance in the aphasia group may reflect smaller sample size or greater clinical heterogeneity.

---

## Multivariate Statistical Analysis

### Multivariable Logistic Regression Models

Three models were fitted to examine independent effects after controlling for confounding variables.

#### Model 1: PIM Use as Outcome

**Formula:** has_any_pim ~ has_aphasia + has_any_mental_health_condition + total_med_count

| Variable | Odds Ratio | 95% CI | P-value |
|----------|------------|---------|---------|
| has_aphasia | 1.18 | 1.09-1.28 | <0.001 |
| has_any_mental_health_condition | 1.85 | 1.74-1.96 | <0.001 |
| total_med_count | 1.12 | 1.11-1.13 | <0.001 |

- After controlling for mental health status and overall medication count, aphasia remains an independent predictor of PIM use (OR = 1.18, p < 0.001).

#### Model 2: High-Risk Status as Outcome

**Formula:** is_high_risk ~ has_aphasia + has_any_mental_health_condition + total_pim_count + max_concurrent_meds

| Variable | Odds Ratio | 95% CI | P-value |
|----------|------------|---------|---------|
| has_aphasia | 1.12 | 1.02-1.23 | 0.015 |
| has_any_mental_health_condition | 2.34 | 2.16-2.54 | <0.001 |
| total_pim_count | 1.89 | 1.82-1.96 | <0.001 |
| max_concurrent_meds | 1.08 | 1.07-1.09 | <0.001 |

- Aphasia independently predicts high-risk status (OR = 1.12, p = 0.015) after adjusting for mental health comorbidity and medication burden.

#### Model 3: 180-Day Readmission as Outcome

**Formula:** has_180day_readmission ~ has_aphasia + is_high_risk + has_any_mental_health_condition + total_med_count

| Variable | Odds Ratio | 95% CI | P-value |
|----------|------------|---------|---------|
| has_aphasia | 1.08 | 0.92-1.27 | 0.342 |
| is_high_risk | 1.45 | 1.28-1.65 | <0.001 |
| has_any_mental_health_condition | 1.32 | 1.16-1.50 | <0.001 |
| total_med_count | 1.02 | 1.01-1.03 | <0.001 |

- The independent effect of aphasia on readmission is attenuated after controlling for high-risk medication status and mental health comorbidity, suggesting mediation through these pathways.

---

## Interaction Analysis

### Aphasia × Mental Health on PIM Use

**Research Question:** Does the effect of aphasia on PIM use differ by mental health status?

**Statistical Test:** Interaction term in logistic regression (has_aphasia:has_any_mental_health_condition)

**Result:** Interaction p-value = 0.082 (not significant at α = 0.05)

**Stratified Analysis:**

| Mental Health Status | Aphasia OR for PIM Use | 95% CI | P-value |
|---------------------|------------------------|---------|---------|
| No MH Condition | 1.14 | 1.02-1.28 | 0.025 |
| Has MH Condition | 1.22 | 1.09-1.36 | <0.001 |

- While the interaction term did not reach statistical significance, stratified analysis suggests the effect of aphasia on PIM use may be slightly stronger among patients with mental health conditions. This pattern warrants further investigation with larger samples.

---

## Model Deployment Considerations

### Clinical Interpretability

The logistic regression model provides direct clinical utility through interpretable odds ratios. For example:

**Example Patient Risk Calculation:**
- Base risk: 12% (average readmission rate)
- Has aphasia + polypharmacy: OR = 1.62 → Adjusted risk = 18.3%
- Also has anxiety: OR = 1.45 → Further adjusted risk = 24.5%
- Also has medication-diagnosis discordance: OR = 1.38 → Final risk = 31.2%

### Model Limitations

**Class Imbalance:** Readmission rate is 12%, leading to lower AUPRC (0.174) despite acceptable AUROC (0.672).

**Temporal Validation:** Current model uses random train/test split. Future work should validate on separate temporal cohort.

**Missing Variables:** Claims data lack clinical severity measures (like stroke severity, functional status) that may improve predictions.

**Generalizability:** Model trained on commercially-insured population may not generalize to Medicare/Medicaid populations.

---

## Possible Future Directions

### Model Enhancement
- Incorporate temporal patterns of medication use
- Test ensemble methods combining multiple model types

### Methodological Extensions
- Propensity score matching for causal inference
- Mediation analysis of aphasia → mental health → PIM → readmission pathway

---

## Technical Details

### Data Files
- **Input:** high_risk_cohort_with_readmissions.csv (N=53,068)
- **Filtered:** Patients with PIMs only (N=16,971)
- **Features:** 36 total (25 original + 11 engineered)
- **Output:** Trained models saved as .pkl files

### Reproducibility
All analyses are fully reproducible using scripts in the project repository:
- `src/extract_readmission_data.py` - Data extraction from OMOP database
- `src/feature_engineering.py` - Feature creation
- `src/predictive_modeling.py` - Model training and evaluation
- `src/multivariate_analyses.py` - Statistical analyses

Random seed: 42 (fixed for reproducibility)

---

**Last Updated:** December 3, 2025
