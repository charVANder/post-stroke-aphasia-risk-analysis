"""
Logistic regression model for clinical impact analysis.
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

from constants import MODEL_FORMULA, INTERACTION_TERM


def fit_clinical_impact_model(df):
    """
    Fit logistic regression with aphasia, PIM, interaction, and MH confounders.

    Model: logit(P(readmission)) = (beta)0 + (beta)1(aphasia) + (beta)2(PIM) + (beta)3(aphasia × PIM) +
                                   (beta)4(depression) + (beta)5(anxiety) + (beta)6(ptsd) +
                                   (beta)7(bipolar) + (beta)8(schizophrenia) + (beta)9(psychotic) +
                                   (beta)10(seizure)

    Parameters
    df : p.df
        Input df with all required variables

    Returns
    -------
        (fitted_model, results_df)
        - fitted_model: statsmodels GLM model object
        - results_df: df with coefficients, ORs, CIs, p-values
    """

    print("CLINICAL IMPACT MODEL: Logistic Regression")
    print(f"\nFormula: {' '.join(MODEL_FORMULA.split())}\n")

    # Fit model with L1 regularization to handle quasi-separation
    # Regularization prevents infinite coefficients and improves stability
    # Using alpha=0.01 (moderate regularization) with simplified model (no interaction)
    print("Fitting with L1 regularization (alpha=0.01)...")
    logit_model = smf.logit(MODEL_FORMULA, data=df)
    model = logit_model.fit_regularized(method='l1', alpha=0.01, disp=0, maxiter=1000, trim_mode='auto')
    print("\n" + model.summary().as_text())

    # Extract results
    params = model.params
    conf = model.conf_int()
    pvals = model.pvalues

    # results to df
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

    # Model fit statistics
    print("MODEL FIT STATISTICS")
    print(f"    Pseudo R^2 (McFadden): {model.prsquared:.4f}")
    print(f"    AIC: {model.aic:.2f}")
    print(f"    BIC: {model.bic:.2f}")
    print(f"    Log-Likelihood: {model.llf:.2f}")

    # Test interaction significance (if interaction term is in model)
    print("INTERACTION TEST")
    if INTERACTION_TERM is not None and INTERACTION_TERM in pvals.index:
        interaction_pval = pvals[INTERACTION_TERM]
        print(f"    Interaction term: {INTERACTION_TERM}")
        print(f"    P-value: {interaction_pval:.4f}")

        if interaction_pval < 0.05:
            print(f"YES, Significant interaction detected (p={interaction_pval:.4f})")
            print(f"    bc Effect of PIMs on readmission differs by aphasia status")
        else:
            print(f"NO, No significant interaction (p={interaction_pval:.4f})")
            print(f"    bc Effect of PIMs on readmission does not differ by aphasia status")
    else:
        print(f"    No interaction term in model (simplified model)")
        print(f"    Assuming effect of PIMs is the same for both aphasia groups")

    print("ODDS RATIOS WITH 95% CONFIDENCE INTERVALS")
    print(results_df.to_string(index=False))
    print("\nSignificance: *** p<0.001, ** p<0.01, * p<0.05")

    return model, results_df
