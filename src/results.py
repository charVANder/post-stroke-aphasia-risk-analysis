import pandas as pd
import numpy as np
import io
import sys
import os
from scipy import stats

def add_risk_flags(df):
    # Risk w/ antidepressant
    df['antidep_risk'] = (
        (df['has_antidepressant'] == 1) & 
        (df['has_depression'] == 0) &
        (df['has_anxiety'] == 0) &
        (df['has_ptsd'] == 0)
    ).astype(int)

    # Risk w/ anxiolytic
    df['anxiolytic_risk'] = (
        (df['has_anxiolytic'] == 1) & 
        (df['has_anxiety'] == 0) & 
        (df['has_ptsd'] == 0) &
        (df['has_seizure'] == 0)
    ).astype(int)

    # Risk w/ hypnotic/sedative
    df['hyp_sed_risk'] = (
        (df['has_hypnotic_sedative'] == 1) & 
        (df['has_anxiety'] == 0) & 
        (df['has_seizure'] == 0)
    ).astype(int)

    # Risk w/ antipsychotic
    df['antipsych_risk'] = (
        (df['has_antipsychotic'] == 1) & 
        (df['has_bipolar'] == 0) & 
        (df['has_schizophrenia'] == 0) & 
        (df['has_psychotic_disorder'] == 0)
    ).astype(int)

    # Creating a composite risk score
    df['total_risk_score'] = (
        df['antidep_risk'] +
        df['anxiolytic_risk'] +
        df['hyp_sed_risk'] +
        df['antipsych_risk'] +
        df['has_polypharmacy_all_meds']
    )
    df['is_high_risk'] = (df['total_risk_score'] >= 2).astype(int)

    return df


def chi_square_test(df, variable, group_var='has_aphasia'):
    contingency = pd.crosstab(df[group_var], df[variable])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    return chi2, p_value


def t_test(df, variable, group_var='has_aphasia'):
    group1 = df[df[group_var] == 1][variable]
    group0 = df[df[group_var] == 0][variable]
    t_stat, p_value = stats.ttest_ind(group1, group0, nan_policy='omit')
    return t_stat, p_value


def calculate_correlation(df, var1, var2):
    corr, p_value = stats.pearsonr(df[var1], df[var2])
    return corr, p_value


def make_summary(df, outfile="results.txt"):
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer

    try:
        total = len(df)
        aphasia_count = df['has_aphasia'].sum()
        no_aphasia_count = total - aphasia_count
        
        print("-"*80)
        print("STROKE COHORT ANALYSIS")
        print("-"*80)
        print("\nNotes:")
        print("- pp = percentage points")
        print("- p-values from chi-square tests (categorical) or t-tests (continuous)")
        print("- r = Pearson correlation coefficient")
        print("- Dementia patients excluded from all analyses")
        
        # Part 1 Cohort Overview
        print("\n" + "-"*80)
        print("APHASIA COHORT OVERVIEW")
        print("-"*80)
        print(f"\nTotal Patients (Dementia Excluded): {total:,}")
        print(f"  - With Aphasia:    {aphasia_count:,} ({aphasia_count/total*100:.2f}%)")
        print(f"  - Without Aphasia: {no_aphasia_count:,} ({no_aphasia_count/total*100:.2f}%)")
        
        # Part 2 MH Prevalence
        print("\n" + "-"*80)
        print("MENTAL HEALTH CONDITION PREVALENCE")
        print("-"*80)
        
        mh_conditions = [
            ('has_depression', 'Depression'),
            ('has_anxiety', 'Anxiety'),
            ('has_ptsd', 'PTSD'),
            ('has_bipolar', 'Bipolar Disorder'),
            ('has_schizophrenia', 'Schizophrenia'),
            ('has_psychotic_disorder', 'Psychotic Disorder'),
            ('has_seizure', 'Seizure Disorder'),
            ('has_any_mental_health_condition', 'Any Mental Health Condition')
        ]
        
        print("\n{:<35} {:>12} {:>12} {:>10} {:>10}".format(
            "Condition", "Aphasia", "No Aphasia", "Diff", "p-value"
        ))
        print("-" * 80)
        
        for condition, label in mh_conditions:
            aphasia_n = df[df['has_aphasia']==1][condition].sum()
            no_aphasia_n = df[df['has_aphasia']==0][condition].sum()
            aphasia_pct = (aphasia_n / aphasia_count) * 100
            no_aphasia_pct = (no_aphasia_n / no_aphasia_count) * 100
            diff = aphasia_pct - no_aphasia_pct
            
            # Chi-square test
            chi2, p_val = chi_square_test(df, condition)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            
            print(f"{label:<35} {aphasia_n:>5} ({aphasia_pct:>5.2f}%) "
                  f"{no_aphasia_n:>5} ({no_aphasia_pct:>5.2f}%) "
                  f"{diff:>+6.2f}pp {p_str:>10}")
            
        # MH Condition Distribution
        print("\n\nMental Health Conditions Distribution of Burdne")
        print("-" * 80)
        condition_cols = [col for col in ['has_depression', 'has_anxiety', 'has_ptsd', 'has_bipolar', 'has_schizophrenia', 'has_psychotic_disorder', 'has_seizure']]
        df['mh_condition_count'] = df[condition_cols].sum(axis=1)
        aphasia_mh_dist = df[df['has_aphasia']==1]['mh_condition_count'].value_counts(normalize=True).sort_index() * 100
        no_aphasia_mh_dist = df[df['has_aphasia']==0]['mh_condition_count'].value_counts(normalize=True).sort_index() * 100
        
        print("{:>12} {:>15} {:>15}".format("# Conditions", "Aphasia", "No Aphasia"))
        print("-" * 80)
        for count in range(8):
            aph_pct = aphasia_mh_dist.get(count, 0)
            no_aph_pct = no_aphasia_mh_dist.get(count, 0)
            aph_n = int((aph_pct / 100) * aphasia_count)
            no_aph_n = int((no_aph_pct / 100) * no_aphasia_count)
            print(f"{count:>12} {aph_n:>6} ({aph_pct:>5.2f}%) {no_aph_n:>6} ({no_aph_pct:>5.2f}%)")
        
        # som stat tests
        aphasia_mh_mean = df[df['has_aphasia']==1]['mh_condition_count'].mean()
        no_aphasia_mh_mean = df[df['has_aphasia']==0]['mh_condition_count'].mean()
        aphasia_mh_std = df[df['has_aphasia']==1]['mh_condition_count'].std()
        no_aphasia_mh_std = df[df['has_aphasia']==0]['mh_condition_count'].std()
        t_stat_mh, p_val_t_mh = t_test(df, 'mh_condition_count')
        p_str_t_mh = f"{p_val_t_mh:.4f}" if p_val_t_mh >= 0.0001 else "<0.0001"
        contingency_mh = pd.crosstab(df['has_aphasia'], df['mh_condition_count'])
        chi2_mh, p_val_chi_mh, dof_mh, expected_mh = stats.chi2_contingency(contingency_mh)
        p_str_chi_mh = f"{p_val_chi_mh:.4f}" if p_val_chi_mh >= 0.0001 else "<0.0001"
        print(f"\nMean conditions: Aphasia={aphasia_mh_mean:.2f}±{aphasia_mh_std:.2f}, No Aphasia={no_aphasia_mh_mean:.2f}±{no_aphasia_mh_std:.2f}")
        print(f"t-test (mean comparison): p={p_str_t_mh}")
        print(f"Chi-square test (distribution pattern): p={p_str_chi_mh}")
        
        # Part 3 PIM PREVALENCE
        print("\n" + "-"*80)
        print("PIM PREVALENCE")
        print("-"*80)
        
        pim_metrics = [
            ('has_any_pim', 'Any PIM'),
            ('has_antidepressant', 'Antidepressant'),
            ('has_anxiolytic', 'Anxiolytic'),
            ('has_antipsychotic', 'Antipsychotic'),
            ('has_hypnotic_sedative', 'Hypnotic/Sedative'),
            ('has_polypharmacy_all_meds', 'Polypharmacy (≥5 meds)')
        ]
        
        print("\n{:<35} {:>12} {:>12} {:>10} {:>10}".format(
            "Medication Type", "Aphasia", "No Aphasia", "Diff", "p-value"
        ))
        print("-" * 80)
        
        for metric, label in pim_metrics:
            aphasia_n = df[df['has_aphasia']==1][metric].sum()
            no_aphasia_n = df[df['has_aphasia']==0][metric].sum()
            aphasia_pct = (aphasia_n / aphasia_count) * 100
            no_aphasia_pct = (no_aphasia_n / no_aphasia_count) * 100
            diff = aphasia_pct - no_aphasia_pct
            
            chi2, p_val = chi_square_test(df, metric)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            
            print(f"{label:<35} {aphasia_n:>5} ({aphasia_pct:>5.2f}%) "
                  f"{no_aphasia_n:>5} ({no_aphasia_pct:>5.2f}%) "
                  f"{diff:>+6.2f}pp {p_str:>10}")
        
        # PIM Count Distribution
        print("\n\nPIM Count Distribution:")
        print("-" * 80)
        pim_cols = ['has_antidepressant', 'has_anxiolytic', 'has_antipsychotic', 'has_hypnotic_sedative']
        df['pim_count'] = df[pim_cols].sum(axis=1)
        aphasia_pim_dist = df[df['has_aphasia']==1]['pim_count'].value_counts(normalize=True).sort_index() * 100
        no_aphasia_pim_dist = df[df['has_aphasia']==0]['pim_count'].value_counts(normalize=True).sort_index() * 100
        print("{:>12} {:>15} {:>15}".format("# PIMs", "Aphasia", "No Aphasia"))
        print("-" * 80)
        for count in range(5):
            aph_pct = aphasia_pim_dist.get(count, 0)
            no_aph_pct = no_aphasia_pim_dist.get(count, 0)
            aph_n = int((aph_pct / 100) * aphasia_count)
            no_aph_n = int((no_aph_pct / 100) * no_aphasia_count)
            label = f"{count}" if count < 4 else "4+"
            print(f"{label:>12} {aph_n:>6} ({aph_pct:>5.2f}%) {no_aph_n:>6} ({no_aph_pct:>5.2f}%)")
        
        # stat tests
        aphasia_pim_mean = df[df['has_aphasia']==1]['pim_count'].mean()
        no_aphasia_pim_mean = df[df['has_aphasia']==0]['pim_count'].mean()
        aphasia_pim_std = df[df['has_aphasia']==1]['pim_count'].std()
        no_aphasia_pim_std = df[df['has_aphasia']==0]['pim_count'].std()
        t_stat_pim, p_val_t_pim = t_test(df, 'pim_count')
        p_str_t_pim = f"{p_val_t_pim:.4f}" if p_val_t_pim >= 0.0001 else "<0.0001"
        contingency_pim = pd.crosstab(df['has_aphasia'], df['pim_count'])
        chi2_pim, p_val_chi_pim, dof_pim, expected_pim = stats.chi2_contingency(contingency_pim)
        p_str_chi_pim = f"{p_val_chi_pim:.4f}" if p_val_chi_pim >= 0.0001 else "<0.0001"
        print(f"\nMean PIMs: Aphasia={aphasia_pim_mean:.2f}±{aphasia_pim_std:.2f}, No Aphasia={no_aphasia_pim_mean:.2f}±{no_aphasia_pim_std:.2f}")
        print(f"t-test (mean comparison): p={p_str_t_pim}")
        print(f"Chi-square test (distribution pattern): p={p_str_chi_pim}")

        # Part 4 Risk Flags
        print("\n" + "-"*80)
        print("RISK FLAGS")
        print("-"*80)        
        risk_flags = [
            ('antidep_risk', 'Antidepressant Risk', 
             'Antidepressant without Depression/Anxiety/PTSD'),
            ('anxiolytic_risk', 'Anxiolytic Risk',
             'Anxiolytic without Anxiety/PTSD/Seizure'),
            ('hyp_sed_risk', 'Hypnotic/Sedative Risk',
             'Hypnotic/Sedative without Anxiety/Seizure'),
            ('antipsych_risk', 'Antipsychotic Risk',
             'Antipsychotic without Bipolar/Schizophrenia/Psychosis')
        ]
        
        print("\n{:<35} {:>12} {:>12} {:>10} {:>10}".format(
            "Risk Category", "Aphasia", "No Aphasia", "Diff", "p-value"
        ))
        print("-" * 80)
        
        for risk, label, description in risk_flags:
            aphasia_n = df[df['has_aphasia']==1][risk].sum()
            no_aphasia_n = df[df['has_aphasia']==0][risk].sum()
            aphasia_pct = (aphasia_n / aphasia_count) * 100
            no_aphasia_pct = (no_aphasia_n / no_aphasia_count) * 100
            diff = aphasia_pct - no_aphasia_pct
            
            chi2, p_val = chi_square_test(df, risk)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            
            print(f"{label:<35} {aphasia_n:>5} ({aphasia_pct:>5.2f}%) "
                  f"{no_aphasia_n:>5} ({no_aphasia_pct:>5.2f}%) "
                  f"{diff:>+6.2f}pp {p_str:>10}")
        
        # Part 5 High Risk
        print("\n" + "-"*80)
        print("HIGH-RISK PATIENTS")
        print("-"*80)
        print("\nHigh-Risk Definition: Total risk score ≥ 2")
        print("(Sum of individual risk flags + polypharmacy)")
        
        high_risk_aphasia = df[df['has_aphasia']==1]['is_high_risk'].sum()
        high_risk_no_aphasia = df[df['has_aphasia']==0]['is_high_risk'].sum()
        high_risk_aphasia_pct = (high_risk_aphasia / aphasia_count) * 100
        high_risk_no_aphasia_pct = (high_risk_no_aphasia / no_aphasia_count) * 100
        diff = high_risk_aphasia_pct - high_risk_no_aphasia_pct
        
        chi2, p_val = chi_square_test(df, 'is_high_risk')
        p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
        
        print(f"\n  Aphasia:    {high_risk_aphasia:>5} out of {aphasia_count:>5} ({high_risk_aphasia_pct:>6.2f}%)")
        print(f"  No Aphasia: {high_risk_no_aphasia:>5} out of {no_aphasia_count:>5} ({high_risk_no_aphasia_pct:>6.2f}%)")
        print(f"  Difference: {diff:>+6.2f} percentage points (p={p_str})")
        
        # Risk Score Dist
        print("\n\nRisk Score Distribution:")
        print("-" * 80)
        print("{:>12} {:>15} {:>15}".format("Risk Score", "Aphasia", "No Aphasia"))
        print("-" * 80)
        
        risk_dist_aphasia = df[df['has_aphasia']==1]['total_risk_score'].value_counts().sort_index()
        risk_dist_no_aphasia = df[df['has_aphasia']==0]['total_risk_score'].value_counts().sort_index()
        
        for score in range(6):
            aphasia_n = risk_dist_aphasia.get(score, 0)
            no_aphasia_n = risk_dist_no_aphasia.get(score, 0)
            aphasia_pct = (aphasia_n / aphasia_count) * 100
            no_aphasia_pct = (no_aphasia_n / no_aphasia_count) * 100
            print(f"{score:>12} {aphasia_n:>6} ({aphasia_pct:>5.2f}%) "
                  f"{no_aphasia_n:>6} ({no_aphasia_pct:>5.2f}%)")
        
        # Part 6 cont. metrics
        print("\n" + "-"*80)
        print("OTHER RISK METRICS")
        print("-"*80)
        
        continuous_vars = [
            ('total_pim_count', 'Total PIM Count'),
            ('max_concurrent_pims', 'Max Concurrent PIMs'),
            ('total_risk_score', 'Total Risk Score'),
            ('total_med_count', 'Total Medication Count'),
            ('max_concurrent_meds', 'Max Concurrent Medications')
        ]
        
        print("\n{:<30} {:>18} {:>18} {:>10}".format(
            "Metric", "Aphasia", "No Aphasia", "p-value"
        ))
        print("{:<30} {:>18} {:>18} {:>10}".format(
            "", "(Mean ± SD)", "(Mean ± SD)", ""
        ))
        print("-" * 80)
        
        for var, label in continuous_vars:
            aphasia_mean = df[df['has_aphasia']==1][var].mean()
            no_aphasia_mean = df[df['has_aphasia']==0][var].mean()
            aphasia_std = df[df['has_aphasia']==1][var].std()
            no_aphasia_std = df[df['has_aphasia']==0][var].std()
            
            t_stat, p_val = t_test(df, var)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            
            print(f"{label:<30} {aphasia_mean:>6.2f} ± {aphasia_std:>5.2f} "
                  f"{no_aphasia_mean:>6.2f} ± {no_aphasia_std:>5.2f}   {p_str:>10}")
        
        # Part 7 Correlations
        print("\n" + "-"*80)
        print("MORE CORRELATIONS")
        print("-"*80)
        print("\nAphasia and Key Outcomes")
        print("-" * 80)
        
        correlation_vars = [
            ('has_any_pim', 'Any PIM'),
            ('has_polypharmacy_all_meds', 'Polypharmacy'),
            ('total_risk_score', 'Total Risk Score'),
            ('is_high_risk', 'High-Risk Status'),
            ('has_any_mental_health_condition', 'Any Mental Health Condition')
        ]
        
        print("{:<40} {:>12} {:>10}".format("Variable Pair", "r", "p-value"))
        print("-" * 80)
        
        for var, label in correlation_vars:
            corr, p_val = calculate_correlation(df, 'has_aphasia', var)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            print(f"Aphasia x {label:<32} {corr:>12.4f} {p_str:>10}")
        
        print("\n\nRisk Factors and Mental Health")
        print("-" * 80)
        print("{:<40} {:>12} {:>10}".format("Variable Pair", "r", "p-value"))
        print("-" * 80)
        
        cross_correlations = [
            ('has_any_mental_health_condition', 'has_any_pim', 
             'Mental Health x PIM'),
            ('has_any_mental_health_condition', 'total_risk_score',
             'Mental Health x Risk Score'),
            ('has_polypharmacy_all_meds', 'total_risk_score',
             'Polypharmacy x Risk Score'),
            ('total_pim_count', 'total_risk_score',
             'PIM Count x Risk Score')
        ]
        
        for var1, var2, label in cross_correlations:
            corr, p_val = calculate_correlation(df, var1, var2)
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001"
            print(f"{label:<40} {corr:>12.4f} {p_str:>10}")
        
        # Part 8 Risk by MH Status
        print("\n" + "-"*80)
        print("RISK BY MH STATUS")
        print("-"*80)
        
        # Among those WITH mental health conditions
        mh_df = df[df['has_any_mental_health_condition'] == 1]
        mh_total = len(mh_df)
        mh_aphasia = mh_df['has_aphasia'].sum()
        mh_no_aphasia = mh_total - mh_aphasia
        
        print("\nPatients WITH Mental Health Conditions")
        print(f"    Total: {mh_total:,} (Aphasia: {mh_aphasia:,}, No Aphasia: {mh_no_aphasia:,})")
        print("-" * 80)
        
        if mh_aphasia > 0 and mh_no_aphasia > 0:
            print("\n{:<35} {:>12} {:>12} {:>10}".format(
                "Outcome", "Aphasia", "No Aphasia", "Diff"
            ))
            print("-" * 80)
            
            for metric, label in [('has_any_pim', 'Any PIM'), ('is_high_risk', 'High-Risk'), ('antidep_risk', 'Antidepressant Risk'), ('anxiolytic_risk', 'Anxiolytic Risk')]:
                aph_n = mh_df[mh_df['has_aphasia']==1][metric].sum()
                no_aph_n = mh_df[mh_df['has_aphasia']==0][metric].sum()
                aph_pct = (aph_n / mh_aphasia) * 100
                no_aph_pct = (no_aph_n / mh_no_aphasia) * 100
                diff = aph_pct - no_aph_pct
                
                print(f"{label:<35} {aph_n:>5} ({aph_pct:>5.2f}%) "
                      f"{no_aph_n:>5} ({no_aph_pct:>5.2f}%) {diff:>+6.2f}pp")
        
        # Among those WITHOUT mental health conditions
        no_mh_df = df[df['has_any_mental_health_condition'] == 0]
        no_mh_total = len(no_mh_df)
        no_mh_aphasia = no_mh_df['has_aphasia'].sum()
        no_mh_no_aphasia = no_mh_total - no_mh_aphasia
        
        print("\n\nPatients WITHOUT Mental Health Conditions")
        print(f"    Total: {no_mh_total:,} (Aphasia: {no_mh_aphasia:,}, No Aphasia: {no_mh_no_aphasia:,})")
        print("-" * 80)
        
        if no_mh_aphasia > 0 and no_mh_no_aphasia > 0:
            print("\n{:<35} {:>12} {:>12} {:>10}".format(
                "Outcome", "Aphasia", "No Aphasia", "Diff"
            ))
            print("-" * 80)
            
            for metric, label in [('has_any_pim', 'Any PIM'), ('is_high_risk', 'High-Risk'), ('antidep_risk', 'Antidepressant Risk'), ('anxiolytic_risk', 'Anxiolytic Risk')]:
                aph_n = no_mh_df[no_mh_df['has_aphasia']==1][metric].sum()
                no_aph_n = no_mh_df[no_mh_df['has_aphasia']==0][metric].sum()
                aph_pct = (aph_n / no_mh_aphasia) * 100 if no_mh_aphasia > 0 else 0
                no_aph_pct = (no_aph_n / no_mh_no_aphasia) * 100 if no_mh_no_aphasia > 0 else 0
                diff = aph_pct - no_aph_pct
                
                print(f"{label:<35} {aph_n:>5} ({aph_pct:>5.2f}%) "
                      f"{no_aph_n:>5} ({no_aph_pct:>5.2f}%) {diff:>+6.2f}pp")
    
    finally:
        sys.stdout = old_stdout
    
    summary_text = buffer.getvalue()
    with open(outfile, "w") as f:
        f.write(summary_text)
    
    print(summary_text)


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    mh_df = pd.read_csv(os.path.join(DATA_DIR, "mental_health_flags.csv"))
    pim_df = pd.read_csv(os.path.join(DATA_DIR, "pim_flags.csv"))

    # Merging tables w/o dementia
    merged_df = mh_df.merge(pim_df, on='subject_id', how='left')
    pim_na_columns = ['has_hypnotic_sedative', 'has_antipsychotic', 'has_antidepressant', 'has_anxiolytic', 'has_any_pim', 'total_pim_count', 'max_concurrent_pims', 'max_concurrent_days', 'has_polypharmacy', 'has_polypharmacy_all_meds','total_med_count', 'max_concurrent_meds', 'max_concurrent_meds_days']
    merged_df[pim_na_columns] = merged_df[pim_na_columns].fillna(0).astype(int)
    no_dementia_df = merged_df[merged_df['has_dementia'] == 0].copy()

    # Adding risk flags and saving
    risk_df = add_risk_flags(no_dementia_df)
    risk_df.to_csv(os.path.join(DATA_DIR, "high_risk_cohort_no_dementia.csv"), index=False)

    # Generate report
    make_summary(risk_df, outfile=os.path.join(DATA_DIR, "results.txt"))

if __name__ == "__main__":
    main()