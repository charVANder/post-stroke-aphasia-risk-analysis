# Prevalence and Impact of PIMs, Mental Health, and Polypharmacy in Post-Stroke Aphasia

Capstone project for our M.S. in Data Science from  Northeastern University.<br>
**Team:** [Evangeline Kim](https://github.com/charVANder) & [Liam O'Connor](https://github.com/LRDOC)<br>
**Stakeholder:** [Rob Cavanaugh](https://roux.northeastern.edu/people/rob-cavanaugh/) (PhD, Asst. Prof., MGH Institute, The Roux Institute)

This OHDSI-Stroke research investigates the prevalence and impact of potentially inappropriate medications (PIMs) and polypharmacy in stroke survivors, with particular focus on patients with aphasia - a population that experiences significant communication and healthcare barriers. We examine high-risk prescribing patterns, explore links to underdiagnosed mental health conditions, and evaluate how these factors relate to hospital readmissions. 

Using the Pharmetrics+ claims dataset and OMOP Common Data Model, we analyzed over 53,000 post-stroke patients to identify medication-related risks that may compromise recovery and increase readmission rates. Our analysis combines descriptive statistics, predictive modeling for risk stratification, and explanatory modeling to quantify clinical impact. This work aims to generate insights for safer prescribing practices and improve post-stroke care for vulnerable populations.

## Website
A GitHub Pages website using the Observable Framework has been created. Click the link [here]() to read our full report and explore the methodology, interactive visualizations, modeling pipelines, and results.

## Setup
### Conda Enviroment:
```bash
conda env create -f environment.yml
conda activate post-stroke-aphasia-risk-analysis-env
```

### Non-conda setup:
```bash
# Creating and activating venv
python3 -m venv env
source env/bin/activate
# For Windows users: env\Scripts\activate

# Installing the required packages
pip install -r requirements.txt
```

## Creating Cohort Tables in the Redshift Database

### 1. Database Credentials
* First ensure that you have a `config.py` file in your root repo. Do NOT push or share this file and make sure that it is properly gitignored.

    In your config file, fill in the following with the credentials provided by OHDSI Admin:

    ```bash
    HOST = "<examplecluster.abc123xyz789.us-west-1.redshift.amazonaws.com>"
    DATABASE = "<Database Name>"
    USER = "<Your Username>"
    PASSWORD = "<Your Password>"
    SCHEMA = "<Your Work Schema>"
    ```
    *The files in the repo will use the config file to connect to the redshift database and run queries*

### 2. Creating the Base Cohort
* To create the base cohort on the redshift database, run the following command:
    ```bash
    make cohort
    ```
    *This will create both the `inpatient_stroke_demo` and `stroke_cohort_w_conditions_demo` tables with the latter being the base cohort that the `eda2.py` file works off of.*

### 3. Initial EDA on Base Cohort
* To create the initial data exploration images using the base cohort, run the following command:
    ```bash
    make eda
    ```

## In-Depth Analyses

### 1. Create Indicator/Flagging tables
* To create the flagging tables necessary for in-depth analysis, run the following command:
    ```bash
    make tables
    ```
    *This will create the `mental_health_flags` table and the `pim_flags` table on the redshift database, containing information on specified health and drug conditions for the cohort. These tables will also be saved as CSVs into your data directory.*

    *NOTE: Creating the PIM table will take long time as it has to go through multiple medications to check for polypharmacy (medication concurrency).*

### 2. Create Statistic Results Report
* To generate the `high_risk_cohort_no_dementia` table and an analysis summary of results, run the following command:
    ```bash
    make summary
    ```
    *This command will also save the table and `results.txt` into your `data` directory*

### 3. Visualizations
* To create analysis visualizations, run the following commands:
    ```bash
    make mh_visuals # for mental health condition graphs
    make pim_visuals # for PIM graphs
    make high_risk_visuals # for high risk cohort graphs
    ```
    *Visualizations will be saved into your `figs` directory*

## Predictive and Explanatory Modeling Pipelines

### 1. Predictive Modeling Pipeline: Hospital Readmission Risk
* Three predictive models (Logistic Regression, Lasso Logistic Regression, and XGBoost) were developed using an 80/20 train-test split with stratified sampling to predict 180-day hospital readmissions in stroke survivors with PIM prescriptions. Models incorporated 36 features including medication burden metrics, mental health comorbidities, medication-diagnosis discordance flags, and engineered interaction terms. Performance was evaluated using AUROC and AUPRC metrics, with SHAP values used to interpret XGBoost feature importance. Additionally, multivariable logistic regression models were fitted to examine independent effects of aphasia on PIM use, high-risk status, and readmission while controlling for confounding variables, with interaction terms tested to explore effect modification by mental health status.

* To run the predictive modeling pipeline, run the following commands:
    ```bash
    make readmissions # extracts hospital readmission data (may take several minutes)
    make features # engineers the features for modeling
    make modeling # trains the predictive models (Logistic, Lasso, and XGBoost). Takes 5-10min.
    make statistics # runs multivariate analyses
    ```

    Alternatively, you can also run them all at once with the following:
    ```bash
    make predictive-pipeline
    ```

### 2. Explanatory Modeling Pipeline: Clinical Impact of PIMs and Hospital Readmissions
* A logistic regression model was developed using the full post-stroke cohort to quantify the association between PIM exposure and 180-day readmissions, examining whether this relationship differs between aphasia and non-aphasia patients. The model included aphasia status, PIM exposure, and seven mental health comorbidities as covariates, with an interaction term tested but removed due to non-significance. L1 regularization (α = 0.01) was applied to handle quasi-separation in the data, with bootstrap confidence intervals (1,000 iterations) calculated for predicted probabilities and G-computation used for marginal effects decomposition. The analysis produced predicted probabilities of readmission for all aphasia/PIM combinations, translated these into expected events per 1,000 patients, and decomposed readmission disparities by their contributing factors. Results revealed an exceptionally strong association between PIMs and readmissions (~100-fold difference), though the quasi-separation pattern indicates this is likely an associative rather than causal relationship.

* To run the explanatory modeling pipeline, run the following commands:
    ```bash
    make clinical-impact
    ```

---

*The base stroke cohort used in this project was built off of the work done in a previous project found [here](https://github.com/cbt87/stroke_aftercare)*
