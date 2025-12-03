"""
Multivariate Statistical Analyses
OHDSI-Stroke Aphasia Research Project

This module performs advanced statistical analyses:
1. Multivariable logistic regression (control for confounding)
2. Interaction analysis (effect modification)
3. Multiple testing correction (FDR)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set random seed
np.random.seed(42)

# Plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def multivariable_logistic_regression(df, outcome, predictors, model_name):
    """
    Fit multivariable logistic regression model.

    Parameters
    p.df
        Input dataframe
    outcome (str
        Outcome variable name
    predictors
        List of predictor variable names
    model_name
        Name for this model

    Returns
    statsmodels.GLM
        Fitted model
    p.DF
        Results table with odds ratios and confidence intervals
    """

    print(f"MULTIVARIABLE LOGISTIC REGRESSION: {model_name}")

    # Create formula
    formula = f"{outcome} ~ {' + '.join(predictors)}"
    print(f"\nFormula: {formula}\n")

    # Fit model
    print("Fitting model...")
    model = smf.logit(formula, data=df).fit()

    # Print summary
    print(model.summary())

    # Extract odds ratios with confidence intervals
    params = model.params
    conf = model.conf_int()
    pvals = model.pvalues

    results_df = pd.DataFrame({
        'Variable': params.index,
        'Coefficient': params.values,
        'Std Error': model.bse.values,
        'Odds Ratio': np.exp(params.values),
        'OR 95% CI Lower': np.exp(conf[0]),
        'OR 95% CI Upper': np.exp(conf[1]),
        'P-value': pvals.values,
        'Significant': ['***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
                       for p in pvals.values]
    })

    print("\n" + "="*60)
    print("ODDS RATIOS WITH 95% CONFIDENCE INTERVALS")
    print("="*60)
    print(results_df.to_string(index=False))
    print("\nSignificance: *** p<0.001, ** p<0.01, * p<0.05")
    print("="*60 + "\n")

    return model, results_df


def interaction_analysis(df, outcome, main_predictor, moderator, covariates=None):
    """
    Test interaction (effect modification) between two variables.

    Parameters
    df : p.DF
        Input dataframe
    outcome : str
        Outcome variable name
    main_predictor : str
        Main predictor of interest
    moderator : str
        Moderator variable (tests if effect of main predictor differs by this)
    covariates : list, optional
        Additional covariates to adjust for

    Returns
    statsmodels.GLM
        Fitted interaction model
    dict
        Stratified results
    """

    print(f"INTERACTION ANALYSIS")
    print(f"\nTesting: Does {moderator} modify the effect of {main_predictor} on {outcome}?")

    # Create interaction term
    interaction_term = f"{main_predictor}:{moderator}"

    # Build formula
    formula_parts = [main_predictor, moderator, interaction_term]
    if covariates:
        formula_parts.extend(covariates)

    formula = f"{outcome} ~ {' + '.join(formula_parts)}"
    print(f"\nFormula: {formula}\n")

    # Fit interaction model
    print("Fitting interaction model...")
    model = smf.logit(formula, data=df).fit()
    print(model.summary())

    # Test interaction significance
    interaction_pval = model.pvalues[interaction_term]
    print(f"INTERACTION TEST")
    print(f"Interaction term: {interaction_term}")
    print(f"P-value: {interaction_pval:.4f}")

    if interaction_pval < 0.05:
        print(f"✓ Significant interaction detected (p={interaction_pval:.4f})")
        print(f"  → Effect of {main_predictor} differs by {moderator} status")
    else:
        print(f"✗ No significant interaction (p={interaction_pval:.4f})")
        print(f"  → Effect of {main_predictor} does not differ by {moderator} status")
    print("="*60 + "\n")

    # Stratified analysis
    print("="*60)
    print("STRATIFIED ANALYSIS")
    print("="*60 + "\n")

    stratified_results = {}

    for level in df[moderator].unique():
        df_subset = df[df[moderator] == level]
        n = len(df_subset)
        n_outcome = df_subset[outcome].sum()

        print(f"{moderator} = {level}: n={n}, {outcome}={n_outcome} ({n_outcome/n*100:.1f}%)")

        # Fit model for this stratum
        formula_strat = f"{outcome} ~ {main_predictor}"
        if covariates:
            formula_strat += " + " + " + ".join(covariates)

        model_strat = smf.logit(formula_strat, data=df_subset).fit(disp=0)

        # Extract results for main predictor
        try:
            or_val = np.exp(model_strat.params[main_predictor])
            ci_lower = np.exp(model_strat.conf_int().loc[main_predictor, 0])
            ci_upper = np.exp(model_strat.conf_int().loc[main_predictor, 1])
            pval = model_strat.pvalues[main_predictor]

            print(f"  OR for {main_predictor}: {or_val:.3f} (95% CI: {ci_lower:.3f}-{ci_upper:.3f}), p={pval:.4f}")

            stratified_results[level] = {
                'n': n,
                'n_outcome': n_outcome,
                'OR': or_val,
                'CI_lower': ci_lower,
                'CI_upper': ci_upper,
                'p_value': pval
            }
        except:
            print(f"  Could not estimate OR (insufficient data)")
            stratified_results[level] = None

        print()


    return model, stratified_results


def plot_interaction(stratified_results, main_predictor, moderator, output_dir):
    """
    Plot stratified odds ratios with confidence intervals.

    Parameters
    stratified_results : dict
        Results from interaction_analysis()
    main_predictor
        Main predictor name
    moderator
        mod variable name
    output_dir
        Directory to save plot
    """

    print("Creating interaction plot...")

    # Prepare data for plotting
    strata = []
    ors = []
    ci_lowers = []
    ci_uppers = []

    for level, results in stratified_results.items():
        if results is not None:
            strata.append(f"{moderator}={level}")
            ors.append(results['OR'])
            ci_lowers.append(results['CI_lower'])
            ci_uppers.append(results['CI_upper'])

    # Create forest plot
    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = np.arange(len(strata))

    # Plot OR with CI
    ax.scatter(ors, y_pos, s=100, zorder=3)
    for i, (or_val, ci_low, ci_high) in enumerate(zip(ors, ci_lowers, ci_uppers)):
        ax.plot([ci_low, ci_high], [i, i], 'k-', linewidth=2)

    # Reference line at OR=1
    ax.axvline(x=1, color='red', linestyle='--', label='OR = 1 (no effect)')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(strata)
    ax.set_xlabel('Odds Ratio (95% CI)')
    ax.set_title(f'Effect of {main_predictor} by {moderator}\n(Forest Plot)')
    ax.grid(axis='x', alpha=0.3)
    ax.legend()

    plt.tight_layout()

    output_file = os.path.join(output_dir, f'interaction_{main_predictor}_{moderator}.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")


def multiple_testing_correction(p_values, test_names, method='fdr_bh', alpha=0.05):
    """
    Apply multiple testing correction to a set of p-values.

    Parameters
    p_values : list
        List of p-values
    test_names : list
        Names of tests corresponding to p-values
    method : str
        Correction method ('fdr_bh' for Benjamini-Hochberg FDR,
        'bonferroni', 'holm', etc.)
    alpha : float
        Significance level (default: 0.05)

    Returns
    p.DF
        Results table with raw and adjusted p-values
    """

    print("MULTIPLE TESTING CORRECTION")
    print(f"\nMethod: {method.upper()}")
    print(f"Alpha: {alpha}")
    print(f"Number of tests: {len(p_values)}\n")

    # Apply correction
    reject, p_adjusted, alphac_sidak, alphac_bonf = multipletests(
        p_values,
        alpha=alpha,
        method=method
    )

    # Create results table
    results_df = pd.DataFrame({
        'Test': test_names,
        'P-value (raw)': p_values,
        'P-value (adjusted)': p_adjusted,
        'Significant (raw)': ['Yes' if p < alpha else 'No' for p in p_values],
        'Significant (adjusted)': ['Yes' if r else 'No' for r in reject]
    })

    # Sort by raw p-value
    results_df = results_df.sort_values('P-value (raw)')

    print(results_df.to_string(index=False))

    # Summary
    n_sig_raw = sum(results_df['Significant (raw)'] == 'Yes')
    n_sig_adj = sum(results_df['Significant (adjusted)'] == 'Yes')

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Significant before correction: {n_sig_raw}/{len(p_values)} ({n_sig_raw/len(p_values)*100:.1f}%)")
    print(f"Significant after correction:  {n_sig_adj}/{len(p_values)} ({n_sig_adj/len(p_values)*100:.1f}%)")
    print(f"Tests no longer significant:   {n_sig_raw - n_sig_adj}")
    print("="*60 + "\n")

    return results_df



if __name__ == '__main__':

    print("MULTIVARIATE STATISTICAL ANALYSES")
    print("OHDSI-Stroke Aphasia Research Project")

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    FIGS_DIR = os.path.join(BASE_DIR, "..", "figs")
    os.makedirs(FIGS_DIR, exist_ok=True)

    INPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_with_readmissions.csv')

    # Load data
    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} records\n")

    # MULTIVARIABLE LOGISTIC REGRESSION MODELS

    print("MULTIVARIABLE LOGISTIC REGRESSION")

    # first model PIM use as outcome
    model1, results1 = multivariable_logistic_regression(
        df,
        outcome='has_any_pim',
        predictors=['has_aphasia', 'has_any_mental_health_condition', 'total_med_count'],
        model_name='Model 1: PIM Use'
    )
    results1.to_csv(os.path.join(DATA_DIR, 'multivariable_model1_pim_use.csv'), index=False)

    # second model High-risk status as outcome
    model2, results2 = multivariable_logistic_regression(
        df,
        outcome='is_high_risk',
        predictors=['has_aphasia', 'has_any_mental_health_condition', 'total_pim_count', 'max_concurrent_meds'],
        model_name='Model 2: High-Risk Status'
    )
    results2.to_csv(os.path.join(DATA_DIR, 'multivariable_model2_high_risk.csv'), index=False)

    # third model 180-day readmission as outcome (if available)
    # Based on week11.md: track ED visits from first_pim_date to first_pim_date + 180 days
    if 'has_180day_readmission' in df.columns:
        # Filter to patients with PIMs only
        df_with_pims = df[df['has_any_pim'] == 1].copy()

        model3, results3 = multivariable_logistic_regression(
            df_with_pims,
            outcome='has_180day_readmission',
            predictors=['has_aphasia', 'is_high_risk', 'has_any_mental_health_condition', 'total_med_count'],
            model_name='Model 3: 180-Day Readmission'
        )
        results3.to_csv(os.path.join(DATA_DIR, 'multivariable_model3_readmission.csv'), index=False)

    # INTERACTION ANALYSIS
    print("INTERACTION ANALYSIS")

    # first interaction phasia × Mental Health on PIM use
    interaction_model1, strat_results1 = interaction_analysis(
        df,
        outcome='has_any_pim',
        main_predictor='has_aphasia',
        moderator='has_any_mental_health_condition',
        covariates=['total_med_count']
    )

    # Plot interaction
    plot_interaction(
        strat_results1,
        main_predictor='has_aphasia',
        moderator='has_any_mental_health_condition',
        output_dir=FIGS_DIR
    )

    # sec interaction Aphasia × High-risk status on readmission (if available)
    if 'has_180day_readmission' in df.columns:
        df_with_pims = df[df['has_any_pim'] == 1].copy()

        interaction_model2, strat_results2 = interaction_analysis(
            df_with_pims,
            outcome='has_180day_readmission',
            main_predictor='has_aphasia',
            moderator='is_high_risk',
            covariates=['has_any_mental_health_condition', 'total_med_count']
        )

        # Plot interaction
        plot_interaction(
            strat_results2,
            main_predictor='has_aphasia',
            moderator='is_high_risk',
            output_dir=FIGS_DIR
        )

    # MULTIPLE TESTING CORRECTION (EXAMPLE)

    print("MULTIPLE TESTING CORRECTION (EXAMPLE)")

    #
    #
    # still kinda todo here - need to collect all p-values from bivariate tests in results.py
    #
    #
    #
    # Example: Collect p-values from bivariate tests
    # This is a simplified ex - in practice, you'd collect all p-values
    # from your chi-square and t-tests in results.py

    example_p_values = [
        model1.pvalues['has_aphasia'],
        model1.pvalues['has_any_mental_health_condition'],
        model2.pvalues['has_aphasia'],
        model2.pvalues['has_any_mental_health_condition'],
        interaction_model1.pvalues['has_aphasia:has_any_mental_health_condition']
    ]

    example_test_names = [
        'Model 1: Aphasia → PIM',
        'Model 1: Mental Health → PIM',
        'Model 2: Aphasia → High-Risk',
        'Model 2: Mental Health → High-Risk',
        'Interaction: Aphasia × MH → PIM'
    ]

    fdr_results = multiple_testing_correction(
        example_p_values,
        example_test_names,
        method='fdr_bh',
        alpha=0.05
    )

    fdr_results.to_csv(os.path.join(DATA_DIR, 'multiple_testing_correction.csv'), index=False)

    # SUMMARY

    print("ANALYSIS COMPLETE!")
    print(f"\nResults saved to:")
    print(f"  Data files: {DATA_DIR}")
    print(f"  Figures: {FIGS_DIR}")
    print("\nGenerated files:")
    print("  - multivariable_model1_pim_use.csv")
    print("  - multivariable_model2_high_risk.csv")
    if 'has_180day_readmission' in df.columns:
        print("  - multivariable_model3_readmission.csv")
    print("  - interaction_*.png")
    print("  - multiple_testing_correction.csv")
    print("="*60 + "\n")

    print("\nKEY FINDINGS:")
    print("\n1. INDEPENDENT EFFECT OF APHASIA:")
    print(f"   PIM Use: OR={np.exp(model1.params['has_aphasia']):.3f}, p={model1.pvalues['has_aphasia']:.4f}")
    print(f"   High-Risk: OR={np.exp(model2.params['has_aphasia']):.3f}, p={model2.pvalues['has_aphasia']:.4f}")

    print("\n2. INTERACTION EFFECTS:")
    interaction_pval = interaction_model1.pvalues['has_aphasia:has_any_mental_health_condition']
    if interaction_pval < 0.05:
        print(f"   ✓ Aphasia × Mental Health interaction is SIGNIFICANT (p={interaction_pval:.4f})")
    else:
        print(f"   ✗ Aphasia × Mental Health interaction is NOT significant (p={interaction_pval:.4f})")
