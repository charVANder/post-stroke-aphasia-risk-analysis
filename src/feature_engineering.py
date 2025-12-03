"""
Feature Engineering for Hospital Readmission Prediction
OHDSI-Stroke Aphasia Research Project

This module creates engineered features from the base dataset for use in
predictive modeling of 30-/90-day hospital readmissions.
"""

import pandas as pd
import numpy as np
import os


def engineer_features(df):
    """
    Create all engineered features for modeling.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with base features

    Returns
    -------
    pandas.DataFrame
        Dataframe with original features plus engineered features
    """

    df = df.copy()

    # INTERACTION FEATURES
    # Aphasia × Mental Health
    df['aphasia_x_mh'] = df['has_aphasia'] * df['has_any_mental_health_condition']

    # Aphasia × High Risk Status
    df['aphasia_x_highrisk'] = df['has_aphasia'] * df['is_high_risk']

    # Aphasia × Polypharmacy (all meds)
    df['aphasia_x_polypharm'] = df['has_aphasia'] * df['has_polypharmacy_all_meds']

    # MEDICATION-DIAGNOSIS DISCORDANCE SCORE
    # Sum of all risk flags (medications without corresponding diagnoses)
    df['med_dx_discordance'] = (
        df['antidep_risk'] +
        df['anxiolytic_risk'] +
        df['hyp_sed_risk'] +
        df['antipsych_risk']
    )

    # Binary indicator of any discordance
    df['has_any_discordance'] = (df['med_dx_discordance'] > 0).astype(int)

    # MENTAL HEALTH BURDEN
    # Count of distinct mental health conditions
    mh_cols = [
        'has_depression',
        'has_anxiety',
        'has_ptsd',
        'has_bipolar',
        'has_schizophrenia',
        'has_psychotic_disorder',
        'has_seizure'
    ]
    df['mh_burden'] = df[mh_cols].sum(axis=1)

    # PIM DIVERSITY
    # Count of different PIM categories (not total count, but distinct types)
    pim_cols = [
        'has_antidepressant',
        'has_anxiolytic',
        'has_antipsychotic',
        'has_hypnotic_sedative'
    ]
    df['pim_diversity'] = df[pim_cols].sum(axis=1)

    # HIGH-RISK MEDICATION COMBINATIONS
    # Concurrent antidepressant + anxiolytic (common risky combination)
    df['antidep_anxio_combo'] = (
        (df['has_antidepressant'] == 1) &
        (df['has_anxiolytic'] == 1)
    ).astype(int)

    # Multiple medication-diagnosis discordances (2+)
    df['multiple_discordances'] = (df['med_dx_discordance'] >= 2).astype(int)

    # High medication burden (10+ total medications)
    df['high_med_burden'] = (df['total_med_count'] >= 10).astype(int)

    # COMPLEX PATIENT INDICATOR
    # Aphasia + Mental Health + PIMs (triple complexity)
    df['complex_patient'] = (
        (df['has_aphasia'] == 1) &
        (df['has_any_mental_health_condition'] == 1) &
        (df['has_any_pim'] == 1)
    ).astype(int)

    return df


def load_and_engineer_data(data_path):
    """
    Load dataset and apply feature engineering.

    Parameters
    data_path : str
        Path to the input CSV file

    Returns
    p.DF
        Dataframe with all engineered features
    """

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} records")

    print("\nData Quality Checks:")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    print(f"  Duplicate subject_ids: {df['subject_id'].duplicated().sum()}")

    print("\nEngineering features...")
    df = engineer_features(df)

    print("\nEngineered Features Summary:")
    engineered_features = [
        'aphasia_x_mh', 'aphasia_x_highrisk', 'aphasia_x_polypharm',
        'med_dx_discordance', 'has_any_discordance',
        'mh_burden', 'pim_diversity',
        'antidep_anxio_combo', 'multiple_discordances', 'high_med_burden',
        'complex_patient'
    ]

    for feat in engineered_features:
        if df[feat].dtype in ['int64', 'int32']:
            print(f"  {feat}: {df[feat].sum():,} / {len(df):,} ({df[feat].mean()*100:.1f}%)")
        else:
            print(f"  {feat}: mean={df[feat].mean():.2f}, std={df[feat].std():.2f}")

    return df


def get_feature_list():
    """
    Get list of all features to use in predictive modeling.

    Returns
    list
        List of feature column names
    """

    feature_cols = [
        # Demographics
        'has_aphasia',

        # Mental health conditions (individual)
        'has_depression',
        'has_anxiety',
        'has_seizure',
        'has_bipolar',
        'has_schizophrenia',
        'has_ptsd',
        'has_psychotic_disorder',

        # Mental health (aggregate)
        'has_any_mental_health_condition',
        'mh_burden',

        # PIM medications (individual categories)
        'has_antidepressant',
        'has_anxiolytic',
        'has_antipsychotic',
        'has_hypnotic_sedative',

        # PIM (aggregate)
        'has_any_pim',
        'total_pim_count',
        'pim_diversity',
        'max_concurrent_pims',

        # Polypharmacy (all medications)
        'has_polypharmacy_all_meds',
        'total_med_count',
        'max_concurrent_meds',

        # Risk scores
        'is_high_risk',
        'total_risk_score',

        # Medication-diagnosis discordance
        'antidep_risk',
        'anxiolytic_risk',
        'hyp_sed_risk',
        'antipsych_risk',
        'med_dx_discordance',
        'has_any_discordance',

        # Interaction features
        'aphasia_x_mh',
        'aphasia_x_highrisk',
        'aphasia_x_polypharm',

        # High-risk combinations
        'antidep_anxio_combo',
        'multiple_discordances',
        'high_med_burden',
        'complex_patient'
    ]

    return feature_cols


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    # Use the dataset with readmissions (after running extract_readmission_data.py)
    INPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_with_readmissions.csv')
    OUTPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_engineered_features.csv')

    # Load and engineer
    df = load_and_engineer_data(INPUT_FILE)

    # Save engineered dataset
    print(f"\nSaving engineered dataset to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done!")

    # Display feature list
    features = get_feature_list()
    print(f"\nTotal features for modeling: {len(features)}")
    print("Features:", features)
