"""
Utility functions for clinical impact analysis.
"""

def parse_scenario_name(scenario_name):
    """
    Parse scenario name into human-readable labels.

    Parameters
    scenario_name : str
        Scenario name (e.g., 'aphasia_pim', 'no_aphasia_no_pim')

    Returns
    tuple
        (aphasia_label, pim_label)
    """
    if scenario_name.startswith('aphasia') and not scenario_name.startswith('no_aphasia'):
        aphasia_label = "Aphasia"
    else:
        aphasia_label = "No Aphasia"

    # Check for PIM status
    if 'no_pim' in scenario_name:
        pim_label = "No PIM"
    else:
        pim_label = "PIM"

    return aphasia_label, pim_label


def format_scenario_label(aphasia_val, pim_val):
    """
    Format aphasia and PIM values into labels.

    Parameters
    aphasia_val : int
        Aphasia value (0 or 1)
    pim_val : int
        PIM value (0 or 1)

    Returns
    tuple
        (aphasia_label, pim_label)
    """
    aphasia_label = "Aphasia" if aphasia_val == 1 else "No Aphasia"
    pim_label = "PIM" if pim_val == 1 else "No PIM"
    return aphasia_label, pim_label
