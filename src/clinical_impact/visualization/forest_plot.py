"""
Forest plot visualization for clinical impact analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def plot_forest_plot(results_df, output_dir):
    """
    Create forest plot of odds ratios.

    Parameters
    results_df : p.df
        Results from fit_clinical_impact_model
    output_dir : str
        Directory to save plot
    """

    print("Creating forest plot...")

    # Exclude intercept
    plot_df = results_df[results_df['Variable'] != 'Intercept'].copy()

    # Sort by odds ratio
    plot_df = plot_df.sort_values('Odds Ratio')

    # Display table of values being plotted
    print("\nFOREST PLOT DATA (Odds Ratios with 95% CI)")
    display_df = plot_df[['Variable', 'Odds Ratio', 'OR 95% CI Lower', 'OR 95% CI Upper', 'P-value', 'Significant']].copy()
    print(display_df.to_string(index=False))
    print()
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(plot_df))

    # Plot OR with CI
    ax.scatter(plot_df['Odds Ratio'], y_pos, s=100, zorder=3, color='steelblue')

    for i, (_, row) in enumerate(plot_df.iterrows()):
        ax.plot([row['OR 95% CI Lower'], row['OR 95% CI Upper']], [i, i], 'k-', linewidth=2)

    # Reference line at OR=1
    ax.axvline(x=1, color='red', linestyle='--', linewidth=2, label='OR = 1 (no effect)')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df['Variable'])
    ax.set_xlabel('Odds Ratio (95% CI)', fontsize=12)
    ax.set_title('Clinical Impact Model: Odds Ratios for 180-Day Hospital Readmission',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    ax.legend()

    plt.tight_layout()

    output_file = os.path.join(output_dir, 'clinical_impact_forest_plot.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {output_file}\n")
