# Key Takeaways and Major Observations
Interpretation, discussion, and major findings of the results shown in the initial EDA, statistics reports, predictive modeling reports, and explanatory modeling reports.

---

## Initial EDA Takeaways <a id="eda-takeaways"></a>

1. **Age Distribution:** Age distributions were very similar between patients with and without aphasia, with both groups consisting primarily of older adults over 60 years old.

2. **Mental Health Prevalence:** Patients with aphasia showed higher rates of mental health conditions overall, with seizure disorders showing the largest difference between groups.

3. **PIM Categories:** Antidepressants were the most prevalent PIM class in both groups, followed by anxiolytics, hypnotics/sedatives, and antipsychotics.

4. **Antidepressant Paradox:** Despite higher depression rates in the aphasia group, antidepressant prescribing was lower in aphasia patients, potentially indicating undertreatment due to communication barriers.

5. **Correlation Patterns:** Mental health conditions and PIM use showed positive correlations, with depression and anxiety demonstrating the strongest comorbidity patterns in both groups.

6. **Pattern Consistency:** While prevalence rates differed between groups, the co-occurrence patterns of conditions and PIMs remained consistent regardless of aphasia status, suggesting communication barriers may affect diagnosis rates but not underlying condition relationships.

---

## Statistics Report Takeaways <a id="statistics-takeaways"></a>

1. **Mental Health Condition Prevalence:** Patients with aphasia showed significantly higher rates of any mental health condition (+8.21pp, p<0.0001). The most substantial differences were in depression (+5.20pp, 33.36% vs 28.16%) and seizure disorders (+8.82pp, 20.93% vs 12.12%).

2. **Mental Health Condition Burden:** Aphasia patients had a higher mean number of mental health conditions, indicating not only higher rates of individual conditions but also more co-occurring diagnoses. Anxiety disorders were also more prevalent (+1.47pp, p=0.0062), while PTSD, bipolar disorder, schizophrenia, and psychotic disorders showed no significant differences.

3. **PIM Prevalence:** Any PIM use was modestly elevated in aphasia patients (34.71% vs 31.48%, +3.24pp, p<0.0001), driven primarily by increased antidepressant use (29.07% vs 25.24%). Mean number of PIMs and total medication counts were also significantly higher (9.42±10.34 vs 9.04±10.13, p=0.0019).

4. **Risk Flags:** Aphasia patients showed significant elevated antidepressant risk and antipsychotic risk, suggesting potential medication-diagnosis discordance (receiving medications without corresponding diagnoses).

5. **High-Risk Classification:** A greater proportion of aphasia patients met high-risk criteria (11.59% vs 10.66%, p=0.0127), though most patients in both groups had lower risk scores of 0-1. Risk score distributions differed significantly between groups.

6. **Polypharmacy and Medication Burden:** Aphasia patients had significantly higher rates of polypharmacy (45.57% vs 41.80%, +3.77pp, p<0.0001). Antidepressants were the most commonly prescribed PIM class, followed by anxiolytics, antipsychotics, and hypnotics/sedatives.

7. **Aphasia-Outcome Correlations:** While aphasia status showed modest direct correlations with adverse outcomes (r=0.02-0.06), the consistent pattern of statistically significant differences across multiple medication management domains suggests aphasia's impact operates through communication barriers rather than as a simple linear predictor.

8. **Risk Factor Relationships:** Very strong correlation was observed between polypharmacy and risk score (r=0.83, p<0.0001). Mental health conditions showed moderate correlation with PIM use (r=0.35, p<0.0001), indicating these risk factors tend to cluster together.

9. **Mental Health Conditions by Aphasia Status (stratified analysis):** Among patients without diagnosed mental health conditions, aphasia patients showed substantially higher medication-diagnosis discordance (12.03% receiving antidepressants vs 10.52%, +1.51pp; 13.79% classified as high-risk vs 12.37%). Among patients with diagnosed conditions, discordance remained elevated (3.29% vs 2.07% antidepressant risk, +1.21pp), suggesting potential underdiagnosis where communication barriers complicate diagnostic assessment.

---

## Predictive Modeling Report Takeaways <a id="predictive-modeling-takeaways"></a>

1. **Model Performance:** Logistic regression achieved the best discrimination for 180-day readmission prediction (AUROC = 0.672, AUPRC = 0.174), consistent with published readmission prediction models. Performance was comparable across aphasia status (AUROC difference = 0.015), indicating no substantial bias.

2. **Aphasia-Polypharmacy Interaction:** The interaction between aphasia and polypharmacy was the strongest predictor of 180-day readmission risk, suggesting that patients with both conditions face substantially elevated readmission risk compared to either factor alone.

3. **Medication-Diagnosis Discordance as a Risk Factor:** Patients receiving medications without corresponding documented diagnoses showed significantly elevated readmission risk (OR = 1.38), highlighting potential gaps in care coordination and diagnostic documentation.

4. **Mental Health Burden:** Mental health comorbidity demonstrated a dose-response relationship with readmission risk (OR = 1.22 per additional condition), with anxiety disorders showing particularly strong association (OR = 1.45).

5. **Medication Burden Dominates Feature Importance:** SHAP analysis revealed that overall medication burden (max concurrent medications, total medication count) had the largest impact on readmission predictions, followed by mental health comorbidity burden and aphasia status.

6. **Independent Effect of Aphasia on Medication Patterns:** Multivariable regression showed aphasia independently predicted PIM use (OR = 1.18, p<0.001) and high-risk status (OR = 1.12, p=0.015) after controlling for mental health status and medication burden.

7. **Aphasia's Indirect Effect on Readmission:** Aphasia's association with 180-day readmission seems to operate through medication management problems and mental health comorbidity rather than as a direct independent risk factor. When controlling for high-risk medication status and mental health conditions, the direct effect of aphasia on readmission becomes small and non-significant (OR = 1.08, p=0.342).

---

## Explanatory Modeling Report Takeaways <a id="explanatory-modeling-takeaways"></a>

1. **Extremely Strong Association:** Among 53,068 post-stroke patients, PIM exposure showed an approximately 100-fold difference in 180-day readmission rates. Patients without PIMs had 2.6 readmissions per 1,000, while those with PIMs had 216-261 per 1,000.

2. **Independent Effects After Controlling for Confounders:** After adjusting for mental health conditions, both aphasia (OR=1.29, p<0.001) and PIM exposure (OR=289,059, p=0.020) remained independently associated with readmissions. The extreme odds ratio for PIMs reflects quasi-separation in the data.

3. **Modest Aphasia-Specific Risk:** Among patients with PIMs, aphasia patients showed modestly higher readmission rates than non-aphasia patients (260.9 vs 216.1 events per 1,000, +44.7 per 1,000). When PIMs were absent, readmission risk was nearly identical across aphasia status.

4. **Disparity Decomposition:** Of the 29.8 per 1,000 readmission disparity between aphasia and non-aphasia groups: 23% was attributable to differential PIM prescription rates (aphasia patients prescribed PIMs more often), 149% from interaction effects (aphasia patients with PIMs showed disproportionately higher risk), and minimal independent aphasia effect when PIM exposure was controlled.

5. **Limitations:** The quasi-separation pattern (68% of patients perfectly predicted by PIM status alone) and extreme effect size suggest this is an associative rather than causal relationship. PIMs likely serve as markers of underlying disease severity. The most plausible explanation for the observed pattern is that PIMs are preferentially prescribed to patients already at high readmission risk due to greater comorbidity burden, cognitive impairment, or medical complexity. Without baseline PIM measurement, we cannot determine whether PIMs preceded readmissions or were prescribed during readmission hospitalizations (reverse causation). The near-perfect separation means coefficient estimates are unstable despite regularization. Confidence intervals are extremely wide for PIM exposure. Findings reflect patients in this specific healthcare system and may not generalize to other populations or settings.

6. **Clinical Utility Despite Causal Limitations:** PIM exposure combined with aphasia status and mental health burden successfully identifies a very high-risk subgroup (21-26% readmission rate) for targeted interventions such as medication reconciliation, deprescribing initiatives, and enhanced monitoring, even without establishing direct causation.
