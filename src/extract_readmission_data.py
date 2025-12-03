"""
Extract Hospital Readmission and ED Visit Data from OMOP Database
OHDSI-Stroke Aphasia Research Project

This script queries the OMOP visit_occurrence table to identify emergency department
visits and hospital readmissions within 180 days after first PIM prescription.
"""

import redshift_connector
import pandas as pd
import numpy as np
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Database connection
print("Connecting to Redshift database...")
connection = redshift_connector.connect(
    host=config.HOST,
    port=5439,
    database=config.DATABASE,
    user=config.USER,
    password=config.PASSWORD
)
cursor = connection.cursor()
print("Connected successfully!\n")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_no_dementia.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_with_readmissions.csv')

# Load existing cohort data with proper CSV handling
print(f"Loading cohort data from {INPUT_FILE}...")
cohort_df = pd.read_csv(
    INPUT_FILE,
    quoting=csv.QUOTE_MINIMAL,
    quotechar='"',
    escapechar=None,
    encoding='utf-8',
    engine='python'  # Python engine handles quoted fields better than C engine
)
print(f"Loaded {len(cohort_df):,} patients\n")

# Validate binary columns for data quality
print("Validating data quality...")
binary_cols = ['has_any_pim', 'has_aphasia', 'has_depression', 'has_anxiety',
               'has_ptsd', 'has_bipolar', 'has_schizophrenia',
               'has_psychotic_disorder', 'has_seizure']

for col in binary_cols:
    if col in cohort_df.columns:
        invalid_values = cohort_df[~cohort_df[col].isin([0, 1, np.nan])][col].unique()
        if len(invalid_values) > 0:
            print(f"WARNING: {col} has invalid values: {invalid_values}")
            raise ValueError(f"Data quality issue detected in {col}")

print("Data validation passed!\n")

# Create temporary table with cohort subject IDs and PIM dates
print("Creating temporary table in Redshift...")
temp_table_name = f"{config.SCHEMA}.temp_readmission_cohort"

# Drop temp table if exists
cursor.execute(f"DROP TABLE IF EXISTS {temp_table_name};")
connection.commit()

# Create temp table
create_temp_table_query = f"""
CREATE TABLE {temp_table_name} (
    subject_id BIGINT,
    first_pim_date DATE
);
"""
cursor.execute(create_temp_table_query)
connection.commit()
print(f"Created temp table: {temp_table_name}\n")

# Prepare cohort data for upload (only patients with PIMs)
cohort_with_pims = cohort_df[cohort_df['has_any_pim'] == 1][['subject_id', 'first_pim_date']].copy()
cohort_with_pims = cohort_with_pims.dropna(subset=['first_pim_date'])
print(f"Uploading {len(cohort_with_pims):,} patients with PIMs to temp table...")

# Insert data in batches
batch_size = 1000
for i in range(0, len(cohort_with_pims), batch_size):
    batch = cohort_with_pims.iloc[i:i+batch_size]

    values = []
    for _, row in batch.iterrows():
        values.append(f"({row['subject_id']}, '{row['first_pim_date']}')")

    insert_query = f"""
    INSERT INTO {temp_table_name} (subject_id, first_pim_date)
    VALUES {', '.join(values)};
    """
    cursor.execute(insert_query)
    connection.commit()

    if (i + batch_size) % 5000 == 0:
        print(f"  Uploaded {min(i + batch_size, len(cohort_with_pims)):,} / {len(cohort_with_pims):,} records...")

print(f"Upload complete!\n")

# Query for ED visits and hospital readmissions
print("Querying visit_occurrence table for readmissions...")
print("This may take several minutes... Rocks are talking to rocks now\n")

readmission_query = f"""
WITH cohort AS (
    SELECT
        subject_id,
        first_pim_date,
        first_pim_date + INTERVAL '30 days' AS day_30_cutoff,
        first_pim_date + INTERVAL '90 days' AS day_90_cutoff,
        first_pim_date + INTERVAL '180 days' AS day_180_cutoff
    FROM {temp_table_name}
),
visits AS (
    SELECT
        vo.person_id AS subject_id,
        vo.visit_start_date,
        vo.visit_concept_id,
        vo.visit_occurrence_id,
        c.concept_name AS visit_type
    FROM omop_cdm_53_pmtx_202203.visit_occurrence vo
    INNER JOIN omop_cdm_53_pmtx_202203.concept c
        ON vo.visit_concept_id = c.concept_id
    WHERE vo.person_id IN (SELECT subject_id FROM cohort)
        AND vo.visit_concept_id IN (
            -- Emergency Room Visit
            9203,
            -- Inpatient Visit
            9201,
            -- Inpatient Hospital
            262
        )
),
readmissions AS (
    SELECT
        c.subject_id,
        c.first_pim_date,
        v.visit_start_date,
        v.visit_type,
        v.visit_occurrence_id,
        -- Calculate days between first PIM and visit
        DATEDIFF(day, c.first_pim_date, v.visit_start_date) AS days_to_visit,
        -- Flag if visit is within time windows
        CASE
            WHEN v.visit_start_date > c.first_pim_date
                AND v.visit_start_date <= c.day_30_cutoff
            THEN 1 ELSE 0
        END AS is_30day_visit,
        CASE
            WHEN v.visit_start_date > c.first_pim_date
                AND v.visit_start_date <= c.day_90_cutoff
            THEN 1 ELSE 0
        END AS is_90day_visit,
        CASE
            WHEN v.visit_start_date > c.first_pim_date
                AND v.visit_start_date <= c.day_180_cutoff
            THEN 1 ELSE 0
        END AS is_180day_visit
    FROM cohort c
    INNER JOIN visits v ON c.subject_id = v.subject_id
    WHERE v.visit_start_date > c.first_pim_date  -- Only visits AFTER first PIM
        AND v.visit_start_date <= c.day_180_cutoff  -- Within 180 days
)
SELECT
    subject_id,
    -- Count of readmissions in each window
    SUM(is_30day_visit) AS readmissions_30d_count,
    SUM(is_90day_visit) AS readmissions_90d_count,
    SUM(is_180day_visit) AS readmissions_180d_count,
    -- Binary flags for any readmission
    CASE WHEN SUM(is_30day_visit) > 0 THEN 1 ELSE 0 END AS has_30day_readmission,
    CASE WHEN SUM(is_90day_visit) > 0 THEN 1 ELSE 0 END AS has_90day_readmission,
    CASE WHEN SUM(is_180day_visit) > 0 THEN 1 ELSE 0 END AS has_180day_readmission,
    -- Days to first readmission
    MIN(CASE WHEN is_30day_visit = 1 THEN days_to_visit ELSE NULL END) AS days_to_first_30d_readmission,
    MIN(CASE WHEN is_90day_visit = 1 THEN days_to_visit ELSE NULL END) AS days_to_first_90d_readmission,
    MIN(CASE WHEN is_180day_visit = 1 THEN days_to_visit ELSE NULL END) AS days_to_first_180d_readmission
FROM readmissions
GROUP BY subject_id;
"""

cursor.execute(readmission_query)
results = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]

# Convert to DataFrame
readmission_df = pd.DataFrame(results, columns=column_names)
print(f"Retrieved readmission data for {len(readmission_df):,} patients with visits\n")

# Clean up temporary table
print("Cleaning up temporary table...")
cursor.execute(f"DROP TABLE IF EXISTS {temp_table_name};")
connection.commit()
cursor.close()
connection.close()
print("Database connection closed.\n")

# Merge with original cohort
print("Merging readmission data with cohort...")
final_df = cohort_df.merge(
    readmission_df,
    on='subject_id',
    how='left'  # Keep all patients, even those without readmissions
)

# Fill NaN values with 0 for patients without readmissions
readmission_cols = [
    'readmissions_30d_count', 'readmissions_90d_count', 'readmissions_180d_count',
    'has_30day_readmission', 'has_90day_readmission', 'has_180day_readmission',
    'days_to_first_30d_readmission', 'days_to_first_90d_readmission',
    'days_to_first_180d_readmission'
]

for col in readmission_cols:
    if col in final_df.columns:
        if 'has_' in col or 'count' in col:
            final_df[col] = final_df[col].fillna(0).astype(int)
        # Keep days_to_first as float (NaN means no readmission)

print(f"\nFinal dataset: {len(final_df):,} patients × {len(final_df.columns)} columns")

# Summary statistics
print("\n" + "="*60)
print("READMISSION SUMMARY STATISTICS")
print("="*60)

total_patients = len(final_df)
patients_with_pims = (final_df['has_any_pim'] == 1).sum()

print(f"\nTotal Patients: {total_patients:,}")
print(f"Patients with PIMs: {patients_with_pims:,} ({patients_with_pims/total_patients*100:.1f}%)")
print(f"Patients without PIMs: {total_patients - patients_with_pims:,}")

print("\n30-Day Readmissions:")
n_30d = final_df['has_30day_readmission'].sum()
print(f"  Total: {n_30d:,} / {patients_with_pims:,} ({n_30d/patients_with_pims*100:.1f}% of patients with PIMs)")
print(f"  Aphasia: {final_df[final_df['has_aphasia']==1]['has_30day_readmission'].sum():,}")
print(f"  No Aphasia: {final_df[final_df['has_aphasia']==0]['has_30day_readmission'].sum():,}")

print("\n90-Day Readmissions:")
n_90d = final_df['has_90day_readmission'].sum()
print(f"  Total: {n_90d:,} / {patients_with_pims:,} ({n_90d/patients_with_pims*100:.1f}% of patients with PIMs)")
print(f"  Aphasia: {final_df[final_df['has_aphasia']==1]['has_90day_readmission'].sum():,}")
print(f"  No Aphasia: {final_df[final_df['has_aphasia']==0]['has_90day_readmission'].sum():,}")

print("\n180-Day Readmissions:")
n_180d = final_df['has_180day_readmission'].sum()
print(f"  Total: {n_180d:,} / {patients_with_pims:,} ({n_180d/patients_with_pims*100:.1f}% of patients with PIMs)")
print(f"  Aphasia: {final_df[final_df['has_aphasia']==1]['has_180day_readmission'].sum():,}")
print(f"  No Aphasia: {final_df[final_df['has_aphasia']==0]['has_180day_readmission'].sum():,}")

print("\nMean Days to First Readmission (among those with readmissions):")
print(f"  30-day window: {final_df['days_to_first_30d_readmission'].mean():.1f} days")
print(f"  90-day window: {final_df['days_to_first_90d_readmission'].mean():.1f} days")
print(f"  180-day window: {final_df['days_to_first_180d_readmission'].mean():.1f} days")

print("="*60 + "\n")

# Save to CSV
print(f"Saving enriched dataset to {OUTPUT_FILE}...")
final_df.to_csv(
    OUTPUT_FILE,
    index=False,
    quoting=csv.QUOTE_MINIMAL,
    quotechar='"',
    encoding='utf-8'
)
print("Done!")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Update feature_engineering.py to use the new dataset:")
print(f"   INPUT_FILE = '{OUTPUT_FILE}'")
print("2. Run feature engineering:")
print("   python src/feature_engineering.py")
print("3. Proceed with predictive modeling:")
print("   python src/predictive_modeling.py")
print("="*60)
