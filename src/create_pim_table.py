
import redshift_connector
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
# V3: Filters to only include medications taken orally (PO route)
# V3.5: Now includes both PIM-specific analysis AND all-medication polypharmacy analysis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


# GitHub URLs for PIM medication CSVs (from Rob's (the stakeholder) AoU research)
PIM_CSV_URLS = {
    'hypnotic_sedative': 'https://raw.githubusercontent.com/cnwong/AoU_data/refs/heads/main/hyp_sed_v8.csv',
    'antipsychotic': 'https://raw.githubusercontent.com/cnwong/AoU_data/refs/heads/main/antipsych_v8.csv',
    'antidepressant': 'https://raw.githubusercontent.com/cnwong/AoU_data/refs/heads/main/antidepress_v8.csv',
    'anxiolytic': 'https://raw.githubusercontent.com/cnwong/AoU_data/refs/heads/main/anxiolytic_v8.csv'
}

# PO (oral) route concept IDs from clinical review
PO_ROUTE_CONCEPT_IDS = [4132161, 4132711, 4132254, 4167540, 4292110, 4186834, 3661892, 4168665]


def load_pim_concept_ids():
    """
    Loads from GitHub CSVs

    Returns:
        dict: {category_name: [concept_ids]}
    """
    print("\nLoading PIM concept IDs from GitHub...")
    pim_concepts = {}

    for category, url in PIM_CSV_URLS.items():
        try:
            df = pd.read_csv(url)
            concept_ids = df['concept_id'].unique().tolist()  # CSV has 'concept_id' column
            pim_concepts[category] = concept_ids
            print(f"  {category}: {len(concept_ids)} unique concept IDs")
        except Exception as e:
            print(f"  ERROR {category}: {e}")
            pim_concepts[category] = []
    total_concepts = sum(len(ids) for ids in pim_concepts.values())
    print(f"Total PIM concepts loaded: {total_concepts}\n")

    return pim_concepts


def fetch_pim_exposures(cursor, schema, cohort_table, pim_concepts):
    """
    Fetch drug exposures for PIMs in the cohort (oral route only)

    Args:
        cursor: Database cursor (config.py)
        schema: Database schema (config.py)
        cohort_table: Name of cohort table
        pim_concepts: Dictionary of {category: [concept_ids]}

    Returns:
        pandas.DF with PIM exposures
    """

    # flatten all concept IDs with category labels
    all_concept_ids = []
    concept_to_category = {}

    for category, concept_ids in pim_concepts.items():
        all_concept_ids.extend(concept_ids)
        for cid in concept_ids:
            concept_to_category[cid] = category

    if not all_concept_ids:
        print("ERROR: No PIM concept IDs loaded")
        return pd.DataFrame()

    # Create concept ID string for SQL IN clause
    # need this to be a string of comma-separated values for sql
    concept_ids_str = ', '.join(str(cid) for cid in all_concept_ids)
    po_routes_str = ', '.join(str(rid) for rid in PO_ROUTE_CONCEPT_IDS)

    query = f'''
        SELECT
            de.person_id as subject_id,
            de.drug_concept_id,
            de.drug_exposure_start_date,
            de.drug_exposure_end_date,
            de.days_supply,
            de.route_concept_id
        FROM omop_cdm_53_pmtx_202203.drug_exposure de
        INNER JOIN {schema}.{cohort_table} sc
            ON de.person_id = sc.subject_id
            AND de.drug_exposure_start_date >= sc.cohort_start_date
            AND de.drug_exposure_start_date <= sc.cohort_end_date
        WHERE de.drug_concept_id IN ({concept_ids_str})
            AND de.drug_exposure_start_date IS NOT NULL
            AND de.route_concept_id IN ({po_routes_str})
    '''

    cursor.execute(query)
    df = cursor.fetch_dataframe()

    # Add cat column
    df['pim_category'] = df['drug_concept_id'].map(concept_to_category)

    # Handle null end dates - use start_date + days_supply (or start_date + 30 as fallback)
    df['drug_exposure_end_date'] = pd.to_datetime(df['drug_exposure_end_date'], errors='coerce')
    df['drug_exposure_start_date'] = pd.to_datetime(df['drug_exposure_start_date'])

    # Fill missing end dates
    mask_null_end = df['drug_exposure_end_date'].isna()
    df.loc[mask_null_end, 'drug_exposure_end_date'] = df.loc[mask_null_end].apply(
        lambda row: row['drug_exposure_start_date'] + pd.Timedelta(days=int(row['days_supply']) if pd.notna(row['days_supply']) and row['days_supply'] > 0 else 30),
        axis=1
    )

    print(f"Fetched {len(df)} PO (oral) PIM exposure records for {df['subject_id'].nunique()} patients")
    print(f"Date range: {df['drug_exposure_start_date'].min()} to {df['drug_exposure_end_date'].max()}")

    return df


def fetch_all_med_exposures(cursor, schema, cohort_table):
    """
    Fetch ALL drug exposures in the cohort (oral route only) - not just PIMs

    Args:
        cursor: Database cursor (config.py)
        schema: Database schema (config.py)
        cohort_table: Name of cohort table

    Returns:
        p.DF with all medication exposures
    """

    po_routes_str = ', '.join(str(rid) for rid in PO_ROUTE_CONCEPT_IDS)

    query = f'''
        SELECT
            de.person_id as subject_id,
            de.drug_concept_id,
            de.drug_exposure_start_date,
            de.drug_exposure_end_date,
            de.days_supply,
            de.route_concept_id
        FROM omop_cdm_53_pmtx_202203.drug_exposure de
        INNER JOIN {schema}.{cohort_table} sc
            ON de.person_id = sc.subject_id
            AND de.drug_exposure_start_date >= sc.cohort_start_date
            AND de.drug_exposure_start_date <= sc.cohort_end_date
        WHERE de.drug_exposure_start_date IS NOT NULL
            AND de.route_concept_id IN ({po_routes_str})
    '''

    cursor.execute(query)
    df = cursor.fetch_dataframe()

    # Handle null end dates - use start_date + days_supply (or start_date + 30 as fallback)
    df['drug_exposure_end_date'] = pd.to_datetime(df['drug_exposure_end_date'], errors='coerce')
    df['drug_exposure_start_date'] = pd.to_datetime(df['drug_exposure_start_date'])

    # Fill missing end dates
    mask_null_end = df['drug_exposure_end_date'].isna()
    df.loc[mask_null_end, 'drug_exposure_end_date'] = df.loc[mask_null_end].apply(
        lambda row: row['drug_exposure_start_date'] + pd.Timedelta(days=int(row['days_supply']) if pd.notna(row['days_supply']) and row['days_supply'] > 0 else 30),
        axis=1
    )

    print(f"Fetched {len(df)} PO (oral) medication exposure records for {df['subject_id'].nunique()} patients")
    print(f"Date range: {df['drug_exposure_start_date'].min()} to {df['drug_exposure_end_date'].max()}")

    return df


def calc_concurrent_pims(exposures_df, polypharmacy_threshold=5, min_concurrent_days=30):
    """
    calc concurrent PIM usage and identify polypharmacy

    Polypharmacy definition: 5+ distinct PIMs taken concurrently for 30+ consecutive days

    Args:
        exposures_df: DataFrame with PIM exposures
        polypharmacy_threshold: Minimum number of concurrent PIMs (default: 5)
        min_concurrent_days: Minimum consecutive days (default: 30)

    Returns:
        pandas.DataFrame with one row per subject_id containing:
        - max_concurrent_pims: Maximum number of PIMs taken simultaneously
        - max_concurrent_days: Longest period with threshold+ concurrent PIMs
        - has_polypharmacy: Binary flag for PIM polypharmacy
    """
    print(f"\nCalculating concurrent PIM usage (threshold: {polypharmacy_threshold}+ PIMs for {min_concurrent_days}+ days)...")

    if exposures_df.empty:
        return pd.DataFrame(columns=['subject_id', 'max_concurrent_pims', 'max_concurrent_days', 'has_polypharmacy'])

    results = []

    for subject_id, group in exposures_df.groupby('subject_id'):
        # Get all unique exposure windows
        exposures = group[['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']].values

        # Find all unique dates across all exposures
        all_dates = set()
        # for each exposure, add all dates in the range to all_dates while accounting for overlaps
        for _, start, end in exposures:
            current_date = start
            while current_date <= end:
                all_dates.add(current_date)
                current_date += pd.Timedelta(days=1)

        if not all_dates:
            results.append({
                'subject_id': subject_id,
                'max_concurrent_pims': 0,
                'max_concurrent_days': 0,
                'has_polypharmacy': 0
            })
            continue

        sorted_dates = sorted(all_dates) # sort uq dates

        # For each date count concurr uq drugs
        date_to_concurrent = {}
        for date in sorted_dates:
            concurrent_drugs = set()
            # for each exposure, check if date falls within start-end
            for drug_id, start, end in exposures:
                if start <= date <= end:
                    concurrent_drugs.add(drug_id)
            date_to_concurrent[date] = len(concurrent_drugs)

        # max concurrent and longest streak above threshold
        max_concurrent = max(date_to_concurrent.values()) if date_to_concurrent else 0

        # longest consecutive period with threshold+ concurrent PIMs
        max_streak_days = 0
        current_streak = 0
        prev_date = None

        for date in sorted_dates:
            if date_to_concurrent[date] >= polypharmacy_threshold:
                if prev_date is None or (date - prev_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                max_streak_days = max(max_streak_days, current_streak)
            else:
                current_streak = 0
            prev_date = date

        has_polypharmacy = 1 if max_streak_days >= min_concurrent_days else 0

        results.append({
            'subject_id': subject_id,
            'max_concurrent_pims': int(max_concurrent),
            'max_concurrent_days': int(max_streak_days),
            'has_polypharmacy': has_polypharmacy
        })

    results_df = pd.DataFrame(results)

    # Summary stats
    poly_count = results_df['has_polypharmacy'].sum()
    print(f"  Polypharmacy detected in {poly_count} patients ({poly_count/len(results_df)*100:.1f}%)")
    print(f"  Max concurrent PIMs observed: {results_df['max_concurrent_pims'].max()}")
    print(f"  Longest concurrent period: {results_df['max_concurrent_days'].max()} days")

    return results_df


def calc_concurrent_all_meds(exposures_df, polypharmacy_threshold=5, min_concurrent_days=30):
    """
    Calculate concurrent medication usage across ALL medications (not just PIMs)

    Polypharmacy definition: 5+ distinct medications taken concurrently for 30+ consecutive days

    Args:
        exposures_df: DataFrame with all medication exposures
        polypharmacy_threshold: Minimum number of concurrent medications (default: 5)
        min_concurrent_days: Minimum consecutive days (default: 30)

    Returns:
        pandas.DataFrame with one row per subject_id containing:
        - max_concurrent_meds: Maximum number of medications taken simultaneously
        - max_concurrent_meds_days: Longest period with threshold+ concurrent medications
        - has_polypharmacy_all_meds: Binary flag for all-medication polypharmacy
    """
    print(f"\nCalculating concurrent ALL medication usage (threshold: {polypharmacy_threshold}+ meds for {min_concurrent_days}+ days)...")

    if exposures_df.empty:
        return pd.DataFrame(columns=['subject_id', 'max_concurrent_meds', 'max_concurrent_meds_days', 'has_polypharmacy_all_meds'])

    results = []

    for subject_id, group in exposures_df.groupby('subject_id'):
        # Get all unique exposure windows
        exposures = group[['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']].values

        # Find all unique dates across all exposures
        all_dates = set()
        # for each exposure, add all dates in the range to all_dates while accounting for overlaps
        for _, start, end in exposures:
            current_date = start
            while current_date <= end:
                all_dates.add(current_date)
                current_date += pd.Timedelta(days=1)

        if not all_dates:
            results.append({
                'subject_id': subject_id,
                'max_concurrent_meds': 0,
                'max_concurrent_meds_days': 0,
                'has_polypharmacy_all_meds': 0
            })
            continue

        sorted_dates = sorted(all_dates) # sort uq dates

        # For each date count concurr uq drugs
        date_to_concurrent = {}
        for date in sorted_dates:
            concurrent_drugs = set()
            # for each exposure, check if date falls within start-end
            for drug_id, start, end in exposures:
                if start <= date <= end:
                    concurrent_drugs.add(drug_id)
            date_to_concurrent[date] = len(concurrent_drugs)

        # max concurrent and longest streak above threshold
        max_concurrent = max(date_to_concurrent.values()) if date_to_concurrent else 0

        # longest consecutive period with threshold+ concurrent medications
        max_streak_days = 0
        current_streak = 0
        prev_date = None

        for date in sorted_dates:
            if date_to_concurrent[date] >= polypharmacy_threshold:
                if prev_date is None or (date - prev_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                max_streak_days = max(max_streak_days, current_streak)
            else:
                current_streak = 0
            prev_date = date

        has_polypharmacy = 1 if max_streak_days >= min_concurrent_days else 0

        results.append({
            'subject_id': subject_id,
            'max_concurrent_meds': int(max_concurrent),
            'max_concurrent_meds_days': int(max_streak_days),
            'has_polypharmacy_all_meds': has_polypharmacy
        })

    results_df = pd.DataFrame(results)

    # Summary stats
    poly_count = results_df['has_polypharmacy_all_meds'].sum()
    print(f"  All-medication polypharmacy detected in {poly_count} patients ({poly_count/len(results_df)*100:.1f}%)")
    print(f"  Max concurrent medications observed: {results_df['max_concurrent_meds'].max()}")
    print(f"  Longest concurrent period: {results_df['max_concurrent_meds_days'].max()} days")

    return results_df


def create_pim_flags_table(cursor, schema, cohort_table, output_table='pim_flags',
                           polypharmacy_threshold=5, min_concurrent_days=30):
    """
    Create comprehensive medication analysis table with both PIM-specific and all-medication metrics

    Analyzes two aspects of medication usage:
    1. PIM-specific analysis: Tracks specific categories of PIMs and concurrent PIM usage
    2. All-medication analysis: Tracks polypharmacy across ALL medications (not just PIMs)

    Args:
        cursor: Database cursor
        schema: Database schema
        cohort_table: Name of cohort table
        output_table: Name of output table (default: 'pim_flags_v3')
        polypharmacy_threshold: Minimum concurrent medications for polypharmacy (default: 5)
        min_concurrent_days: Minimum consecutive days (default: 30)

    Table columns include:
        - PIM-specific: has_[category], total_pim_count, max_concurrent_pims, has_polypharmacy
        - All-medication: total_med_count, max_concurrent_meds, has_polypharmacy_all_meds
    """
    print(f"\n{'=-'*80}")
    print(f"Creating comprehensive medication analysis table: {schema}.{output_table}")
    print(f"Analysis includes: PIM-specific metrics + All-medication polypharmacy")
    print(f"Route filter: PO (oral) only")
    print(f"{'=-'*80}")

    # Load PIM concept IDs
    pim_concepts = load_pim_concept_ids()

    # Fetch PIM exposures
    exposures_df = fetch_pim_exposures(cursor, schema, cohort_table, pim_concepts)

    if exposures_df.empty:
        print("No PIM exposures found! Creating empty table.")
        return

    # Calculate concurrent PIM usage
    concurrent_df = calc_concurrent_pims(exposures_df, polypharmacy_threshold, min_concurrent_days)

    # Fetch ALL medication exposures (not just PIMs, PO route only, including non-PIMs)
    print("\n" + "=-"*40)
    print("Fetching ALL medication exposures...")
    print("=-"*40)
    all_meds_df = fetch_all_med_exposures(cursor, schema, cohort_table)

    # Calculate concurrent ALL medication usage
    all_meds_concurrent_df = calc_concurrent_all_meds(all_meds_df, polypharmacy_threshold, min_concurrent_days)

    # Calculate category flags
    print("\nCalculating PIM category flags...")
    category_flags = exposures_df.groupby(['subject_id', 'pim_category'])['drug_concept_id'].count().unstack(fill_value=0)
    category_flags = (category_flags > 0).astype(int)
    category_flags.columns = ['has_' + col for col in category_flags.columns]

    # Calc summary stats per patient for PIMs
    pim_summary_stats = exposures_df.groupby('subject_id').agg({
        'drug_concept_id': 'nunique',
        'drug_exposure_start_date': 'min',
        'drug_exposure_end_date': 'max'
    }).rename(columns={
        'drug_concept_id': 'total_pim_count',
        'drug_exposure_start_date': 'first_pim_date',
        'drug_exposure_end_date': 'last_pim_date'
    })

    # Calc summary stats per patient for ALL medications
    all_meds_summary_stats = all_meds_df.groupby('subject_id').agg({
        'drug_concept_id': 'nunique',
        'drug_exposure_start_date': 'min',
        'drug_exposure_end_date': 'max'
    }).rename(columns={
        'drug_concept_id': 'total_med_count',
        'drug_exposure_start_date': 'first_med_date',
        'drug_exposure_end_date': 'last_med_date'
    })

    # Combine all metrics
    final_df = pim_summary_stats.join(category_flags, how='outer').join(concurrent_df.set_index('subject_id'), how='outer')
    final_df = final_df.join(all_meds_summary_stats, how='outer').join(all_meds_concurrent_df.set_index('subject_id'), how='outer')
    final_df = final_df.fillna(0)

    # Add has_any_pim flag
    final_df['has_any_pim'] = (final_df['total_pim_count'] > 0).astype(int)

    # Ensure all expected category columns exist
    for category in ['has_hypnotic_sedative', 'has_antipsychotic', 'has_antidepressant', 'has_anxiolytic']:
        if category not in final_df.columns:
            final_df[category] = 0

    # Convert dates to strings for SQL
    final_df['first_pim_date'] = pd.to_datetime(final_df['first_pim_date']).dt.strftime('%Y-%m-%d')
    final_df['last_pim_date'] = pd.to_datetime(final_df['last_pim_date']).dt.strftime('%Y-%m-%d')
    final_df['first_med_date'] = pd.to_datetime(final_df['first_med_date']).dt.strftime('%Y-%m-%d')
    final_df['last_med_date'] = pd.to_datetime(final_df['last_med_date']).dt.strftime('%Y-%m-%d')

    # Reset index to get subject_id as column
    final_df = final_df.reset_index()

    # Save CSV to data directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.makedirs(os.path.join(root_dir, 'src', 'data'), exist_ok=True)
    output_csv_path = os.path.join(root_dir, 'src', 'data', f'{output_table}.csv')
    final_df.to_csv(output_csv_path, index=False)
    print(f"\nSaved {output_table}.csv to: {output_csv_path}")

    print(f"\nFinal table will have {len(final_df)} rows")
    print("\nColumn summary:")
    for col in final_df.columns:
        if col.startswith('has_'):
            count = final_df[col].sum()
            pct = count / len(final_df) * 100
            print(f"  {col}: {count} ({pct:.1f}%)")

    # Drop existing table
    print(f"\nDropping existing table if exists...")
    drop_query = f'DROP TABLE IF EXISTS {schema}.{output_table}'
    cursor.execute(drop_query)

    # Create table schema
    print(f"Creating table structure...")
    create_query = f'''
        CREATE TABLE {schema}.{output_table} (
            subject_id BIGINT,
            has_hypnotic_sedative INTEGER,
            has_antipsychotic INTEGER,
            has_antidepressant INTEGER,
            has_anxiolytic INTEGER,
            has_any_pim INTEGER,
            total_pim_count INTEGER,
            max_concurrent_pims INTEGER,
            max_concurrent_days INTEGER,
            has_polypharmacy INTEGER,
            first_pim_date DATE,
            last_pim_date DATE,
            total_med_count INTEGER,
            max_concurrent_meds INTEGER,
            max_concurrent_meds_days INTEGER,
            has_polypharmacy_all_meds INTEGER,
            first_med_date DATE,
            last_med_date DATE
        )
    '''
    cursor.execute(create_query)

    # Insert data in batches to avoid prepared statement cache issues
    print(f"Inserting {len(final_df)} rows in batches...")

    batch_size = 1000
    total_batches = (len(final_df) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(final_df))
        batch_df = final_df.iloc[start_idx:end_idx]

        # Build multi-row INSERT
        # (it kills itself if we try to use prepared statements with too many rows)
        values_list = []
        for _, row in batch_df.iterrows():
            values = f'''(
                {int(row['subject_id'])},
                {int(row['has_hypnotic_sedative'])},
                {int(row['has_antipsychotic'])},
                {int(row['has_antidepressant'])},
                {int(row['has_anxiolytic'])},
                {int(row['has_any_pim'])},
                {int(row['total_pim_count'])},
                {int(row['max_concurrent_pims'])},
                {int(row['max_concurrent_days'])},
                {int(row['has_polypharmacy'])},
                '{row['first_pim_date']}',
                '{row['last_pim_date']}',
                {int(row['total_med_count'])},
                {int(row['max_concurrent_meds'])},
                {int(row['max_concurrent_meds_days'])},
                {int(row['has_polypharmacy_all_meds'])},
                '{row['first_med_date']}',
                '{row['last_med_date']}'
            )'''
            values_list.append(values)

        insert_query = f'''
            INSERT INTO {schema}.{output_table} VALUES
            {','.join(values_list)}
        '''
        cursor.execute(insert_query)

        if (batch_num + 1) % 10 == 0 or batch_num == total_batches - 1:
            print(f"  Inserted {end_idx}/{len(final_df)} rows...")

    print(f"\n{'='*80}")
    print(f"Table {schema}.{output_table} created successfully!")
    print(f"Includes PIM-specific analysis + all-medication polypharmacy metrics")
    print(f"{'='*80}\n")


def main():
    connection = None

    try:
        print("Connecting to Redshift...")
        connection = redshift_connector.connect(
            host=config.HOST,
            port=5439,
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD
        )
        cursor = connection.cursor()

        # Configuration
        schema = config.SCHEMA
        cohort_table = 'stroke_cohort_w_conditions_demo'
        output_table = 'pim_flags'
        polypharmacy_threshold = 5  # 5+ concurrent medications
        min_concurrent_days = 30     # 30+ consecutive days

        # Create comprehensive medication analysis table (PIMs + all medications)
        create_pim_flags_table(
            cursor=cursor,
            schema=schema,
            cohort_table=cohort_table,
            output_table=output_table,
            polypharmacy_threshold=polypharmacy_threshold,
            min_concurrent_days=min_concurrent_days
        )

        connection.commit()
        print("Changes committed to database.")

    except Exception as e:
        print(f"\nERROR: {e}")
        if connection:
            connection.rollback()
        raise

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()