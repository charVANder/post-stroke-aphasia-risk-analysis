"""
Decomposition plot visualization for clinical impact analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def plot_decomposition(decomp_df, output_dir):
    """
    Create visualization of marginal effects decomposition.

    Parameters
    decomp_df : p.df
        DataFrame from marginal_effects_decomposition
    output_dir : str
        Directory to save plot
    """

    print("Creating decomposition plot...")

    # Extract key components (exclude baseline and total rows)
    components = decomp_df[decomp_df['Component'].isin([
        'Differential PIM Exposure',
        'Independent Effect of Aphasia',
        'Interaction Effect'
    ])].copy()

    # Display data table
    print("\nDECOMPOSITION COMPONENTS DATA")
    display_df = components[['Component', 'Value (per 1000)', 'Interpretation']].copy()
    print(display_df.to_string(index=False))
    print()

    fig, ax = plt.subplots(figsize=(12, 8))

    y_pos = np.arange(len(components))
    values = components['Value (per 1000)'].values

    colors = ['#e74c3c', '#3498db', '#f39c12']  # Red, Blue, Orange

    bars = ax.barh(y_pos, values, color=colors, alpha=0.8)

    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(components['Component'], fontsize=11)
    ax.set_xlabel('Contribution to Readmission Disparity\n(Events per 1000 Patients)',
                  fontsize=12)
    ax.set_title('Marginal Effects Decomposition:\nSources of Readmission Disparity Between Aphasia Groups',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # value labels and interpretations
    for i, (bar, val, interp) in enumerate(zip(bars, values, components['Interpretation'])):
        ax.text(val, bar.get_y() + bar.get_height()/2.,
               f' {val:+.2f}',
               ha='left' if val > 0 else 'right',
               va='center', fontsize=11, fontweight='bold')

    # legend with interpretations
    legend_text = '\n'.join([
        f"{comp}: {interp}"
        for comp, interp in zip(components['Component'], components['Interpretation'])
    ])

    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    output_file = os.path.join(output_dir, 'clinical_impact_decomposition_barplot.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f" Saved: {output_file}\n")
