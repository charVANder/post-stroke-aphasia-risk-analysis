# Imports
import redshift_connector
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def ensure_output_dir():
    project_root = Path(__file__).parent.parent

    # Check figs -> output -> create figs
    figs_dir = project_root / 'figs'
    if figs_dir.exists():
        return figs_dir

    output_dir = project_root / 'output'
    if output_dir.exists():
        return output_dir

    figs_dir.mkdir(parents=True, exist_ok=True)
    return figs_dir


def connect_to_db():
    try:
        connection = redshift_connector.connect(
            host=config.HOST,
            port=5439,
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise


def fetch_demographic_data(cursor):
    try:
        query = f'''
            SELECT sc.*, p.gender_source_value, p.location_id, p.year_of_birth
            FROM {config.SCHEMA}.stroke_cohort_w_conditions_demo sc
            INNER JOIN omop_cdm_53_pmtx_202203.person p
                ON sc.subject_id = p.person_id;
        '''
        cursor.execute(query)
        df = cursor.fetch_dataframe()
        df['age'] = 2025 - df['year_of_birth']
        return df
    except Exception as e:
        print(f"Failed to fetch demographic data: {e}")
        raise


def fetch_location_data(cursor):
    try:
        query = f'''
            SELECT sc.*, p.gender_source_value, p.location_id, p.year_of_birth, l.state
            FROM {config.SCHEMA}.stroke_cohort_w_conditions_demo sc
            INNER JOIN omop_cdm_53_pmtx_202203.person p ON sc.subject_id = p.person_id
            INNER JOIN omop_cdm_53_pmtx_202203.location l ON p.location_id = l.location_id;
        '''
        cursor.execute(query)
        df = cursor.fetch_dataframe()
        df = df.dropna(subset=['state'])
        df['age'] = 2025 - df['year_of_birth']
        return df
    except Exception as e:
        print(f"Failed to fetch location data: {e}")
        raise


def plot_cohort_by_yob(df, output_dir):
    try:
        grouped_df = df.groupby(['year_of_birth', 'has_aphasia']).size().unstack(fill_value=0)
        grouped_df.columns = ['No Aphasia', 'Aphasia']
        grouped_df['Total'] = grouped_df.sum(axis=1)
        grouped_df = grouped_df.sort_values('Total', ascending=False).drop(columns='Total')

        plt.rcParams['figure.figsize'] = [15, 7]
        grouped_df.plot(kind='bar', stacked=True, width=0.8)
        plt.title("Stroke + Aphasia Counts by Year of Birth")
        plt.xlabel("Year of Birth")
        plt.ylabel("Patient Count")
        plt.legend(title="Aphasia Status")
        plt.tight_layout()

        output_path = output_dir / "eda2_cohort_yob.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create YOB plot: {e}")
        raise


def plot_cohort_by_gender(df, output_dir):
    try:
        grouped_df = df.groupby(['year_of_birth', 'gender_source_value']).size().unstack(fill_value=0)
        grouped_df = grouped_df.fillna(0)
        grouped_df = grouped_df.sort_index()

        plt.rcParams['figure.figsize'] = [15, 7]
        grouped_df.plot(kind='bar', stacked=True, width=0.8)
        plt.title("Stroke Counts by Year of Birth and Gender")
        plt.xlabel("Year of Birth")
        plt.ylabel("Patient Count")
        plt.legend(title="Gender")
        plt.tight_layout()

        output_path = output_dir / "eda2_cohort_gender.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create gender plot: {e}")
        raise


def plot_cohort_by_state(df, output_dir):
    try:
        grouped_df = df.groupby(['state', 'has_aphasia']).size().unstack(fill_value=0)
        grouped_df.columns = ['No Aphasia', 'Aphasia']
        grouped_df['Total'] = grouped_df.sum(axis=1)
        grouped_df = grouped_df.sort_values(by='Total', ascending=False).drop(columns='Total')

        grouped_df.plot(kind='bar', stacked=True, width=0.8)
        plt.title("Stroke Cohort by State and Aphasia Status")
        plt.xlabel("State")
        plt.ylabel("Patient Count")
        plt.tight_layout()

        output_path = output_dir / "eda2_cohort_state.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create state plot: {e}")
        raise


def plot_age_distribution(df, output_dir):
    try:
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df[df['has_aphasia'] == 1], x='age', label='Aphasia', fill=True)
        sns.kdeplot(data=df[df['has_aphasia'] == 0], x='age', label='No Aphasia', fill=True)
        plt.title("Age Distribution of Stroke Patients by Aphasia Status")
        plt.xlabel("Age")
        plt.ylabel("Density")
        plt.legend()
        plt.tight_layout()

        output_path = output_dir / "eda2_age_dist.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create age distribution plot: {e}")
        raise


def plot_discharge_location(df, output_dir):
    try:
        discharge_group = df.groupby(['discharge_location', 'has_aphasia']).size().unstack(fill_value=0)
        discharge_group.columns = ['No Aphasia', 'Aphasia']
        discharge_group['Total'] = discharge_group.sum(axis=1)
        discharge_group = discharge_group.sort_values('Total', ascending=False).drop(columns='Total')

        discharge_group.plot(kind='bar', stacked=True)
        plt.title("Discharge Location by Aphasia Status")
        plt.ylabel("Patient Count")
        plt.xlabel("Discharge Location")
        plt.xticks(rotation=20)
        plt.tight_layout()

        output_path = output_dir / "eda2_discharge_location.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create discharge location plot: {e}")
        raise


def plot_length_of_stay(df, output_dir):
    try:
        df_copy = df.copy()
        df_copy['visit_start_date'] = pd.to_datetime(df_copy['visit_start_date'], errors='coerce')
        df_copy['visit_end_date'] = pd.to_datetime(df_copy['visit_end_date'], errors='coerce')
        df_copy['length_of_stay'] = (df_copy['visit_end_date'] - df_copy['visit_start_date']).dt.days

        sns.histplot(data=df_copy, x='length_of_stay', hue='has_aphasia', multiple='stack', bins=30)
        plt.title("Distribution of Length of Stay by Aphasia Status")
        plt.xlabel("Days in Hospital")
        plt.ylabel("Patient Count")
        plt.legend(title="Aphasia", labels=["No Aphasia", "Aphasia"])
        plt.tight_layout()

        output_path = output_dir / "eda2_length_of_stay.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create length of stay plot: {e}")
        raise


def plot_cooccurrence(df, output_dir):
    try:
        counts_matrix = np.zeros((3, 3), dtype=int)
        conditions = ['has_aphasia', 'has_dysphagia', 'has_dysarthria']

        for i, cond1 in enumerate(conditions):
            for j, cond2 in enumerate(conditions):
                counts_matrix[i, j] = ((df[cond1] == 1) & (df[cond2] == 1)).sum()

        counts_df = pd.DataFrame(counts_matrix, index=conditions, columns=conditions)
        sns.heatmap(counts_df, annot=True, fmt='d', cmap='Blues')
        plt.title("Counts of Co-occurrence Between Communication Disorders")
        plt.tight_layout()

        output_path = output_dir / "eda2_cooccurrence.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create co-occurrence plot: {e}")
        raise


def plot_time_trend(df, output_dir):
    try:
        df_copy = df.copy()
        df_copy['cohort_start_date'] = pd.to_datetime(df_copy['cohort_start_date'], errors='coerce')
        df_copy['year'] = df_copy['cohort_start_date'].dt.year

        trend_df = df_copy.groupby(['year', 'has_aphasia']).size().unstack(fill_value=0)
        trend_df.columns = ['No Aphasia', 'Aphasia']
        trend_df.plot(kind='line', marker='o')
        plt.title("Yearly Stroke Events by Aphasia Status")
        plt.xlabel("Year")
        plt.ylabel("Patient Count")
        plt.grid(False)
        plt.tight_layout()

        output_path = output_dir / "eda2_time_trend.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")

        plt.show()
        plt.close()
    except Exception as e:
        print(f"Failed to create time trend plot: {e}")
        raise


def main():
    connection = None

    try:
        output_dir = ensure_output_dir()
        connection = connect_to_db()
        cursor = connection.cursor()

        # Fetch demographic data
        demo_df = fetch_demographic_data(cursor)

        # Plot 1: Cohort by YOB
        plot_cohort_by_yob(demo_df, output_dir)

        # Plot 2: Cohort by Gender
        plot_cohort_by_gender(demo_df, output_dir)

        # Fetch location data
        location_df = fetch_location_data(cursor)

        # Plot 3: Cohort by State
        plot_cohort_by_state(location_df, output_dir)

        # Plot 4: Age Distribution
        plot_age_distribution(location_df, output_dir)

        # Plot 5: Discharge Location
        plot_discharge_location(demo_df, output_dir)

        # Plot 6: Length of Stay
        plot_length_of_stay(demo_df, output_dir)

        # Plot 7: Co-occurrence
        plot_cooccurrence(demo_df, output_dir)

        # Plot 8: Time Trend
        plot_time_trend(demo_df, output_dir)

        print("EDA2 completed yippie")

    except Exception as e:
        print(f"EDA2 failed: {e}")
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
