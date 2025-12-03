# Statistics Report
This page provides the statistics and test results of our cohort analysis. For more detailed methodology and visualizations, please also see other pages.

For key observations and a more detailed interpretation of all these results, please refer to the specific Key Takeaways section found [here](./key-takeaways#statistics-takeaways).

---

## Study Overview

**Initial Stroke Population:** ~174,000 patients (all hospital patients with ≥1 stroke occurrence with second occurring within 6 months)

**Base Cohort:** 53,068 patients
- Inclusion criteria: Patients without dementia and with a 6-month observation period before/after first stroke occurrence
- **With Aphasia:** 8,265 (15.57%)
- **Without Aphasia:** 44,803 (84.43%)

**Statistical Methods:**
- Chi-square tests for categorical variables
- Independent t-tests for continuous variables
- Pearson correlation for associations
- Significance level: α = 0.05

---

## Mental Health Condition Prevalence
Examining whether patients with aphasia have different rates of diagnosed mental health conditions compared to patients without aphasia. Significant p-values (p < 0.05) indicate that the observed differences are unlikely to be due to chance alone.


| Condition | Aphasia | No Aphasia | Difference | p-value |
|-----------|---------|------------|------------|---------|
| **Any Mental Health Condition** | 4,566 (55.25%) | 21,075 (47.04%) | +8.21 pp | <0.0001 |
| Depression | 2,757 (33.36%) | 12,616 (28.16%) | +5.20 pp | <0.0001 |
| Anxiety | 2,392 (28.94%) | 12,306 (27.47%) | +1.47 pp | 0.0062 |
| Seizure Disorder | 1,730 (20.93%) | 5,428 (12.12%) | +8.82 pp | <0.0001 |
| Bipolar Disorder | 153 (1.85%) | 879 (1.96%) | -0.11 pp | 0.5309 |
| Psychotic Disorder | 118 (1.43%) | 644 (1.44%) | -0.01 pp | 0.9858 |
| PTSD | 92 (1.11%) | 595 (1.33%) | -0.21 pp | 0.1247 |
| Schizophrenia | 30 (0.36%) | 197 (0.44%) | -0.08 pp | 0.3733 |

*See [Interactive Cohort Explorer](./cohort-explorer) for visual representation.*

### Mental Health Condition Burden
Examining the cumulative burden of mental health conditions (how many distinct conditions each patient has been diagnosed with). We compared both the average number of conditions and the distribution patterns between aphasia and non-aphasia patients. Significant results suggest that aphasia patients not only have higher rates of individual conditions, but also tend to have multiple co-occurring conditions.

**Mean Number of Conditions:**
- Aphasia: 0.88 ± 0.98
- No Aphasia: 0.73 ± 0.94
- t-test: p < 0.0001

**Distribution by Number of Conditions:**

| # Conditions | Aphasia | No Aphasia |
|--------------|---------|------------|
| 0 | 3,699 (44.75%) | 23,728 (52.96%) |
| 1 | 2,517 (30.45%) | 12,208 (27.25%) |
| 2 | 1,511 (18.28%) | 6,762 (15.09%) |
| 3 | 450 (5.44%) | 1,666 (3.72%) |
| 4 | 65 (0.79%) | 294 (0.66%) |
| 5 | 16 (0.19%) | 108 (0.24%) |
| 6 | 6 (0.07%) | 29 (0.06%) |
| 7 | 1 (0.01%) | 5 (0.01%) |

Chi-square test: p < 0.0001

*Click [here](./visualizations#mh-burden-distribution-graph) to see the visualization of this distribution (Mental Health Burden Distribution).*

---

## Potentially Inappropriate Medication (PIM) Prevalence
Comparing the use of PIMs between aphasia and non-aphasia patients. Polypharmacy is also examined as it increases the risk of adverse drug interactions. Significant differences suggest disparities in medication management between the two groups.

| Medication Type | Aphasia | No Aphasia | Difference | p-value |
|----------------|---------|------------|------------|---------|
| **Any PIM** | 2,869 (34.71%) | 14,102 (31.48%) | +3.24 pp | <0.0001 |
| Antidepressant | 2,403 (29.07%) | 11,309 (25.24%) | +3.83 pp | <0.0001 |
| Anxiolytic | 1,011 (12.23%) | 5,515 (12.31%) | -0.08 pp | 0.8587 |
| Antipsychotic | 451 (5.46%) | 2,274 (5.08%) | +0.38 pp | 0.1569 |
| Hypnotic/Sedative | 240 (2.90%) | 1,500 (3.35%) | -0.44 pp | 0.0404 |
| **Polypharmacy (≥5 meds)** | 3,766 (45.57%) | 18,726 (41.80%) | +3.77 pp | <0.0001 |

*See [Interactive Cohort Explorer](./cohort-explorer) for visual representation*

### PIM Burden
Similar to the mental health burden, we examined how many different PIMs patients are taking.

**Mean Number of PIMs:**
- Aphasia: 0.50 ± 0.78
- No Aphasia: 0.46 ± 0.78
- t-test: p < 0.0001

**Distribution by Number of PIMs:**

| # PIMs | Aphasia | No Aphasia |
|--------|---------|------------|
| 0 | 5,396 (65.29%) | 30,701 (68.52%) |
| 1 | 1,882 (22.77%) | 9,000 (20.09%) |
| 2 | 761 (9.21%) | 3,869 (8.64%) |
| 3 | 203 (2.46%) | 1,072 (2.39%) |
| 4+ | 23 (0.28%) | 161 (0.36%) |

Chi-square test: p < 0.0001

*Click [here](./visualizations#pim-burden-distribution-graph) to see the visualization of this distribution (PIM Burden Distribution).*

---

## Medication-Diagnosis Risk Flags

Risk flags identify potential medication-diagnosis discordance—situations where patients are receiving medications without a corresponding formal diagnosis in their medical record. Significant differences indicate that the pattern of discordance differs between groups.

| Risk Category | Aphasia | No Aphasia | Difference | p-value |
|---------------|---------|------------|------------|---------|
| Antidepressant Risk | 595 (7.20%) | 2,934 (6.55%) | +0.65 pp | 0.0310 |
| Antipsychotic Risk | 365 (4.42%) | 1,714 (3.83%) | +0.59 pp | 0.0120 |
| Anxiolytic Risk | 243 (2.94%) | 1,581 (3.53%) | -0.59 pp | 0.0077 |
| Hypnotic/Sedative Risk | 108 (1.31%) | 683 (1.52%) | -0.22 pp | 0.1466 |

*See [Interactive Cohort Explorer](./cohort-explorer) for visual representation.*

---

## High-Risk Patient Classification
A composite risk score was used to identify patients with multiple risk factors by summing individual risk flags and polypharmacy status. Patients with a total risk score of 2 or higher were classified as "high-risk," indicating they face compounded medication safety concerns.

**Definition:** Total risk score ≥ 2 (sum of individual risk flags + polypharmacy indicator)

**Prevalence:**
- Aphasia: 958 / 8,265 (11.59%)
- No Aphasia: 4,775 / 44,803 (10.66%)
- Difference: +0.93 pp (p = 0.0127)

### Risk Score Distribution

| Risk Score | Aphasia | No Aphasia |
|------------|---------|------------|
| 0 | 4,309 (52.14%) | 24,771 (55.29%) |
| 1 | 2,998 (36.27%) | 15,257 (34.05%) |
| 2 | 812 (9.82%) | 4,044 (9.03%) |
| 3 | 130 (1.57%) | 638 (1.42%) |
| 4 | 15 (0.18%) | 86 (0.19%) |
| 5 | 1 (0.01%) | 7 (0.02%) |

*Click [here](./visualizations#risk-score-distribution-graph) to see the visualization of this distribution (Risk Score Distribution).*

---

## Additional Risk Metrics
Continuous measures were added for extra perspective on medication use and risk. They capture not just whether patients have PIMs or polypharmacy, but to what extent and what intensity of exposure over time. Significant p-values indicate meaningful differences in the magnitude of medication burden between groups.

| Metric | Aphasia (Mean ± SD) | No Aphasia (Mean ± SD) | p-value |
|--------|---------------------|------------------------|---------|
| Total PIM Count | 0.85 ± 1.71 | 0.76 ± 1.62 | <0.0001 |
| Max Concurrent PIMs | 0.63 ± 1.08 | 0.58 ± 1.06 | <0.0001 |
| Total Risk Score | 0.61 ± 0.74 | 0.57 ± 0.73 | <0.0001 |
| Total Medication Count | 9.42 ± 10.34 | 9.04 ± 10.13 | 0.0019 |
| Max Concurrent Medications | 5.16 ± 4.89 | 4.92 ± 4.77 | <0.0001 |

---

## Correlation Analysis
Correlation measures the strength and direction of the relationships between certain variables (ranging from -1 to +1). Even small correlations can be statistically significant in large samples (although practical significance can also change depending on context).

### Aphasia and Key Outcomes
Correlations to examine how strongly aphasia status is associated with various adverse outcomes. While statistically significant, smaller correlation coefficients also indicate that aphasia explains only a small portion of variance in these outcomes. Other factors likely play larger roles.

| Variable Pair | r | p-value |
|---------------|---|---------|
| Aphasia × Any Mental Health Condition | 0.0595 | <0.0001 |
| Aphasia × Polypharmacy | 0.0277 | <0.0001 |
| Aphasia × Any PIM | 0.0252 | <0.0001 |
| Aphasia × Total Risk Score | 0.0208 | <0.0001 |
| Aphasia × High-Risk Status | 0.0109 | 0.0120 |

### Risk Factors and Mental Health
Correlations to examine relationships between different risk measures. Strong correlations show how these measures are related. The more modest correlations also suggest that certain risk factors tend to cluster together, which may have clinical implications in future analyses.

| Variable Pair | r | p-value |
|---------------|---|---------|
| Polypharmacy × Risk Score | 0.8311 | <0.0001 |
| PIM Count × Risk Score | 0.4979 | <0.0001 |
| Mental Health × PIM | 0.3533 | <0.0001 |
| Mental Health × Risk Score | 0.0269 | <0.0001 |

---

## Stratified Analysis by Mental Health Status
Examining whether the relationship between aphasia and medication outcomes differs depending on whether patients have diagnosed mental health conditions.

### Patients WITH Mental Health Conditions (n = 25,641)
Among patients with mental health diagnoses, we expected higher baseline PIM use since these medications are often prescribed for mental health treatment.

| Outcome | Aphasia (n=4,566) | No Aphasia (n=21,075) | Difference |
|---------|-------------------|-----------------------|------------|
| Any PIM | 2,249 (49.26%) | 10,321 (48.97%) | +0.28 pp |
| High-Risk | 448 (9.81%) | 1,841 (8.74%) | +1.08 pp |
| Antidepressant Risk | 150 (3.29%) | 437 (2.07%) | +1.21 pp |
| Anxiolytic Risk | 79 (1.73%) | 449 (2.13%) | -0.40 pp |

*See [Interactive Cohort Explorer](./cohort-explorer) for visual representations.*   

### Patients WITHOUT Mental Health Conditions (n = 27,427)
Among patients without mental health diagnoses, PIM use was expected to be lower overall. It should be noted that risk flags become particularly concerning here, as they indicate patients receiving medications despite no documented mental health condition. This is a potential signal of diagnostic gaps or informal prescribing.

| Outcome | Aphasia (n=3,699) | No Aphasia (n=23,728) | Difference |
|---------|-------------------|-----------------------|------------|
| Any PIM | 620 (16.76%) | 3,781 (15.93%) | +0.83 pp |
| High-Risk | 510 (13.79%) | 2,934 (12.37%) | +1.42 pp |
| Antidepressant Risk | 445 (12.03%) | 2,497 (10.52%) | +1.51 pp |
| Anxiolytic Risk | 164 (4.43%) | 1,132 (4.77%) | -0.34 pp |

*See [Interactive Cohort Explorer](./cohort-explorer) for visual representations.*

---

*Note: pp = percentage points. All statistical tests used α = 0.05 significance level. Dementia patients were excluded from all analyses to avoid confounding.*

**Last Updated:** December 2, 2025