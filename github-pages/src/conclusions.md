# Conclusions
This study of 53,068 post-stroke patients revealed that aphasia is associated with elevated rates of mental health conditions, increases in PIM use and polypharmacy, and patterns of medication-diagnosis discordance that suggest potential underdiagnosis. Among patients without documented mental health conditions, aphasia patients showed substantially higher rates of receiving medications without corresponding diagnoses, indicating that communication barriers may complicate psychiatric assessment and lead to symptomatic management without formal evaluation.

Our predictive modeling successfully identified high-risk patients, with the aphasia-polypharmacy interaction emerging as the strongest predictor of 180-day readmissions. The explanatory modeling revealed an exceptionally strong association between PIM exposure and readmissions (approximately 100-fold difference), though the quasi-separation pattern indicates PIMs likely serve as markers of underlying disease severity rather than independent causes. While we cannot establish definitive causality with our current data, these findings successfully identified a vulnerable population--stroke survivors with aphasia, mental health burden, and PIM exposure—-that faces 21-26% readmission rates and would benefit from targeted interventions such as enhanced medication reconciliation, communication-assisted diagnostic approaches, and increased monitoring.

Ultimately, this work showed that communication barriers associated with aphasia contribute to suboptimal medication management and potential gaps in mental health care. Improving outcomes for this population will require changes that facilitate better communication between patients and providers, more comprehensive mental health screening protocols, and careful attention to medication safety in the context of post-stroke recovery.

This project was an incredible learning experience, allowing us to explore health informatics, data science, and patient-centered care in meaningful ways. Working with real-world clinical data was both challenging and deeply rewarding, and we are extremely grateful for the opportunity to contribute research that may hopefully improve care for stroke survivors facing the compounded difficulties of aphasia and complex medication management. We thank our stakeholders and advisors for their guidance, clinical expertise, and encouragement throughout this research. Their insights were invaluable in shaping our analysis and interpreting our findings!

---

## Future Work
**Use Stronger Statistical Methods:**
- Use more advanced statistical techniques beyond our current chi-square tests, t-tests, and Pearson correlations. Methods like Bayesian inference, mixed-effects models, or robust regression could better handle uncertainty and complex data patterns.
- Apply propensity score matching or inverse probability weighting to create more comparable patient groups and reduce bias from confounding factors.
- Maybe perform mediation analysis to trace the specific pathways connecting aphasia to readmissions.

**Understanding Cause and Effect:** The quasi-separation pattern in our data prevented us from determining whether PIMs actually cause readmissions or just identify patients who are already sicker. Future work could address this by:
- Measuring baseline medication used at hospital discharge to confirm whether PIMs were prescribed before or during readmission events (taking more time to establish a better timeline) to rule out reverse causation.
- Applying propensity score matching or instrumental variable approaches to help disentangle whether PIMs cause readmissions or simply mark patients with greater underlying severity.
- Using advanced causal inference techniques like instrumental variable analysis or regression discontinuity designs, which can help establish causal relationships even when patients aren't randomly assigned to treatments.
- Testing findings in Medicare/Medicaid populations and different healthcare systems to assess whether our results generalize across different patient groups/settings.

**Adding More Clinical Context:**
- Incorporate clinical measures currently missing from the claims data, such as stroke severity scores, functional assessments, and cognitive impairment indicators. These would improve our models and help account for patient differences we couldn't measure.

---

## Noteworthy Challenges
- Working with the massive OMOP Common Data Model was initially daunting while trying to efficiently query millions of patient records.
- Multiple iterations were needed for the mental health, PIM, and high-risk flagging logic.
- Multiple models were created and optimized for different aspects of this project. Much work was put into studying advanced statistics and learning how to best refactor models for specific needs.

---

## Lessons Learned
- Some statistical analyses postponed until more robust sample sizes achieved.
- Iterative development and stakeholder communication were essential.
- Creating reusable, well-documented cohort tables for future analyses.
- Clinical validation is as critical as statistical rigor in healthcare data science.

---

## Acknowledgements
Special thanks to:
- **Stakeholder Rob Cavanaugh** and his coworker **Chelsea** for their continual guidance.
- **Jonah Bradenday** for working out any OHDSI lab issues.
- **Casey Tilton** whose project we built our initial base aphasia cohort on.
  - His work can be found [here](https://github.com/cbt87/stroke_aftercare).
- **Professor Philip Bogden** for a wonderful final semester.