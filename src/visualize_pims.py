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
PIM_CATEGORIES = {
    'has_hypnotic_sedative': 'Hypnotic/Sedative',
    'has_antipsychotic': 'Antipsychotic',
    'has_antidepressant': 'Antidepressant',
    'has_anxiolytic': 'Anxiolytic',
    'has_any_pim': 'Any PIM',
    'has_polypharmacy_all_meds': 'Polypharmacy (5+ for 30+ days)'
}

RISK_FLAGS = {
    'antidep_risk': 'Antidepressant Risk',
    'anxiolytic_risk': 'Anxiolytic Risk',
    'hyp_sed_risk': 'Hypnotic/Sedative Risk',
    'antipsych_risk': 'Antipsychotic Risk'
}

MH_CONDITIONS = {
    'has_depression': 'Depression',
    'has_anxiety': 'Anxiety',
    'has_ptsd': 'PTSD',
    'has_bipolar': 'Bipolar',
    'has_schizophrenia': 'Schizophrenia',
    'has_psychotic_disorder': 'Psychotic',
    'has_seizure': 'Seizure'
}


def make_pim_prevalence(df):
    aphasia_df = df[df['has_aphasia'] == 1]
    no_aphasia_df = df[df['has_aphasia'] == 0]
    total_aphasia = len(aphasia_df)
    total_no_aphasia = len(no_aphasia_df)

    stats_list_pim = []
    for column_name, display_name in PIM_CATEGORIES.items():
        aphasia_count_pim = aphasia_df[column_name].sum()
        no_aphasia_count_pim = no_aphasia_df[column_name].sum()
        aphasia_pct_pim = (aphasia_count_pim / total_aphasia * 100) if total_aphasia > 0 else 0
        no_aphasia_pct_pim = (no_aphasia_count_pim / total_no_aphasia * 100) if total_no_aphasia > 0 else 0
        stats_list_pim.append({
            'category': display_name,
            'aphasia_count': int(aphasia_count_pim),
            'aphasia_pct': aphasia_pct_pim,
            'no_aphasia_count': int(no_aphasia_count_pim),
            'no_aphasia_pct': no_aphasia_pct_pim
        })
    stats_df_pim = pd.DataFrame(stats_list_pim)

    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        # Plot 1
        categories = stats_df_pim['category'].tolist()
        y_pos = np.arange(len(categories))
        categories_rev = categories[::-1] # highest at top
        aphasia_pcts_rev_pim = stats_df_pim['aphasia_pct'].tolist()[::-1]
        no_aphasia_pcts_rev_pim = stats_df_pim['no_aphasia_pct'].tolist()[::-1]
        bars1 = ax1.barh(y_pos - 0.2, aphasia_pcts_rev_pim, 0.4, label='Aphasia', color='tab:orange') # horizontal bars
        bars2 = ax1.barh(y_pos + 0.2, no_aphasia_pcts_rev_pim, 0.4, label='No Aphasia', color='tab:blue')
        for i, (v1, v2) in enumerate(zip(aphasia_pcts_rev_pim, no_aphasia_pcts_rev_pim)): # value labels
            ax1.text(v1 + 0.5, i - 0.2, f'{v1:.1f}%', va='center', fontsize=9)
            ax1.text(v2 + 0.5, i + 0.2, f'{v2:.1f}%', va='center', fontsize=9)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(categories_rev)
        ax1.set_xlabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Prevalence Rates', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.set_axisbelow(True)

        # Plot 2
        aphasia_counts_rev_pim = stats_df_pim['aphasia_count'].tolist()[::-1]
        no_aphasia_counts_rev_pim = stats_df_pim['no_aphasia_count'].tolist()[::-1]
        bars3 = ax2.barh(y_pos - 0.2, aphasia_counts_rev_pim, 0.4, label='Aphasia', color='tab:orange')
        bars4 = ax2.barh(y_pos + 0.2, no_aphasia_counts_rev_pim, 0.4, label='No Aphasia', color='tab:blue')
        for i, (v1, v2) in enumerate(zip(aphasia_counts_rev_pim, no_aphasia_counts_rev_pim)):
            ax2.text(v1 + max(aphasia_counts_rev_pim + no_aphasia_counts_rev_pim) * 0.01, i - 0.2, f'{int(v1):,}', va='center', fontsize=9)
            ax2.text(v2 + max(aphasia_counts_rev_pim + no_aphasia_counts_rev_pim) * 0.01, i + 0.2, f'{int(v2):,}', va='center', fontsize=9)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(categories_rev)
        ax2.set_xlabel('Patient Count', fontsize=11, fontweight='bold')
        ax2.set_title('Absolute Counts', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.set_axisbelow(True)
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

        fig.suptitle('PIM Prevalence Summary (no dementia):\nAphasia vs Non-Aphasia', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "pim_summary_comparison.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'pim_summary_comparison.png'")
        plt.close()

    except Exception as e:
        print(f"Failed to create summary comparison plot: {e}")
        raise

def make_pim_by_mh_status(df):
    '''PIM prevalence by mh status
    '''
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        pim_categories = ['has_antidepressant', 'has_anxiolytic', 'has_antipsychotic', 'has_hypnotic_sedative', 'has_polypharmacy_all_meds']
        pim_labels = ['Antidep', 'Anxiolytic', 'Antipsych', 'Hypnotic/Sed', 'Polypharm']
        
        # WITH mh conditions
        mh_df = df[df['has_any_mental_health_condition'] == 1]
        mh_aph = mh_df[mh_df['has_aphasia'] == 1]
        mh_no_aph = mh_df[mh_df['has_aphasia'] == 0]
        
        mh_aph_pcts = [(mh_aph[pim].sum() / len(mh_aph) * 100) if len(mh_aph) > 0 else 0 for pim in pim_categories]
        mh_no_aph_pcts = [(mh_no_aph[pim].sum() / len(mh_no_aph) * 100) if len(mh_no_aph) > 0 else 0 for pim in pim_categories]
        x = np.arange(len(pim_labels))
        width = 0.35
        bars1 = ax1.bar(x - width/2, mh_aph_pcts, width, label='Aphasia', color='tab:orange')
        bars2 = ax1.bar(x + width/2, mh_no_aph_pcts, width, label='No Aphasia', color='tab:blue')
        
        ax1.set_ylabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax1.set_title(f'WITH Mental Health Conditions\n(Aphasia: n={len(mh_aph):,}, No Aphasia: n={len(mh_no_aph):,})', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(pim_labels, rotation=15, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_axisbelow(True)
        
        # value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 1:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # WITHOUT mh
        no_mh_df = df[df['has_any_mental_health_condition'] == 0]
        no_mh_aph = no_mh_df[no_mh_df['has_aphasia'] == 1]
        no_mh_no_aph = no_mh_df[no_mh_df['has_aphasia'] == 0]
        
        no_mh_aph_pcts = [(no_mh_aph[pim].sum() / len(no_mh_aph) * 100) if len(no_mh_aph) > 0 else 0 for pim in pim_categories]
        no_mh_no_aph_pcts = [(no_mh_no_aph[pim].sum() / len(no_mh_no_aph) * 100) if len(no_mh_no_aph) > 0 else 0 for pim in pim_categories]
        bars3 = ax2.bar(x - width/2, no_mh_aph_pcts, width, label='Aphasia', color='tab:orange')
        bars4 = ax2.bar(x + width/2, no_mh_no_aph_pcts, width, label='No Aphasia', color='tab:blue')
        ax2.set_ylabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax2.set_title(f'WITHOUT Mental Health Conditions\n(Aphasia: n={len(no_mh_aph):,}, No Aphasia: n={len(no_mh_no_aph):,})', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(pim_labels, rotation=15, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_axisbelow(True)
        
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if height > 1:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle('PIM Prevalence by Mental Health Status', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "pim_by_mh_status.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'pim_by_mh_status.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create PIM by MH status plot: {e}")
        raise


def make_pim_mh_heatmap(df):
    '''Heatmap of PIM prevalence among patients w/ MHs
    '''
    try:
        pim_cols = ['has_antidepressant', 'has_anxiolytic', 'has_antipsychotic', 'has_hypnotic_sedative']
        mh_cols = list(MH_CONDITIONS.keys())
        
        aphasia_df = df[df['has_aphasia'] == 1]
        aphasia_matrix = []
        for pim_col in pim_cols:
            row = []
            for mh_col in mh_cols:
                mh_patients = aphasia_df[aphasia_df[mh_col] == 1]
                if len(mh_patients) > 0:
                    pim_pct = (mh_patients[pim_col].sum() / len(mh_patients)) * 100
                else:
                    pim_pct = 0
                row.append(pim_pct)
            aphasia_matrix.append(row)
        
        # for no aphasia patients
        no_aphasia_df = df[df['has_aphasia'] == 0]
        no_aphasia_matrix = []
        
        for pim_col in pim_cols:
            row = []
            for mh_col in mh_cols:
                mh_patients = no_aphasia_df[no_aphasia_df[mh_col] == 1]
                if len(mh_patients) > 0:
                    pim_pct = (mh_patients[pim_col].sum() / len(mh_patients)) * 100
                else:
                    pim_pct = 0
                row.append(pim_pct)
            no_aphasia_matrix.append(row)
        
        pim_labels = ['Antidepressant', 'Anxiolytic', 'Antipsychotic', 'Hypnotic/Sed']
        mh_labels = list(MH_CONDITIONS.values())
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Aphasia heatmap
        sns.heatmap(aphasia_matrix, annot=True, fmt='.1f', cmap='YlOrRd', xticklabels=mh_labels, yticklabels=pim_labels, ax=ax1, vmin=0, vmax=60, cbar_kws={'label': 'Prevalence (%)'})
        ax1.set_title('With Aphasia\nPIM Prevalence by MH Condition', fontsize=12, fontweight='bold')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # No aphasia heatmap
        sns.heatmap(no_aphasia_matrix, annot=True, fmt='.1f', cmap='YlOrRd', xticklabels=mh_labels, yticklabels=pim_labels, ax=ax2, vmin=0, vmax=60, cbar_kws={'label': 'Prevalence (%)'})
        ax2.set_title('Without Aphasia\nPIM Prevalence by MH Condition', fontsize=12, fontweight='bold')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.suptitle('PIM Prevalence Among Patients with Mental Health Conditions', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "pim_mh_heatmap.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'pim_mh_heatmap.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create PIM-MH heatmap: {e}")
        raise


def make_pim_count_distribution(df):
    '''Number dist. of PIMs per patient
    '''
    try:
        # Calculating PIM count for each patient (not i cluding polypharmacy and any_pim)
        pim_cols = ['has_antidepressant', 'has_anxiolytic', 'has_antipsychotic', 'has_hypnotic_sedative']
        df['pim_count'] = df[pim_cols].sum(axis=1)
        aphasia_dist = df[df['has_aphasia']==1]['pim_count'].value_counts(normalize=True).sort_index() * 100
        no_aphasia_dist = df[df['has_aphasia']==0]['pim_count'].value_counts(normalize=True).sort_index() * 100
        x = np.arange(0, 5)
        width = 0.35
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, [aphasia_dist.get(i, 0) for i in x], width, label='Aphasia', color='tab:orange', alpha=0.8)
        bars2 = ax.bar(x + width/2, [no_aphasia_dist.get(i, 0) for i in x], width, label='No Aphasia', color='tab:blue', alpha=0.8)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.5:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Number of PIMs per Patient', fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage of Patients (%)', fontsize=11, fontweight='bold')
        ax.set_title('Distribution of PIM Count per Patient', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['0', '1', '2', '3', '4+'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "pim_count_distribution.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'pim_count_distribution.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create PIM count distribution plot: {e}")
        raise

def main():
    df = pd.read_csv(os.path.join(DATA_DIR, "high_risk_cohort_no_dementia.csv"))
    make_pim_prevalence(df)
    make_pim_by_mh_status(df)
    make_pim_mh_heatmap(df)
    make_pim_count_distribution(df)

if __name__ == "__main__":
    main()