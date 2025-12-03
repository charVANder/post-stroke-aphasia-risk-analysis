# Imports
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import seaborn as sns

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FIGS_DIR = os.path.join(BASE_DIR, "..", "figs")

def make_risk_graph(df):
    # Set style
    plt.rcParams['figure.figsize'] = (14, 8)

    # Create risk flag comparison by aphasia status
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    risk_flags = ['antidep_risk', 'anxiolytic_risk', 'hyp_sed_risk', 'antipsych_risk']
    risk_labels = ['Antidepressant\nRisk', 'Anxiolytic\nRisk', 'Hypnotic/Sedative\nRisk', 'Antipsychotic\nRisk']
    for idx, (risk, label) in enumerate(zip(risk_flags, risk_labels)):
        ax = axes[idx // 2, idx % 2]
        
        aphasia_pct = (df[df['has_aphasia']==1][risk].sum() / df['has_aphasia'].sum()) * 100
        no_aphasia_pct = (df[df['has_aphasia']==0][risk].sum() / (len(df) - df['has_aphasia'].sum())) * 100
        bars = ax.bar(['Aphasia', 'No Aphasia'], [aphasia_pct, no_aphasia_pct], color=['tab:orange', 'tab:blue'])
        ax.set_ylabel('Percentage (%)', fontsize=12)
        ax.set_title(label, fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(aphasia_pct, no_aphasia_pct) * 1.2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}%', ha='center', va='bottom', fontsize=11)

    plt.suptitle('High-Risk Medication Patterns by Aphasia Status\n(Medications without Appropriate Diagnosis)', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS_DIR, "high_risk_percentages.png"), dpi=300, bbox_inches='tight')
    print(f"File saved in figs directory as 'high_risk_percentages.png'")

def make_risk_distribution(df):
    # Risk score distribution comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Distribution plot
    risk_dist_aphasia = df[df['has_aphasia']==1]['total_risk_score'].value_counts().sort_index()
    risk_dist_no_aphasia = df[df['has_aphasia']==0]['total_risk_score'].value_counts().sort_index()

    x = range(6)
    aphasia_counts = [risk_dist_aphasia.get(i, 0) for i in x]
    no_aphasia_counts = [risk_dist_no_aphasia.get(i, 0) for i in x]

    width = 0.35
    ax1.bar([i - width/2 for i in x], aphasia_counts, width, label='Aphasia', color='tab:orange')
    ax1.bar([i + width/2 for i in x], no_aphasia_counts, width, label='No Aphasia', color='tab:blue')
    ax1.set_xlabel('Total Risk Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Patients', fontsize=12, fontweight='bold')
    ax1.set_title('Risk Score Distribution (Count)', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Percentage plot
    aphasia_total = df['has_aphasia'].sum()
    no_aphasia_total = len(df) - aphasia_total
    aphasia_pcts = [(count/aphasia_total)*100 for count in aphasia_counts]
    no_aphasia_pcts = [(count/no_aphasia_total)*100 for count in no_aphasia_counts]

    ax2.bar([i - width/2 for i in x], aphasia_pcts, width, label='Aphasia', color='tab:orange')
    ax2.bar([i + width/2 for i in x], no_aphasia_pcts, width, label='No Aphasia', color='tab:blue')
    ax2.set_xlabel('Total Risk Score', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Risk Score Distribution (Percentage)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGS_DIR, 'risk_score_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"File saved in figs directory as 'risk_score_distribution.png'")
    plt.close()


def make_risk_by_mh_status(df):
    '''Risk prevalence by mh status. For example, of the aphasia patients with MH conditions, what % have each risk flag
    '''
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        risk_flags = ['antidep_risk', 'anxiolytic_risk', 'hyp_sed_risk', 'antipsych_risk']
        risk_labels = ['Antidep', 'Anxiolytic', 'Hypnotic/Sed', 'Antipsych']

        # with mh conditions
        mh_df = df[df['has_any_mental_health_condition'] == 1]
        mh_aph = mh_df[mh_df['has_aphasia'] == 1]
        mh_no_aph = mh_df[mh_df['has_aphasia'] == 0]
        
        mh_aph_pcts = [(mh_aph[risk].sum() / len(mh_aph) * 100) if len(mh_aph) > 0 else 0 for risk in risk_flags]
        mh_no_aph_pcts = [(mh_no_aph[risk].sum() / len(mh_no_aph) * 100) if len(mh_no_aph) > 0 else 0 for risk in risk_flags]
        
        x = np.arange(len(risk_labels))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, mh_aph_pcts, width, label='Aphasia', color='tab:orange')
        bars2 = ax1.bar(x + width/2, mh_no_aph_pcts, width, label='No Aphasia', color='tab:blue')
        
        ax1.set_ylabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax1.set_title(f'WITH Mental Health Conditions\n(Aphasia: n={len(mh_aph):,}, No Aphasia: n={len(mh_no_aph):,})',  fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(risk_labels, rotation=15, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_axisbelow(True)
        
        # value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.3:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # w/o mh
        no_mh_df = df[df['has_any_mental_health_condition'] == 0]
        no_mh_aph = no_mh_df[no_mh_df['has_aphasia'] == 1]
        no_mh_no_aph = no_mh_df[no_mh_df['has_aphasia'] == 0]
        
        no_mh_aph_pcts = [(no_mh_aph[risk].sum() / len(no_mh_aph) * 100) if len(no_mh_aph) > 0 else 0 for risk in risk_flags]
        no_mh_no_aph_pcts = [(no_mh_no_aph[risk].sum() / len(no_mh_no_aph) * 100) if len(no_mh_no_aph) > 0 else 0 for risk in risk_flags]
        
        bars3 = ax2.bar(x - width/2, no_mh_aph_pcts, width, label='Aphasia', color='tab:orange')
        bars4 = ax2.bar(x + width/2, no_mh_no_aph_pcts, width, label='No Aphasia', color='tab:blue')
        
        ax2.set_ylabel('Prevalence (%)', fontsize=11, fontweight='bold')
        ax2.set_title(f'WITHOUT Mental Health Conditions\n(Aphasia: n={len(no_mh_aph):,}, No Aphasia: n={len(no_mh_no_aph):,})', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(risk_labels, rotation=15, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_axisbelow(True)
        
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.3:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle('Risk Flags by Mental Health Status', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "risk_by_mh_status.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'risk_by_mh_status.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create risk by MH status plot: {e}")
        raise

def make_risk_component_heatmap(df):
    # VAN - not sure if this is actual useful, but it's here :p
    '''Heatmap of risk components by aphasia/MH status. Basically just a visual way to see how risk patterns differ when you combine aphasia status (yes/no) with mh status (yes/no).
    '''
    try:
        risk_flags = ['antidep_risk', 'anxiolytic_risk', 'hyp_sed_risk', 'antipsych_risk', 'has_polypharmacy_all_meds']
        risk_labels = ['Antidep\nRisk', 'Anxiolytic\nRisk', 'Hypnotic/Sed\nRisk', 'Antipsych\nRisk', 'Polypharmacy']
        
        # 2x2 matrix (Aphasia Yes/No by MH Yes/No)
        groups = [
            ('Aphasia + MH', (df['has_aphasia']==1) & (df['has_any_mental_health_condition']==1)),
            ('Aphasia No MH', (df['has_aphasia']==1) & (df['has_any_mental_health_condition']==0)),
            ('No Aphasia + MH', (df['has_aphasia']==0) & (df['has_any_mental_health_condition']==1)),
            ('No Aphasia No MH', (df['has_aphasia']==0) & (df['has_any_mental_health_condition']==0))
        ]
        matrix = []
        group_labels = []
        for label, mask in groups:
            group_df = df[mask]
            if len(group_df) > 0:
                row = [(group_df[risk].sum() / len(group_df) * 100) for risk in risk_flags]
                matrix.append(row)
                group_labels.append(f"{label}\n(n={len(group_df):,})")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(matrix, annot=True, fmt='.2f', cmap='YlOrRd', xticklabels=risk_labels, yticklabels=group_labels, ax=ax,cbar_kws={'label': 'Prevalence (%)'}, vmin=0, vmax=50)
        ax.set_title('Risk Component Prevalence by Patient Group', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, "risk_component_heatmap.png"), dpi=300, bbox_inches='tight')
        print(f"File saved in figs directory as 'risk_component_heatmap.png'")
        plt.close()
        
    except Exception as e:
        print(f"Failed to create risk component heatmap: {e}")
        raise


def main():
    df = pd.read_csv(os.path.join(DATA_DIR, "high_risk_cohort_no_dementia.csv"))
    make_risk_graph(df)
    make_risk_distribution(df)
    make_risk_by_mh_status(df)
    make_risk_component_heatmap(df)

if __name__ == "__main__":
    main()