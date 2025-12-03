# Prevalence and Impact of PIMs, Mental Health, and Polypharmacy in Post-Stroke Aphasia

**Project Team:** [Evangeline Kim](https://github.com/charVANder) & [Liam O'Connor](https://github.com/LRDOC)

**Stakeholder:** [Rob Cavanaugh](https://roux.northeastern.edu/people/rob-cavanaugh/) (PhD, Asst. Prof., MGH Institute, The Roux Institute)

---

## Website Contents
- **[HOME](./index#background)** - Background, overview, and objectives of our project.
- **[METHODOLOGY](./methodology)** - A detailed explanation of our project methodology.
- **[INTERACTIVE COHORT EXPLORER](./cohort-explorer)** - An interactive graph to observe prevalence within various cohort populations. Meant to be paired with our statistics report and results reports.
- **[STATISTICS REPORT](./statistics-report)** - Raw statistics and test results of our cohort analysis. All associated visualizations are linked.
- **[PREDICTIVE MODELING REPORT](./predictive-modeling)** - Walkthrough of our predictive modeling pipelines developed to identify stroke survivors at risk for hospital readmission. All associated visualizations are linked.
- **[EXPLANATORY MODELING REPORT](./explanatory-modeling)** - Walkthrough of our explanatory modeling pipeline developed to explore the clinical impact of PIMs. All associated visualizations are linked.
- **[VISUALIZATIONS](./visualizations)** - Various visualizations and interactive graphs created throughout our methodology. Each visual is linked to its specific use case in the results reports.
- **[KEY TAKEAWAYS](./key-takeaways)** - Summarized key observations and interpretations of all results done throughout the project.
- **[CONCLUSIONS](./conclusions)** - Concluding statements, future work, challenges, and acknowledgements.

---

## Background <a id="background"></a>
Stroke remains one of the most significant public health challenges in the United States, affecting over 800,000 people each year and contributing to over $55 billion in annual healthcare costs. Although survival rates have improved, many stroke survivors live with long-term complications that shape their recovery and quality of life.

This project examines how communication barriers, mental health conditions, and medication-related risks affect stroke survivors with aphasia. Using large-scale claims data mapped to the OMOP Common Data Model, we aim to identify prescribing patterns, explore risk factors, and uncover opportunities to improve post-stroke care for a vulnerable and often under-recognized population.

### Strokes
* Every 40 seconds, someone in the U.S. experiences a stroke. As one of the leading causes of serious long-term disability, stroke impacts multiple domains of function, including physical ability, cognition, and communication. These effects extend far beyond the acute event, influencing how patients navigate the healthcare system and manage their recovery over time.

### Aphasia
* Aphasia affects 25–40% of stroke survivors and can impair speaking, understanding, reading, and writing. These communication barriers create significant challenges in clinical settings, where clear patient–provider interaction is essential for accurate diagnosis, shared decision-making, and safe medication management. Many survivors with aphasia also experience mental health conditions (such as depression or anxiety) that may go unrecognized precisely because the communication difficulties associated with aphasia make symptoms harder to express.

### Why Does this Matter?
* Stroke survivors with aphasia face compounded risks. Communication limitations can lead to incomplete diagnostic evaluations, underdiagnosed mental health needs, inappropriate medication prescribing, and overall care coordination. Understanding how aphasia intersects with medication management and mental health is critical for increasing patient safety, reducing preventable readmissions, and improving post-stroke care.

---

## Research Overview
Using the Pharmetrics+ claims dataset and the OMOP Common Data Model, our study examined medication management patterns in more than 53,000 post-stroke patients. We investigated how aphasia status relates to potentially inappropriate medications (PIMs), mental health comorbidities, medication-diagnosis discordance, and polypharmacy. By comparing outcomes between patients with and without aphasia, we aimed to identify high-risk prescribing patterns that may compromise patient safety and highlight opportunities to improve post-stroke care.

---

## Our Main Objective

**Investigate the prevalence and impact of potentially inappropriate medications (PIMs) and polypharmacy in stroke survivors (especially those with aphasia) by identifying high-risk prescribing patterns, exploring links to the underdiagnosed mental health conditions, and evaluating how these factors might be related to hospital readmissions.**
