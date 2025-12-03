"""
Risk calculation functions for clinical impact analysis.
"""

import pandas as pd
import numpy as np

from utils import parse_scenario_name, format_scenario_label


def calculate_events_per_1000(prob_dict):
    """
    Convert probabilities to events per 1000 patients.

    Parameters
    prob_dict : dict
        dict with scenario probabilities (from bootstrap_confidence_intervals)

    Returns
    p.df
        df with scenarios, probabilities, and events per 1000
    """

    print("EXPECTED EVENTS PER 1000 PATIENTS")

    rows = []

    for scenario_name, values in prob_dict.items():
        # Format scenario name
        aphasia_label, pim_label = parse_scenario_name(scenario_name)

        # Calculate events per 1000
        mean_events = values['mean'] * 1000
        lower_events = values['lower_ci'] * 1000
        upper_events = values['upper_ci'] * 1000

        rows.append({
            'Aphasia Status': aphasia_label,
            'PIM Status': pim_label,
            'Probability': values['mean'],
            'Probability 95% CI Lower': values['lower_ci'],
            'Probability 95% CI Upper': values['upper_ci'],
            'Events per 1000': mean_events,
            'Events per 1000 95% CI Lower': lower_events,
            'Events per 1000 95% CI Upper': upper_events
        })

        print(f"{aphasia_label} + {pim_label:8s}: "
              f"    {mean_events:.1f} events per 1000 patients "
              f"    (95% CI: {lower_events:.1f} - {upper_events:.1f})")

    events_df = pd.DataFrame(rows)
    return events_df


def calculate_risk_differences(prob_dict):
    """
    Calculate all pairwise risk differences (absolute and relative).

    Comparisons:
    1. Within aphasia group: PIM vs No PIM
    2. Within non-aphasia group: PIM vs No PIM
    3. Between groups with PIMs: Aphasia vs No Aphasia
    4. Between groups without PIMs: Aphasia vs No Aphasia

    Parameters
    prob_dict : dict
        Dictionary with scenario probabilities (from bootstrap_confidence_intervals)

    Returns
    p.df
        df with all risk differences
    """

    print("RISK DIFFERENCES")

    # Extract probabilities
    p_aphasia_pim = prob_dict['aphasia_pim']['mean']
    p_aphasia_no_pim = prob_dict['aphasia_no_pim']['mean']
    p_no_aphasia_pim = prob_dict['no_aphasia_pim']['mean']
    p_no_aphasia_no_pim = prob_dict['no_aphasia_no_pim']['mean']

    rows = []

    # 1. Within aphasia group: PIM vs No PIM
    abs_diff = (p_aphasia_pim - p_aphasia_no_pim) * 1000
    rel_diff = ((p_aphasia_pim / p_aphasia_no_pim) - 1) * 100

    rows.append({
        'Comparison': 'Aphasia: PIM vs No PIM',
        'Group': 'Within Aphasia',
        'Absolute Risk Difference (per 1000)': abs_diff,
        'Relative Risk Difference (%)': rel_diff
    })

    print(f"Within Aphasia Group (PIM vs No PIM):")
    print(f"  Absolute: {abs_diff:+.1f} events per 1000")
    print(f"  Relative: {rel_diff:+.1f}%\n")

    # 2. Within non-aphasia group: PIM vs No PIM
    abs_diff = (p_no_aphasia_pim - p_no_aphasia_no_pim) * 1000
    rel_diff = ((p_no_aphasia_pim / p_no_aphasia_no_pim) - 1) * 100

    rows.append({
        'Comparison': 'No Aphasia: PIM vs No PIM',
        'Group': 'Within No Aphasia',
        'Absolute Risk Difference (per 1000)': abs_diff,
        'Relative Risk Difference (%)': rel_diff
    })

    print(f"Within No Aphasia Group (PIM vs No PIM):")
    print(f"    Absolute: {abs_diff:+.1f} events per 1000")
    print(f"    Relative: {rel_diff:+.1f}%\n")

    # 3. Between groups with PIMs: Aphasia vs No Aphasia
    abs_diff = (p_aphasia_pim - p_no_aphasia_pim) * 1000
    rel_diff = ((p_aphasia_pim / p_no_aphasia_pim) - 1) * 100

    rows.append({
        'Comparison': 'With PIMs: Aphasia vs No Aphasia',
        'Group': 'Between Groups (with PIMs)',
        'Absolute Risk Difference (per 1000)': abs_diff,
        'Relative Risk Difference (%)': rel_diff
    })

    print(f"Among Patients with PIMs (Aphasia vs No Aphasia):")
    print(f"    Absolute: {abs_diff:+.1f} events per 1000")
    print(f"    Relative: {rel_diff:+.1f}%\n")

    # 4. Between groups without PIMs: Aphasia vs No Aphasia
    abs_diff = (p_aphasia_no_pim - p_no_aphasia_no_pim) * 1000
    rel_diff = ((p_aphasia_no_pim / p_no_aphasia_no_pim) - 1) * 100

    rows.append({
        'Comparison': 'Without PIMs: Aphasia vs No Aphasia',
        'Group': 'Between Groups (without PIMs)',
        'Absolute Risk Difference (per 1000)': abs_diff,
        'Relative Risk Difference (%)': rel_diff
    })

    print(f"Among Patients without PIMs (Aphasia vs No Aphasia):")
    print(f"  Absolute: {abs_diff:+.1f} events per 1000")
    print(f"  Relative: {rel_diff:+.1f}%")

    risk_diff_df = pd.DataFrame(rows)
    return risk_diff_df


def calculate_observed_rates(df):
    """
    Calculate observed readmission and PIM rates by aphasia status.

    Parameters
    df : p.df
        Input df

    Returns
    p.df
        df with observed rates and sample sizes
    """

    print("OBSERVED RATES BY GROUP")

    rows = []

    for aphasia_val in [0, 1]:
        group = df[df['has_aphasia'] == aphasia_val]
        n = len(group)

        readmission_rate = group['has_180day_readmission'].mean()
        readmission_count = group['has_180day_readmission'].sum()

        pim_rate = group['has_any_pim'].mean()
        pim_count = group['has_any_pim'].sum()

        aphasia_label, _ = format_scenario_label(aphasia_val, 0)

        rows.append({
            'Group': aphasia_label,
            'N': n,
            '180-day Readmission Rate': readmission_rate,
            '180-day Readmission Count': readmission_count,
            'PIM Prescription Rate': pim_rate,
            'PIM Prescription Count': pim_count
        })

        print(f"{aphasia_label} Group (N={n:,}):")
        print(f"  180-day Readmission: {readmission_count:,} ({readmission_rate*100:.2f}%)")
        print(f"  PIM Prescription:    {pim_count:,} ({pim_rate*100:.2f}%)\n")

    observed_df = pd.DataFrame(rows)
    return observed_df
