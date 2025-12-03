"""
Bar plot visualizations for clinical impact analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def _extract_plot_data(df, value_col, ci_lower_col, ci_upper_col):
    """
    Helper to extract plotting data from df.

    Parameters
    df : pandas.DataFrame
        DataFrame with scenario data
    value_col : str
        Column name for values
    ci_lower_col : str
        Column name for lower CI
    ci_upper_col : str
        Column name for upper CI

    Returns
        (aphasia_pim, aphasia_no_pim, no_aphasia_pim, no_aphasia_no_pim,
         aphasia_pim_ci, aphasia_no_pim_ci, no_aphasia_pim_ci, no_aphasia_no_pim_ci)
    """
    aphasia_df = df[df['Aphasia Status'] == 'Aphasia']
    no_aphasia_df = df[df['Aphasia Status'] == 'No Aphasia']

    # Extract values
    aphasia_pim = aphasia_df[aphasia_df['PIM Status'] == 'PIM'][value_col].values[0]
    aphasia_no_pim = aphasia_df[aphasia_df['PIM Status'] == 'No PIM'][value_col].values[0]
    no_aphasia_pim = no_aphasia_df[no_aphasia_df['PIM Status'] == 'PIM'][value_col].values[0]
    no_aphasia_no_pim = no_aphasia_df[no_aphasia_df['PIM Status'] == 'No PIM'][value_col].values[0]

    # Extract CIs
    aphasia_pim_ci = (
        aphasia_df[aphasia_df['PIM Status'] == 'PIM'][ci_lower_col].values[0],
        aphasia_df[aphasia_df['PIM Status'] == 'PIM'][ci_upper_col].values[0]
    )
    aphasia_no_pim_ci = (
        aphasia_df[aphasia_df['PIM Status'] == 'No PIM'][ci_lower_col].values[0],
        aphasia_df[aphasia_df['PIM Status'] == 'No PIM'][ci_upper_col].values[0]
    )
    no_aphasia_pim_ci = (
        no_aphasia_df[no_aphasia_df['PIM Status'] == 'PIM'][ci_lower_col].values[0],
        no_aphasia_df[no_aphasia_df['PIM Status'] == 'PIM'][ci_upper_col].values[0]
    )
    no_aphasia_no_pim_ci = (
        no_aphasia_df[no_aphasia_df['PIM Status'] == 'No PIM'][ci_lower_col].values[0],
        no_aphasia_df[no_aphasia_df['PIM Status'] == 'No PIM'][ci_upper_col].values[0]
    )

    return (aphasia_pim, aphasia_no_pim, no_aphasia_pim, no_aphasia_no_pim,
            aphasia_pim_ci, aphasia_no_pim_ci, no_aphasia_pim_ci, no_aphasia_no_pim_ci)


def plot_predicted_probabilities(prob_df, output_dir):
    """
    bar plot of predicted probabilities.

    Parameters
    prob_df : p.df
        DataFrame from calculate_events_per_1000
    output_dir : str
        Directory to save plot
    """

    print("Creating predicted probabilities plot...")

    # Display data table
    print("\nPREDICTED PROBABILITIES DATA")
    display_df = prob_df[['Aphasia Status', 'PIM Status', 'Probability',
                           'Probability 95% CI Lower', 'Probability 95% CI Upper']].copy()
    print(display_df.to_string(index=False))
    print()

    fig, ax = plt.subplots(figsize=(12, 8))

    # Prepare data for grouped bar plot
    x = np.arange(2)  # 2 groups: Aphasia, No Aphasia
    width = 0.35

    # Extract data using helper function
    (aphasia_pim, aphasia_no_pim, no_aphasia_pim, no_aphasia_no_pim,
     aphasia_pim_ci, aphasia_no_pim_ci, no_aphasia_pim_ci, no_aphasia_no_pim_ci) = \
        _extract_plot_data(prob_df, 'Probability', 'Probability 95% CI Lower', 'Probability 95% CI Upper')

    # Plot bars
    pim_vals = [aphasia_pim, no_aphasia_pim]
    no_pim_vals = [aphasia_no_pim, no_aphasia_no_pim]

    pim_errors = [
        [max(0, aphasia_pim - aphasia_pim_ci[0]), max(0, no_aphasia_pim - no_aphasia_pim_ci[0])],
        [max(0, aphasia_pim_ci[1] - aphasia_pim), max(0, no_aphasia_pim_ci[1] - no_aphasia_pim)]
    ]

    no_pim_errors = [
        [max(0, aphasia_no_pim - aphasia_no_pim_ci[0]), max(0, no_aphasia_no_pim - no_aphasia_no_pim_ci[0])],
        [max(0, aphasia_no_pim_ci[1] - aphasia_no_pim), max(0, no_aphasia_no_pim_ci[1] - no_aphasia_no_pim)]
    ]

    bars1 = ax.bar(x - width / 2, pim_vals, width, label='With PIM',
                   color='red', alpha=0.8, yerr=pim_errors, capsize=5)
    bars2 = ax.bar(x + width / 2, no_pim_vals, width, label='Without PIM',
                   color='blue', alpha=0.8, yerr=no_pim_errors, capsize=5)

    ax.set_ylabel('Predicted Probability of 180-Day Readmission', fontsize=12)
    ax.set_title('Predicted Readmission Probabilities by Aphasia and PIM Status\n(with 95% Confidence Intervals)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['Aphasia', 'No Aphasia'], fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    output_file = os.path.join(output_dir, 'clinical_impact_predicted_probs_barplot.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")


def plot_events_per_1000(events_df, output_dir):
    """
    Create bar plot of expected events per 1000 patients.

    Parameters
    events_df : p.df
        DataFrame from calculate_events_per_1000
    output_dir : str
        Directory to save plot
    """

    print("Creating events per 1000 plot...")

    # Display data table
    print("\nEVENTS PER 1000 PATIENTS DATA")
    display_df = events_df[['Aphasia Status', 'PIM Status', 'Events per 1000',
                             'Events per 1000 95% CI Lower', 'Events per 1000 95% CI Upper']].copy()
    print(display_df.to_string(index=False))
    print()

    fig, ax = plt.subplots(figsize=(12, 8))

    # Prepare data
    x = np.arange(2)
    width = 0.35

    # Extract data using helper function
    (aphasia_pim, aphasia_no_pim, no_aphasia_pim, no_aphasia_no_pim,
     aphasia_pim_ci, aphasia_no_pim_ci, no_aphasia_pim_ci, no_aphasia_no_pim_ci) = \
        _extract_plot_data(events_df, 'Events per 1000', 'Events per 1000 95% CI Lower', 'Events per 1000 95% CI Upper')

    # Plot bars
    pim_vals = [aphasia_pim, no_aphasia_pim]
    no_pim_vals = [aphasia_no_pim, no_aphasia_no_pim]

    # Calculate error bars
    pim_errors = [
        [max(0, aphasia_pim - aphasia_pim_ci[0]), max(0, no_aphasia_pim - no_aphasia_pim_ci[0])],
        [max(0, aphasia_pim_ci[1] - aphasia_pim), max(0, no_aphasia_pim_ci[1] - no_aphasia_pim)]
    ]

    no_pim_errors = [
        [max(0, aphasia_no_pim - aphasia_no_pim_ci[0]), max(0, no_aphasia_no_pim - no_aphasia_no_pim_ci[0])],
        [max(0, aphasia_no_pim_ci[1] - aphasia_no_pim), max(0, no_aphasia_no_pim_ci[1] - no_aphasia_no_pim)]
    ]

    bars1 = ax.bar(x - width / 2, pim_vals, width, label='With PIM',
                   color='red', alpha=0.8, yerr=pim_errors, capsize=5)
    bars2 = ax.bar(x + width / 2, no_pim_vals, width, label='Without PIM',
                   color='blue', alpha=0.8, yerr=no_pim_errors, capsize=5)

    ax.set_ylabel('Expected 180-Day Readmissions per 1000 Patients', fontsize=12)
    ax.set_title('Expected Hospital Readmissions per 1000 Patients\n(with 95% Confidence Intervals)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['Aphasia', 'No Aphasia'], fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    output_file = os.path.join(output_dir, 'clinical_impact_events_per_1000.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")


def plot_risk_differences(risk_diff_df, output_dir):
    """
    Create bar plot of risk differences.

    Parameters
    risk_diff_df : p.df
        df from calculate_risk_differences
    output_dir : str
        Directory to save plot
    """

    print("Creating risk differences plot...")

    # Display data table
    print("\nRISK DIFFERENCES DATA")
    display_df = risk_diff_df[['Comparison', 'Absolute Risk Difference (per 1000)', 'Relative Risk Difference (%)']].copy()
    print(display_df.to_string(index=False))
    print()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Absolute risk differences
    y_pos = np.arange(len(risk_diff_df))

    colors = ['blue', 'blue', 'red', 'red']  # No PIM = blue, PIM = red

    bars = ax1.barh(y_pos, risk_diff_df['Absolute Risk Difference (per 1000)'],
                    color=colors, alpha=0.8)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(risk_diff_df['Comparison'], fontsize=10)
    ax1.set_xlabel('Absolute Risk Difference\n(Events per 1000 Patients)', fontsize=11)
    ax1.set_title('Absolute Risk Differences', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, risk_diff_df['Absolute Risk Difference (per 1000)'])):
        ax1.text(val, bar.get_y() + bar.get_height() / 2.,
                 f' {val:+.1f}',
                 ha='left' if val > 0 else 'right',
                 va='center', fontsize=10)

    # Relative risk differences
    bars = ax2.barh(y_pos, risk_diff_df['Relative Risk Difference (%)'],
                    color=colors, alpha=0.8)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(risk_diff_df['Comparison'], fontsize=10)
    ax2.set_xlabel('Relative Risk Difference (%)', fontsize=11)
    ax2.set_title('Relative Risk Differences', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, risk_diff_df['Relative Risk Difference (%)'])):
        ax2.text(val, bar.get_y() + bar.get_height() / 2.,
                 f' {val:+.1f}%',
                 ha='left' if val > 0 else 'right',
                 va='center', fontsize=10)

    plt.suptitle('Risk Differences: Impact of PIMs and Aphasia on Hospital Readmission',
                 y=1.02)
    plt.tight_layout()

    output_file = os.path.join(output_dir, 'clinical_impact_risk_differences.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")
