"""
Configuration constants for clinical impact analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Model formula (shared between fit and bootstrap)
# Removed interaction term (has_aphasia:has_any_pim) - consistently non-significant (p>0.95)
# and contributes to quasi-separation issues
MODEL_FORMULA = """has_180day_readmission ~ has_aphasia + has_any_pim +
                   has_depression + has_anxiety + has_ptsd +
                   has_bipolar + has_schizophrenia + has_psychotic_disorder +
                   has_seizure"""

# Scenario definitions (shared across functions)
SCENARIOS = {
    'aphasia_pim': (1, 1),
    'aphasia_no_pim': (1, 0),
    'no_aphasia_pim': (0, 1),
    'no_aphasia_no_pim': (0, 0)
}

# Required variables for analysis
REQUIRED_VARS = [
    'has_180day_readmission', 'has_aphasia', 'has_any_pim',
    'has_depression', 'has_anxiety', 'has_ptsd', 'has_bipolar',
    'has_schizophrenia', 'has_psychotic_disorder', 'has_seizure'
]

# Interaction term name (None since we removed it from the model)
INTERACTION_TERM = None
