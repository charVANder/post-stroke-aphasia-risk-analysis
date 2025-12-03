"""
Scenario prediction functions for clinical impact analysis.
"""

import numpy as np
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

from constants import MODEL_FORMULA, SCENARIOS
from utils import format_scenario_label


def predict_scenario_probabilities(model, df):
    """
    Calculate predicted probabilities for 4 scenarios using marginalization.

    Scenarios:
    1. Aphasia + PIM
    2. Aphasia + No PIM
    3. No Aphasia + PIM
    4. No Aphasia + No PIM

    Marginalization approach:
    For each scenario
        - set aphasia and PIM to scenario values for all patients
        - keep mental health variables at observed values
        - predict for each patient, then average across all patients

    Parameters
    model : statsmodels GLM
        Fitted logistic regression model
    df : p.df
        Input dataframe

    Returns
    dict
        Dictionary with keys: 'aphasia_pim', 'aphasia_no_pim', 'no_aphasia_pim',
        'no_aphasia_no_pim', each containing predicted probability
    """

    print("PREDICTED PROBABILITIES (Marginalization)")
    print("     \nCalculating predicted probabilities for 4 scenarios...")
    print("     (Marginalizing over observed mental health confounder distribution)\n")

    predictions = {}

    for scenario_name, (aphasia_val, pim_val) in SCENARIOS.items():
        # Create counterfactual dataset
        df_scenario = df.copy()
        df_scenario['has_aphasia'] = aphasia_val
        df_scenario['has_any_pim'] = pim_val

        probs = model.predict(df_scenario)  # Predict for each patient

        avg_prob = probs.mean() # Average across all patients (marginalization)

        predictions[scenario_name] = avg_prob # just storing the avg prob

        aphasia_label, pim_label = format_scenario_label(aphasia_val, pim_val)
        print(f"{aphasia_label} + {pim_label:8s}: {avg_prob:.4f} ({avg_prob*100:.2f}%)")

    return predictions


def bootstrap_confidence_intervals(df, n_iterations=1000):
    """
    Bootstrap resampling to get 95% CI for predicted probabilities.

    For each bootstrap iteration:
    1. Resample dataset with replacement
    2. Fit logistic regression model
    3. Calculate predicted probabilities for all 4 scenarios
    4. Store results

    After all iterations, use 2.5th and 97.5th percentiles as 95% CI.

    Note: Some iterations may fail to converge; these are skipped.

    Parameters
    df : p.df
        Input dataframe
    n_iterations : int
        Number of bootstrap iterations (default: 1000)

    Returns
    dict
        Dictionary with keys: 'aphasia_pim', 'aphasia_no_pim', 'no_aphasia_pim',
        'no_aphasia_no_pim', each containing dict with 'mean', 'lower_ci', 'upper_ci'
    """

    print(f"BOOTSTRAP CONFIDENCE INTERVALS (n={n_iterations} iterations)")
    print("\nStand by while we do some magic :D... (we are bootstrapping)\n")

    # Store bootstrap results
    bootstrap_results = {key: [] for key in SCENARIOS.keys()}

    # Bootstrap iterations
    for i in range(n_iterations):
        if (i + 1) % 100 == 0:
            print(f"  Iteration {i+1}/{n_iterations}")

        # Resample with replacement
        df_boot = df.sample(n=len(df), replace=True, random_state=i)

        try:
            # Fit model
            model_boot = smf.logit(MODEL_FORMULA, data=df_boot).fit(disp=0)

            # Predict for each scenario
            for scenario_name, (aphasia_val, pim_val) in SCENARIOS.items():
                df_scenario = df_boot.copy()
                df_scenario['has_aphasia'] = aphasia_val
                df_scenario['has_any_pim'] = pim_val

                probs = model_boot.predict(df_scenario)
                avg_prob = probs.mean()

                bootstrap_results[scenario_name].append(avg_prob)

        except Exception as e:
            # If model fails to converge, skip this iteration
            continue

    # Calculate confidence intervals
    ci_results = {}

    print("BOOTSTRAP RESULTS (95% Confidence Intervals)")

    for scenario_name in bootstrap_results.keys():
        values = np.array(bootstrap_results[scenario_name])

        mean_val = values.mean()
        lower_ci = np.percentile(values, 2.5)
        upper_ci = np.percentile(values, 97.5)

        ci_results[scenario_name] = {
            'mean': mean_val,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci
        }

        # Format scenario name for display
        aphasia_label, pim_label = format_scenario_label(*SCENARIOS[scenario_name])

        print(f"{aphasia_label} + {pim_label:8s}: {mean_val:.4f} (95% CI: {lower_ci:.4f} - {upper_ci:.4f})")

    return ci_results
