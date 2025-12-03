import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

#Connect to the redshift database
connection = redshift_connector.connect(
     host=config.HOST,
     port=5439,
     database=config.DATABASE,
     user=config.USER,
     password=config.PASSWORD
  )

def create_cohort(intermediate_table, final_table):
    ''' Stroke cohort w/ aphasia, dysphagia, and dysarthria indicators (based off of Casey's code)
    Parameters:
        intermediate_table: Name of intermediate table to store initial stroke data.
        final_table: Name of final cohort table.
    '''
    cursor = connection.cursor()

    # Inpatient stroke events
    inpatient_stroke_query = f'''
    SELECT 
        co.condition_occurrence_id, 
        co.person_id, 
        co.condition_concept_id, 
        co.condition_start_date, 
        co.condition_end_date, 
        vo.visit_start_date, 
        vo.visit_end_date, 
        vo.discharge_to_concept_id 
    INTO {intermediate_table}
    FROM omop_cdm_53_pmtx_202203.condition_occurrence co
    INNER JOIN omop_cdm_53_pmtx_202203.visit_occurrence vo 
        ON co.visit_occurrence_id = vo.visit_occurrence_id
    WHERE vo.visit_concept_id IN (
        SELECT ca.descendant_concept_id 
        FROM omop_cdm_53_pmtx_202203.concept_ancestor ca 
        INNER JOIN omop_cdm_53_pmtx_202203.concept c 
            ON ca.descendant_concept_id = c.concept_id 
        WHERE ca.ancestor_concept_id IN (9201, 9203, 262)  -- inpatient visit types
    )
    AND co.condition_concept_id IN (
        SELECT ca.descendant_concept_id 
        FROM omop_cdm_53_pmtx_202203.concept_ancestor ca 
        INNER JOIN omop_cdm_53_pmtx_202203.concept c 
            ON ca.descendant_concept_id = c.concept_id 
        WHERE ca.ancestor_concept_id IN (
            372924, 375557, 376713, 443454, 441874, 439847, 432923  -- stroke-related concepts
        )
    );
    '''
    cursor.execute(inpatient_stroke_query)
    connection.commit()

    # Stroke cohort w/ communication condition flags for aphasia, dysphagia, and dysarthria
    create_cohort_w_conditions_query = f'''
    WITH first_stroke_occurrence AS (
        SELECT
            condition_occurrence_id,
            person_id,
            condition_concept_id,
            condition_start_date,
            condition_end_date,
            visit_start_date,
            visit_end_date,
            discharge_to_concept_id,
            ROW_NUMBER() OVER (PARTITION BY person_id ORDER BY condition_start_date ASC) AS row_num
        FROM {intermediate_table}
    ),
    distinct_stroke_occurrence AS (
        SELECT
            condition_occurrence_id,
            person_id,
            condition_concept_id,
            condition_start_date,
            condition_end_date,
            DENSE_RANK() OVER (PARTITION BY person_id ORDER BY condition_start_date ASC) AS distinct_rank
        FROM first_stroke_occurrence
    ),
    multiple_stroke_occurrence AS (
        SELECT f1.person_id
        FROM distinct_stroke_occurrence f1
        JOIN distinct_stroke_occurrence f2 
            ON f1.person_id = f2.person_id 
            AND f1.distinct_rank = 1
            AND f2.distinct_rank = 2
        WHERE DATEDIFF(day, f1.condition_start_date, f2.condition_start_date) <= 180
        GROUP BY f1.person_id
    ),
    stroke_cohort AS (
        SELECT
            f.person_id AS subject_id,
            f.condition_occurrence_id,
            f.condition_concept_id,
            f.condition_start_date AS cohort_start_date,
            f.condition_end_date,
            DATEADD(day, 180, f.condition_start_date) AS six_months_after_index,
            f.visit_start_date,
            f.visit_end_date,
            f.discharge_to_concept_id,
            CASE 
                WHEN f.discharge_to_concept_id IN (581476, 0, 38004519, 9202) THEN 'Home'
                WHEN f.discharge_to_concept_id IN (38004285, 8920) THEN 'Inpatient Rehabilitation Facility'
                WHEN f.discharge_to_concept_id IN (8863, 38004277, 8676) THEN 'SNF/LTC'
                WHEN f.discharge_to_concept_id IN (8717, 32254, 32276) THEN 'Acute Care'
                WHEN f.discharge_to_concept_id IN (8546, 8951, 38004284, 38003619) THEN 'Other'
            END AS discharge_location,
            op.observation_period_start_date,
            op.observation_period_end_date AS cohort_end_date,
            op.observation_period_id
        FROM first_stroke_occurrence f
        INNER JOIN omop_cdm_53_pmtx_202203.observation_period op 
            ON op.person_id = f.person_id
        WHERE f.person_id IN (SELECT person_id FROM multiple_stroke_occurrence)
            AND f.row_num = 1
            AND f.condition_start_date >= DATEADD(day, 180, op.observation_period_start_date)
            AND op.observation_period_end_date >= DATEADD(day, 180, f.condition_start_date)
    ),

    -- Aphasia logic
    aphasia_occurrence AS (
        SELECT condition_occurrence_id, person_id, condition_start_date,
               DENSE_RANK() OVER (PARTITION BY person_id ORDER BY condition_start_date) AS aphasia_rank
        FROM omop_cdm_53_pmtx_202203.condition_occurrence
        WHERE condition_concept_id IN (440424, 40480002)
    ),
    valid_aphasia_occurrence AS (
        SELECT ao.person_id
        FROM stroke_cohort sc
        JOIN aphasia_occurrence ao 
            ON sc.subject_id = ao.person_id
            AND ao.condition_start_date >= sc.cohort_start_date
        GROUP BY ao.person_id
    ),
    multiple_aphasia_occurrence AS (
        SELECT f1.person_id
        FROM aphasia_occurrence f1
        JOIN aphasia_occurrence f2 
            ON f1.person_id = f2.person_id
            AND f1.aphasia_rank = 1
            AND f2.aphasia_rank = 2
        GROUP BY f1.person_id
    ),
    aphasia_indicator AS (
        SELECT sc.subject_id,
               CASE 
                   WHEN va.person_id IS NOT NULL AND ma.person_id IS NOT NULL THEN 1 
                   ELSE 0 
               END AS has_aphasia
        FROM stroke_cohort sc
        LEFT JOIN valid_aphasia_occurrence va ON sc.subject_id = va.person_id
        LEFT JOIN multiple_aphasia_occurrence ma ON sc.subject_id = ma.person_id
    ),

    -- Dysphagia logic
    dysphagia_occurrence AS (
        SELECT condition_occurrence_id, person_id, condition_start_date,
               DENSE_RANK() OVER (PARTITION BY person_id ORDER BY condition_start_date) AS dysphagia_rank
        FROM omop_cdm_53_pmtx_202203.condition_occurrence
        WHERE condition_concept_id IN (31317, 440530, 26823, 443465, 45757559, 4198185)
    ),
    valid_dysphagia_occurrence AS (
        SELECT dyo.person_id
        FROM stroke_cohort sc
        JOIN dysphagia_occurrence dyo 
            ON sc.subject_id = dyo.person_id
            AND dyo.condition_start_date >= sc.cohort_start_date
        GROUP BY dyo.person_id
    ),
    multiple_dysphagia_occurrence AS (
        SELECT dys1.person_id
        FROM dysphagia_occurrence dys1
        JOIN dysphagia_occurrence dys2 
            ON dys1.person_id = dys2.person_id
            AND dys1.dysphagia_rank = 1
            AND dys2.dysphagia_rank = 2
        GROUP BY dys1.person_id
    ),
    dysphagia_indicator AS (
        SELECT sc.subject_id,
               CASE 
                   WHEN vdyo.person_id IS NOT NULL AND mdyo.person_id IS NOT NULL THEN 1 
                   ELSE 0 
               END AS has_dysphagia
        FROM stroke_cohort sc
        LEFT JOIN valid_dysphagia_occurrence vdyo ON sc.subject_id = vdyo.person_id
        LEFT JOIN multiple_dysphagia_occurrence mdyo ON sc.subject_id = mdyo.person_id
    ),

    -- Dysarthria logic
    dysarthria_occurrence AS (
        SELECT condition_occurrence_id, person_id, condition_start_date,
               DENSE_RANK() OVER (PARTITION BY person_id ORDER BY condition_start_date) AS dysarthria_rank
        FROM omop_cdm_53_pmtx_202203.condition_occurrence
        WHERE condition_concept_id IN (4196636, 43530687)
    ),
    valid_dysarthria_occurrence AS (
        SELECT dya.person_id
        FROM stroke_cohort sc
        JOIN dysarthria_occurrence dya 
            ON sc.subject_id = dya.person_id
            AND dya.condition_start_date >= sc.cohort_start_date
        GROUP BY dya.person_id
    ),
    multiple_dysarthria_occurrence AS (
        SELECT dar1.person_id
        FROM dysarthria_occurrence dar1
        JOIN dysarthria_occurrence dar2 
            ON dar1.person_id = dar2.person_id
            AND dar1.dysarthria_rank = 1
            AND dar2.dysarthria_rank = 2
        GROUP BY dar1.person_id
    ),
    dysarthria_indicator AS (
        SELECT sc.subject_id,
               CASE 
                   WHEN vdy.person_id IS NOT NULL AND mdy.person_id IS NOT NULL THEN 1 
                   ELSE 0 
               END AS has_dysarthria
        FROM stroke_cohort sc
        LEFT JOIN valid_dysarthria_occurrence vdy ON sc.subject_id = vdy.person_id
        LEFT JOIN multiple_dysarthria_occurrence mdy ON sc.subject_id = mdy.person_id
    )

    SELECT 
        sc.*, 
        ai.has_aphasia, 
        di.has_dysphagia, 
        dri.has_dysarthria,
        1 AS cohort_definition_id
    INTO {final_table}
    FROM stroke_cohort sc
    LEFT JOIN aphasia_indicator ai ON sc.subject_id = ai.subject_id
    LEFT JOIN dysphagia_indicator di ON sc.subject_id = di.subject_id
    LEFT JOIN dysarthria_indicator dri ON sc.subject_id = dri.subject_id;
    '''

    cursor.execute(create_cohort_w_conditions_query)
    connection.commit()

    # # Preview 5
    # cursor.execute(f"SELECT * FROM {final_table} LIMIT 5")
    # df = cursor.fetch_dataframe()
    # print("Cohort Table Preview:")
    # print(df)


in_patient_stroke_table = f"{config.SCHEMA}.inpatient_stroke_demo"
cohort_table = f"{config.SCHEMA}.stroke_cohort_w_conditions_demo"
create_cohort(intermediate_table=in_patient_stroke_table, final_table=cohort_table)
