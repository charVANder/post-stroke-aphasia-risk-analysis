# Imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import seaborn as sns

# Globals
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FIGS_DIR = os.path.join(BASE_DIR, "..", "figs")
MH_CONDITIONS = {
    'has_seizure': 'Seizure',
    'has_depression': 'Depression',
    'has_anxiety': 'Anxiety',
    'has_bipolar': 'Bipolar',
    'has_schizophrenia': 'Schizophrenia',
    'has_ptsd': 'PTSD',
    'has_psychotic_disorder': 'Psychotic Disorder',
    'has_any_mental_health_condition': 'Any MH Condition'
}

def make_mh_prevalence(df):
    aphasia_df = df[df['has_aphasia'] == 1]
    no_aphasia_df = df[df['has_aphasia'] == 0]
    total_aphasia = len(aphasia_df)
    total_no_aphasia = len(no_aphasia_df)

    stats_list = []
    for column_name, display_name in MH_CONDITIONS.items():
        aphasia_count = aphasia_df[column_name].sum()
        no_aphasia_count = no_aphasia_df[column_name].sum()
        aphasia_pct = (aphasia_count / total_aphasia * 100) if total_aphasia > 0 else 0
        no_aphasia_pct = (no_aphasia_count / total_no_aphasia * 100) if total_no_aphasia > 0 else 0

        stats_list.append({
            'condition': display_name,
            'aphasia_count': int(aphasia_count),
            'aphasia_pct': aphasia_pct,
            'no_aphasia_count': int(no_aphasia_count),
            'no_aphasia_pct': no_aphasia_pct
        })
    stats_df = pd.DataFrame(stats_list)

    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Plot 1
        conditions = stats_df['condition'].tolist()
        y_pos = np.arange(len(conditions))
        conditions_rev = conditions[::-1] # Reverse order for better readability (highest at top)
        aphasia_pcts_rev = stats_df['aphasia_pct'].tolist()[::-1]
        no_aphasia_pcts_rev = stats_df['no_aphasia_pct'].tolist()[::-1]
        bars1 = ax1.barh(y_pos - 0.2, aphasia_pcts_rev, 0.4, label='Aphasia', color='tab:orange') # horizontal bars
        bars2 = ax1.barh(y_pos + 0.2, no_aphasia_pcts_rev, 0.4, label='No Aphasia', color='tab:blue')
        for i, (v1, v2) in enumerate(zip(aphasia_pcts_rev, no_aphasia_pcts_rev)): # value labels
            ax1.text(v1 + 0.5, i - 0.2, f'{v1:.1f}%', va='center', fontsize=9)
            ax1.text(v2 + 0.5, i + 0.2, f'{v2:.1f}%', va='center', fontsize=9)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(conditions_rev)
        ax1.set_xlabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Prevalence Rates', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.set_axisbelow(True)

        # Plot 2
        aphasia_counts_rev = stats_df['aphasia_count'].tolist()[::-1]
        no_aphasia_counts_rev = stats_df['no_aphasia_count'].tolist()[::-1]
        bars3 = ax2.barh(y_pos - 0.2, aphasia_counts_rev, 0.4, label='Aphasia', color='tab:orange')
        bars4 = ax2.barh(y_pos + 0.2, no_aphasia_counts_rev, 0.4, label='No Aphasia', color='tab:blue')
        for i, (v1, v2) in enumerate(zip(aphasia_counts_rev, no_aphasia_counts_rev)):
            ax2.text(v1 + max(aphasia_counts_rev + no_aphasia_counts_rev) * 0.01, i - 0.2,
                    f'{int(v1):,}', va='center', fontsize=9)
            ax2.text(v2 + max(aphasia_counts_rev + no_aphasia_counts_rev) * 0.01, i + 0.2,
                    f'{int(v2):,}', va='center', fontsize=9)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(conditions_rev)
        ax2.set_xlabel('Patient Count', fontsize=11, fontweight='bold')
        ax2.set_title('Absolute Counts', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.set_axisbelow(True)
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

        fig.suptitle('Mental Health Prevalence Summary (no dementia):\nAphasia vs Non-Aphasia', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "mh_summary_comparison.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'mh_summary_comparison.png'")
        plt.close()

    except Exception as e:
        print(f"Failed to create summary comparison plot: {e}")
        raise

def make_mh_comorbidity_heatmaps(df):
    '''Correlation heatmaps of comorbidity patterns by aphasia status
    '''
    try:
        # 'has_any_mental_health_condition' not needed
        condition_cols = [col for col in MH_CONDITIONS.keys() if col != 'has_any_mental_health_condition']
        labels = [MH_CONDITIONS[col] for col in condition_cols]
        aphasia_df = df[df['has_aphasia'] == 1]
        no_aphasia_df = df[df['has_aphasia'] == 0]
        corr_aphasia = aphasia_df[condition_cols].corr()
        corr_no_aphasia = no_aphasia_df[condition_cols].corr()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # With Aphasia
        sns.heatmap(corr_aphasia, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, xticklabels=labels, yticklabels=labels, ax=ax1, vmin=-1, vmax=1)
        ax1.set_title('With Aphasia\nComorbidity Patterns', fontsize=14, fontweight='bold', pad=20)
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)
        
        # Without Aphasia
        sns.heatmap(corr_no_aphasia, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, xticklabels=labels, yticklabels=labels, ax=ax2, vmin=-1, vmax=1)
        ax2.set_title('Without Aphasia\nComorbidity Patterns', fontsize=14, fontweight='bold', pad=20)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
        ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0)
        
        plt.suptitle('Mental Health Condition Comorbidity by Aphasia Status', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "mh_comorbidity_heatmap.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'mh_comorbidity_heatmap.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create comorbidity heatmaps: {e}")
        raise

def make_mh_comorbidity_difference(df):
    '''Heatmap of difference in comorbidity patterns
    '''
    try:
        condition_cols = [col for col in MH_CONDITIONS.keys() if col != 'has_any_mental_health_condition']
        labels = [MH_CONDITIONS[col] for col in condition_cols]
        aphasia_df = df[df['has_aphasia'] == 1]
        no_aphasia_df = df[df['has_aphasia'] == 0]
        corr_aphasia = aphasia_df[condition_cols].corr()
        corr_no_aphasia = no_aphasia_df[condition_cols].corr()
        corr_difference = corr_aphasia - corr_no_aphasia
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_difference, annot=True, fmt='.2f', cmap='RdBu_r', center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8, "label": "Δ Correlation"}, xticklabels=labels, yticklabels=labels, ax=ax, vmin=-0.5, vmax=0.5)
        ax.set_title('Difference in Comorbidity Patterns\n(Aphasia - No Aphasia)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "mh_comorbidity_difference.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'mh_comorbidity_difference.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create comorbidity difference heatmap: {e}")
        raise


def make_mh_burden_distribution(df):
    '''Number dist. of MH conditions per patient
    '''
    try:
        condition_cols = [col for col in MH_CONDITIONS.keys() if col != 'has_any_mental_health_condition']
        df['mh_condition_count'] = df[condition_cols].sum(axis=1)
        aphasia_counts = df[df['has_aphasia']==1]['mh_condition_count'].value_counts(normalize=True).sort_index() * 100
        no_aphasia_counts = df[df['has_aphasia']==0]['mh_condition_count'].value_counts(normalize=True).sort_index() * 100
        x = np.arange(0, 8)
        width = 0.35
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, [aphasia_counts.get(i, 0) for i in x], width, label='Aphasia', color='tab:orange', alpha=0.8)
        bars2 = ax.bar(x + width/2, [no_aphasia_counts.get(i, 0) for i in x], width, label='No Aphasia', color='tab:blue', alpha=0.8)
        
        # value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.5:  # only show if bar is visible
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        ax.set_xlabel('Number of Mental Health Conditions', fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage of Patients (%)', fontsize=11, fontweight='bold')
        ax.set_title('Distribution of Mental Health Condition Burden', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "mh_burden_distribution.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'mh_burden_distribution.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create burden distribution plot: {e}")
        raise


def main():
    df = pd.read_csv(os.path.join(DATA_DIR, "high_risk_cohort_no_dementia.csv"))
    make_mh_prevalence(df)
    make_mh_comorbidity_heatmaps(df)
    make_mh_comorbidity_difference(df)
    make_mh_burden_distribution(df)

if __name__ == "__main__":
    main()
