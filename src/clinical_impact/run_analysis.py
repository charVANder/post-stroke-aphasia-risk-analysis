"""
clinical impact analysis.
This script orchestrates the complete clinical impact analysis pipeline.
"""

import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from cohort_definition import apply_clinical_impact_cohort
from constants import REQUIRED_VARS
from models import fit_clinical_impact_model
from analysis import (
    predict_scenario_probabilities,
    bootstrap_confidence_intervals,
    calculate_events_per_1000,
    calculate_risk_differences,
    marginal_effects_decomposition,
    calculate_observed_rates
)
from visualization import (
    plot_forest_plot,
    plot_predicted_probabilities,
    plot_events_per_1000,
    plot_risk_differences,
    plot_decomposition
)


def main():

    print("CLINICAL IMPACT ANALYSIS: PIMs and Hospital Readmissions by Aphasia Status")

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This is 'src'
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # Go to project root, then data
    FIGS_DIR = os.path.join(BASE_DIR, "..", "figs")  # Go to project root, then figs
    os.makedirs(FIGS_DIR, exist_ok=True)

    INPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_engineered_features.csv')

    # Load data
    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} patients\n")

    # Apply clinical impact cohort definition (non-PIM-based)
    df = apply_clinical_impact_cohort(df)

    # Check for required variables
    missing_vars = [var for var in REQUIRED_VARS if var not in df.columns]
    if missing_vars:
        raise ValueError(f"Missing required variables: {missing_vars}")

    print("All required variables present.\n")

    # Part 1: Calculate observed rates
    observed_df = calculate_observed_rates(df)

    # Part 2: Fit logistic regression model
    model, results_df = fit_clinical_impact_model(df)

    # Part 3: Predict scenario probabilities (point estimates)
    predictions = predict_scenario_probabilities(model, df)

    # Part 4: Bootstrap confidence intervals
    prob_dict_ci = bootstrap_confidence_intervals(df, n_iterations=1000)

    # Part 5: Calculate events per 1000
    events_df = calculate_events_per_1000(prob_dict_ci)

    # Part 6: Calculate risk differences
    risk_diff_df = calculate_risk_differences(prob_dict_ci)

    # Part 7: Marginal effects decomposition
    decomp_df = marginal_effects_decomposition(model, df)

    # Save all results
    print("SAVING RESULTS")

    results_df.to_csv(os.path.join(DATA_DIR, 'clinical_impact_model_results.csv'), index=False)
    print(f"Saved: clinical_impact_model_results.csv")

    events_df.to_csv(os.path.join(DATA_DIR, 'clinical_impact_predicted_probabilities.csv'), index=False)
    print(f"Saved: clinical_impact_predicted_probabilities.csv")

    risk_diff_df.to_csv(os.path.join(DATA_DIR, 'clinical_impact_risk_differences.csv'), index=False)
    print(f"Saved: clinical_impact_risk_differences.csv")

    decomp_df.to_csv(os.path.join(DATA_DIR, 'clinical_impact_marginal_effects_decomposition.csv'), index=False)
    print(f"Saved: clinical_impact_marginal_effects_decomposition.csv")

    observed_df.to_csv(os.path.join(DATA_DIR, 'clinical_impact_observed_rates.csv'), index=False)
    print(f"Saved: clinical_impact_observed_rates.csv")

    # Create all visualizations
    print("CREATING VISUALIZATIONS")
    plot_forest_plot(results_df, FIGS_DIR)
    plot_predicted_probabilities(events_df, FIGS_DIR)
    plot_events_per_1000(events_df, FIGS_DIR)
    plot_risk_differences(risk_diff_df, FIGS_DIR)
    plot_decomposition(decomp_df, FIGS_DIR)

    print("ANALYSIS COMPLETE!")
    print(f"\nResults saved to:")
    print(f"    Data files: {DATA_DIR}")
    print(f"    Figures: {FIGS_DIR}")
    print("\nGenerated files:")
    print("  - clinical_impact_model_results.csv")
    print("  - clinical_impact_predicted_probabilities.csv")
    print("  - clinical_impact_risk_differences.csv")
    print("  - clinical_impact_marginal_effects_decomposition.csv")
    print("  - clinical_impact_observed_rates.csv")
    print("  - clinical_impact_forest_plot.png")
    print("  - clinical_impact_predicted_probs_barplot.png")
    print("  - clinical_impact_events_per_1000.png")
    print("  - clinical_impact_risk_differences.png")
    print("  - clinical_impact_decomposition_barplot.png")


if __name__ == '__main__':
    main()
