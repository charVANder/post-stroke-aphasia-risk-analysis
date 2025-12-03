import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Connecting to the db w/ config
connection = redshift_connector.connect(
    host=config.HOST,
    port=5439,
    database=config.DATABASE,
    user=config.USER,
    password=config.PASSWORD
)

def create_mh_flags_table(cohort_table, output_table, mental_health_conditions):
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {output_table}")
    connection.commit()
    case_statements = []
    for condition_name, ancestor_id in mental_health_conditions.items():
        if condition_name == "dementia":
            # Handling dementia specifically for 2+ dementia events within cohort period
            case_statement = f'''
            CASE 
                WHEN COUNT(CASE 
                    WHEN co.condition_concept_id IN (
                        SELECT ca.descendant_concept_id 
                        FROM omop_cdm_53_pmtx_202203.concept_ancestor ca 
                        WHERE ca.ancestor_concept_id = {ancestor_id}
                    ) THEN 1 END) >= 2
                THEN 1 ELSE 0 
            END AS has_{condition_name}'''
        else:
            # All other MH conditions still use simple presence logic
            case_statement = f'''
            MAX(CASE 
                WHEN co.condition_concept_id IN (
                    SELECT ca.descendant_concept_id 
                    FROM omop_cdm_53_pmtx_202203.concept_ancestor ca 
                    WHERE ca.ancestor_concept_id = {ancestor_id}
                ) THEN 1 
                ELSE 0 
            END) AS has_{condition_name}'''
        case_statements.append(case_statement)
    all_case_statements = ',\n        '.join(case_statements) # joining everything and adding extra spaces for readability

    # I split it into mh_condition_names joined to get the actual ocndition names (mh_condition_agg so they were aggregated to each patient), and then all the mh flags.
    query = f'''
    WITH mental_health_concepts AS (
        -- Getting all descendant concept IDs from the mental health ancestors
        SELECT DISTINCT descendant_concept_id
        FROM omop_cdm_53_pmtx_202203.concept_ancestor
        WHERE ancestor_concept_id IN ({','.join(map(str, mental_health_conditions.values()))})
    ),

    mh_condition_occurrences AS (
        SELECT
            sc.subject_id,
            co.condition_concept_id
        FROM {cohort_table} sc
        LEFT JOIN omop_cdm_53_pmtx_202203.condition_occurrence co
            ON sc.subject_id = co.person_id
            AND co.condition_start_date >= sc.cohort_start_date
            AND co.condition_end_date <= sc.cohort_end_date
        INNER JOIN mental_health_concepts mhc
            ON co.condition_concept_id = mhc.descendant_concept_id
    ),

    mh_condition_names AS (
        SELECT 
            mco.subject_id,
            c.concept_name
        FROM mh_condition_occurrences mco
        JOIN omop_cdm_53_pmtx_202203.concept c
            ON mco.condition_concept_id = c.concept_id
    ),

    mh_condition_agg AS (
        SELECT 
            subject_id,
            LISTAGG(DISTINCT concept_name, '; ') AS mh_condition_names
        FROM mh_condition_names
        GROUP BY subject_id
    ),

    mental_health_flags AS (
        SELECT 
            sc.subject_id,
            sc.has_aphasia,
            {all_case_statements}
        FROM {cohort_table} sc
        LEFT JOIN omop_cdm_53_pmtx_202203.condition_occurrence co
            ON sc.subject_id = co.person_id
            AND co.condition_start_date >= sc.cohort_start_date
            AND co.condition_end_date <= sc.cohort_end_date
        GROUP BY sc.subject_id, sc.has_aphasia
    )

    SELECT 
        mhf.subject_id,
        mhf.has_aphasia,
        has_seizure,
        has_depression,
        has_anxiety,
        has_bipolar,
        has_schizophrenia,
        has_ptsd,
        has_psychotic_disorder,
        has_dementia,
        CASE 
            WHEN has_seizure = 1 
                OR has_depression = 1 
                OR has_anxiety = 1 
                OR has_bipolar = 1 
                OR has_schizophrenia = 1 
                OR has_ptsd = 1 
                OR has_psychotic_disorder = 1 
                OR has_dementia = 1
            THEN 1 
            ELSE 0 
        END AS has_any_mental_health_condition,
        mca.mh_condition_names
    INTO {output_table}
    FROM mental_health_flags mhf
    LEFT JOIN mh_condition_agg mca
        ON mhf.subject_id = mca.subject_id;
    '''
    cursor.execute(query)
    connection.commit()
    print(f"\nMental health flags table created: {output_table}")

    # Taking a peek just in case
    cursor.execute(f"SELECT * FROM {output_table} LIMIT 10")
    df = cursor.fetch_dataframe()
    print("\nMental Health Flags Preview:")
    print(df)

    # VAN - Adding a summary of counts to use for our presentation
    # NOTE: Also, I think making this into a venn diagram would be good idea!! We can do that w/ the PIMs too.
    cursor.execute(f'''
        SELECT 
            SUM(has_seizure) as seizure_count,
            SUM(has_depression) as depression_count,
            SUM(has_anxiety) as anxiety_count,
            SUM(has_bipolar) as bipolar_count,
            SUM(has_schizophrenia) as schizophrenia_count,
            SUM(has_ptsd) as ptsd_count,
            SUM(has_psychotic_disorder) as psychotic_disorder_count,
            SUM(has_dementia) as dementia_count,
            SUM(has_any_mental_health_condition) as any_mh_condition_count,
            COUNT(*) as total_patients
        FROM {output_table}
    ''')
    summary = cursor.fetch_dataframe()
    print("\nMental Health Condition Counts Summary:")
    print(summary)

    # Saving table to CSV
    print("\nSaving mental health flags table as CSV")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(root_dir, "src", "data")
    os.makedirs(output_dir, exist_ok=True)
    table_path = os.path.join(output_dir, "mental_health_flags.csv")
    cursor.execute(f"SELECT * FROM {output_table}")
    full_df = cursor.fetch_dataframe()
    full_df.to_csv(table_path, index=False)
    print(f"Saved mental health flags table to: {table_path}")

    cursor.close()

# Running function here...
# List of mh conditions - these should be the concept ancestor IDs based off of what our stakeholder gave us
mental_health_conditions = {
    "seizure": 377091,
    "depression": 440383,
    "anxiety": 442077,
    "bipolar": 436665,
    "schizophrenia": 435783,
    "ptsd": 436676,
    "psychotic_disorder": 436073,
    "dementia": 4182210
}
cohort_table = f"{config.SCHEMA}.stroke_cohort_w_conditions_demo" # can adjust as needed
mh_flags_table = f"{config.SCHEMA}.mental_health_flags"

create_mh_flags_table(cohort_table=cohort_table, output_table=mh_flags_table, mental_health_conditions=mental_health_conditions)

