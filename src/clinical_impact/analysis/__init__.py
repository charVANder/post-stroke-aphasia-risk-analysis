"""
Clinical impact analysis functions.
"""

from .predictions import predict_scenario_probabilities, bootstrap_confidence_intervals
from .risk_calculations import (
    calculate_events_per_1000,
    calculate_risk_differences,
    calculate_observed_rates
)
from .decomposition import marginal_effects_decomposition

__all__ = [
    'predict_scenario_probabilities',
    'bootstrap_confidence_intervals',
    'calculate_events_per_1000',
    'calculate_risk_differences',
    'calculate_observed_rates',
    'marginal_effects_decomposition'
]
