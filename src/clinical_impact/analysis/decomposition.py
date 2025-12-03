"""
Marginal effects decomposition for clinical impact analysis.
"""

import pandas as pd
import numpy as np


def marginal_effects_decomposition(model, df):
    """
    Decompose total readmission disparity into components.

    Decomposition partitions the total disparity between aphasia and non-aphasia groups:
    1. Component due to differential PIM exposure (composition effect)
    2. Independent effect of aphasia (direct effect)
    3. Interaction/effect modification (differential response to PIMs)

    Uses counterfactual predictions (g-computation approach).

    Parameters
    model : statsmodels GLM
        Fitted logistic regression model
    df : p.df
        Input dataframe

    Returns
    p.df
        df with decomposition components
    """

    print("MARGINAL EFFECTS DECOMPOSITION")
    print("\nQuantifying how much of the readmission disparity is due to:")
    print("     1. Differential PIM prescription rates")
    print("     2. Independent effect of aphasia")
    print("     3. Interaction effects\n")

    # Calculate observed rates in each group
    aphasia_group = df[df['has_aphasia'] == 1]
    no_aphasia_group = df[df['has_aphasia'] == 0]

    # Observed readmission rates
    p_obs_aphasia = aphasia_group['has_180day_readmission'].mean()
    p_obs_no_aphasia = no_aphasia_group['has_180day_readmission'].mean()

    # Observed PIM prescription rates
    pi_aphasia = aphasia_group['has_any_pim'].mean()
    pi_no_aphasia = no_aphasia_group['has_any_pim'].mean()

    print(f"Observed Rates:")
    print(f"  Aphasia group:")
    print(f"    Readmission rate: {p_obs_aphasia:.4f} ({p_obs_aphasia*100:.2f}%)")
    print(f"    PIM prescription rate: {pi_aphasia:.4f} ({pi_aphasia*100:.2f}%)")
    print(f"  No Aphasia group:")
    print(f"    Readmission rate: {p_obs_no_aphasia:.4f} ({p_obs_no_aphasia*100:.2f}%)")
    print(f"    PIM prescription rate: {pi_no_aphasia:.4f} ({pi_no_aphasia*100:.2f}%)")

    # Total observed disparity
    delta_total_obs = (p_obs_aphasia - p_obs_no_aphasia) * 1000
    print(f"\nTotal Observed Disparity: {delta_total_obs:+.2f} events per 1000\n")

    # Calculate counterfactual predictions P_ij
    scenarios = {
        'P_00': (0, 0),  # No aphasia, no PIM
        'P_01': (0, 1),  # No aphasia, has PIM
        'P_10': (1, 0),  # Has aphasia, no PIM
        'P_11': (1, 1)   # Has aphasia, has PIM
    }

    P = {} # predicted probabilities

    # for each scenario, set aphasia and PIM, predict, average
    # (marginalization over MH confounders)
    # results in P_00, P_01, P_10, P_11
    # P_ij = P( readmission | aphasia=i, PIM=j )

    for name, (aphasia_val, pim_val) in scenarios.items():
        df_scenario = df.copy()
        df_scenario['has_aphasia'] = aphasia_val
        df_scenario['has_any_pim'] = pim_val
        probs = model.predict(df_scenario)
        P[name] = probs.mean()

    print("Counterfactual Predicted Probabilities:")
    print(f"    P00 (No Aphasia, No PIM): {P['P_00']:.4f}")
    print(f"    P01 (No Aphasia, PIM):    {P['P_01']:.4f}")
    print(f"    P10 (Aphasia, No PIM):    {P['P_10']:.4f}")
    print(f"    P11 (Aphasia, PIM):       {P['P_11']:.4f}\n")

    # Decomposition components

    # 1. Differential PIM exposure (composition effect)
    # Uses non-aphasia group's PIM effect and difference in exposure rates
    delta_pim_exposure = (pi_aphasia - pi_no_aphasia) * (P['P_01'] - P['P_00']) * 1000

    # 2. Independent effect of aphasia (direct effect, no PIMs)
    delta_aphasia_direct = (P['P_10'] - P['P_00']) * 1000

    # 3. Interaction effect (differential response to PIMs)
    # Difference in PIM effects between groups
    pim_effect_aphasia = P['P_11'] - P['P_10']
    pim_effect_no_aphasia = P['P_01'] - P['P_00']
    delta_interaction = (pim_effect_aphasia - pim_effect_no_aphasia) * 1000

    # TODO/Note: This is a simplified decomposition.
    # Full decomposition would includ additional cross-terms
    # but this captures the main components for interpretation.

    # Predicted total disparity (using observed PIM rates)
    delta_total_pred = (pi_aphasia * P['P_11'] + (1 - pi_aphasia) * P['P_10']) - \
                       (pi_no_aphasia * P['P_01'] + (1 - pi_no_aphasia) * P['P_00'])
    delta_total_pred = delta_total_pred * 1000

    print("DECOMPOSITION RESULTS")

    rows = []

    rows.append({
        'Component': 'Baseline Risk (No Aphasia, No PIM)',
        'Value (per 1000)': P['P_00'] * 1000,
        'Interpretation': 'Baseline readmission risk'
    })

    rows.append({
        'Component': 'Differential PIM Exposure',
        'Value (per 1000)': delta_pim_exposure,
        'Interpretation': 'Due to different PIM prescription rates'
    })

    rows.append({
        'Component': 'Independent Effect of Aphasia',
        'Value (per 1000)': delta_aphasia_direct,
        'Interpretation': 'Direct effect of aphasia (without PIMs)'
    })

    rows.append({
        'Component': 'Interaction Effect',
        'Value (per 1000)': delta_interaction,
        'Interpretation': 'Differential response to PIMs between groups'
    })

    rows.append({
        'Component': 'Total Predicted Disparity',
        'Value (per 1000)': delta_total_pred,
        'Interpretation': 'Sum of components (model-based)'
    })

    rows.append({
        'Component': 'Total Observed Disparity',
        'Value (per 1000)': delta_total_obs,
        'Interpretation': 'Actual observed difference'
    })

    decomp_df = pd.DataFrame(rows)

    print(decomp_df.to_string(index=False))

    # Calculate percentage contributions
    print("PERCENTAGE CONTRIBUTIONS TO DISPARITY")

    if abs(delta_total_pred) > 0.001:  # Avoid division by zero
        pct_pim = (delta_pim_exposure / delta_total_pred) * 100
        pct_aphasia = (delta_aphasia_direct / delta_total_pred) * 100
        pct_interaction = (delta_interaction / delta_total_pred) * 100

        print(f"Differential PIM Exposure:      {pct_pim:6.1f}%")
        print(f"Independent Effect of Aphasia:  {pct_aphasia:6.1f}%")
        print(f"Interaction Effect:             {pct_interaction:6.1f}%")
        print(f"Total:                          {pct_pim + pct_aphasia + pct_interaction:6.1f}%")
    else:
        print("Total disparity is near zero - percentage contributions not meaningful")

    print("="*80 + "\n")

    return decomp_df
