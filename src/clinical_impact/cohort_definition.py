"""
Cohort definition for clinical impact analysis.

Uses the full post-stroke cohort (all 53,068 patients) to avoid circular definition.
No "high-risk" filtering applied - analyzes PIM effects across all stroke patients.
"""

import pandas as pd


def apply_clinical_impact_cohort(df):
    """
    Use full post-stroke cohort for clinical impact analysis.

    avoids circular definition issues by not filtering based on any
    PIM-related or medication-related criteria. Simply analyzes the
    relationship between PIMs and readmissions in all stroke patients

   using full post-stroke cohort because in high-risk cohort,
   patients without PIMs have almost zero readmissions making

    Parameters
    df : pd.df
        Input dataframe with all stroke patients

    Returns
    -------
    pd.df
        Same as input - full cohort with no filtering
    """
    print("="*80)
    print("CLINICAL IMPACT COHORT DEFINITION")
    print("="*80)
    print(f"\nCohort Selection:")
    print(f"  Using FULL post-stroke cohort (no high-risk filtering)")
    print(f"  Total patients: {len(df):,}")
    print(f"\nRationale:")
    print(f"  - Avoids circular definition issues")
    print(f"  - Analyzes PIM effects across ALL stroke patients")
    print(f"  - More generalizable findings")
    print("\n" + "="*80 + "\n")

    return df
