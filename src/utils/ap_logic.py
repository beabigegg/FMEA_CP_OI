# Utility functions and constants for AIAG-VDA Action Priority (AP) logic.
#
# This module defines descriptive rating scales for Severity (S), Occurrence (O)
# and Detection (D) and provides a helper function to calculate an Action
# Priority (AP) level (High, Medium or Low) based on the ratings.  The rating
# descriptions below are derived from the AIAG‑VDA FMEA manual.  In the
# original tables the severity, occurrence and detection rankings run from 1 to
# 10.  Ratings of 10 correspond to the most severe, most likely or least
# detectable conditions, while 1 indicates the least severe, least likely or
# most easily detected conditions【160702036562110†L392-L437】.
#
# The AP calculation implemented here follows the guidance of the FMEA
# alignment document【160702036562110†L392-L437】.  It is intentionally
# simplified – the official AP table spans all 1 000 combinations of S, O and D.
# The logic below captures the highest‑level rules: high severity combined with
# high or moderate occurrence and poor detection yields a High priority;
# medium severity with moderate occurrence and moderate detection yields a High
# priority; medium severity with moderate occurrence but good detection yields
# Medium priority; low severity combinations are generally Low priority.  Any
# combinations not explicitly covered fall back to Low.  If your organisation
# has a customised AP matrix, this module can be extended accordingly.

from typing import Dict

# Severity rating descriptions (1=least severe, 10=most severe) based on AIAG‑VDA FMEA
# manual examples【160702036562110†L483-L520】.
SEVERITY_LEVELS: Dict[int, str] = {
    10: "Affects safe operation of the vehicle or the health of the user【160702036562110†L483-L520】",
    9: "Noncompliance with regulations【160702036562110†L489-L491】",
    8: "Loss of essential function necessary for normal operation during service life【160702036562110†L492-L495】",
    7: "Degradation of essential function necessary for normal operation【160702036562110†L496-L499】",
    6: "Loss of convenience function【160702036562110†L501-L503】",
    5: "Degradation of convenience function【160702036562110†L504-L506】",
    4: "Perceived quality unacceptable to most customers【160702036562110†L507-L509】",
    3: "Perceived quality unacceptable to many customers【160702036562110†L511-L513】",
    2: "Perceived quality unacceptable to some customers【160702036562110†L515-L517】",
    1: "No discernible effect【160702036562110†L519-L520】",
}

# Occurrence rating descriptions (1=least likely, 10=most likely) based on AIAG‑VDA FMEA
# manual examples【160702036562110†L529-L559】.
OCCURRENCE_LEVELS: Dict[int, str] = {
    10: "Occurrence unknown or extremely high; new technology without experience【160702036562110†L529-L531】",
    9: "Failure cause is likely to occur during design life【160702036562110†L532-L534】",
    8: "Failure cause may occur often in the field【160702036562110†L535-L537】",
    7: "Failure cause may occur frequently in the field【160702036562110†L537-L540】",
    6: "Failure cause may occur somewhat frequently【160702036562110†L540-L542】",
    5: "Failure cause may occur occasionally【160702036562110†L543-L545】",
    4: "Failure cause may occur rarely【160702036562110†L547-L548】",
    3: "Failure predicted to occur in isolated cases【160702036562110†L549-L551】",
    2: "Failure predicted to be significantly below acceptance level but isolated cases possible【160702036562110†L552-L555】",
    1: "Failure cannot occur or is significantly below acceptance level【160702036562110†L556-L559】",
}

# Detection rating descriptions (1=most easily detected, 10=least detectable) based on AIAG‑VDA FMEA
# manual examples【160702036562110†L569-L603】.
DETECTION_LEVELS: Dict[int, str] = {
    10: "Fault cannot be detected at all or not during the fault tolerant interval; no monitoring【160702036562110†L569-L571】",
    9: "Fault is almost never detected; response may not reliably occur【160702036562110†L573-L574】",
    8: "Fault detected in very few operating conditions; response may not always occur【160702036562110†L576-L579】",
    7: "Low probability of detection or response【160702036562110†L581-L582】",
    6: "Fault will be detected and responded to in many operating conditions【160702036562110†L584-L585】",
    5: "Fault will be detected and responded to in very many operating conditions【160702036562110†L586-L588】",
    4: "Fault will be detected and responded to in most operating conditions【160702036562110†L590-L591】",
    3: "Fault automatically detected and responded to with high probability【160702036562110†L592-L594】",
    2: "Fault always detected automatically in all relevant operating conditions【160702036562110†L597-L598】",
    1: "Fault always detected automatically and responded in any operating condition【160702036562110†L601-L603】",
}

def _classify_severity(value: int) -> str:
    """
    Classify a numeric severity rating into the severity band used by the AIAG–VDA
    Action Priority table.  The handbook groups severity ratings into the
    following bands: 9–10, 7–8, 4–6, 2–3 and 1【160702036562110†L392-L437】.

    Args:
        value (int): Severity rating between 1 and 10.

    Returns:
        str: A label representing the severity band (e.g. '9-10', '7-8').
    """
    if value == 1:
        return '1'
    if 2 <= value <= 3:
        return '2-3'
    if 4 <= value <= 6:
        return '4-6'
    if 7 <= value <= 8:
        return '7-8'
    return '9-10'


def _classify_occurrence(value: int) -> str:
    """
    Classify an occurrence rating into the bands defined by the AIAG–VDA AP
    table.  Occurrence ratings are grouped into 8–10, 6–7, 4–5, 2–3 and 1
    bands【160702036562110†L392-L437】.

    Args:
        value (int): Occurrence rating between 1 and 10.

    Returns:
        str: Band label representing the occurrence range.
    """
    if value == 1:
        return '1'
    if 2 <= value <= 3:
        return '2-3'
    if 4 <= value <= 5:
        return '4-5'
    if 6 <= value <= 7:
        return '6-7'
    return '8-10'


def _classify_detection(value: int) -> str:
    """
    Classify a detection rating into bands as defined in the AP table.  Detection
    ratings are grouped into 7–10, 5–6, 2–4 and 1 bands【160702036562110†L392-L437】.

    Args:
        value (int): Detection rating between 1 and 10.

    Returns:
        str: Band label for the detection range.
    """
    if value == 1:
        return '1'
    if 2 <= value <= 4:
        return '2-4'
    if 5 <= value <= 6:
        return '5-6'
    return '7-10'


# A nested mapping representing the official AIAG‑VDA Action Priority table.
# The top-level keys are severity bands, the second level are occurrence bands
# and the third level are detection bands.  Each leaf value is the AP rating
# ('H', 'M' or 'L').  This table was transcribed from the FMEA AP table【160702036562110†L392-L437】.
_AP_TABLE = {
    '9-10': {
        '8-10': {'7-10': 'H', '5-6': 'H', '2-4': 'H', '1': 'H'},
        '6-7':  {'7-10': 'H', '5-6': 'H', '2-4': 'H', '1': 'H'},
        '4-5':  {'7-10': 'H', '5-6': 'H', '2-4': 'H', '1': 'M'},
        '2-3':  {'7-10': 'H', '5-6': 'M', '2-4': 'L', '1': 'L'},
        '1':    {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L', '1-10': 'L'},  # fall‑back for severity 9‑10 & occ=1
    },
    '7-8': {
        '8-10': {'7-10': 'H', '5-6': 'H', '2-4': 'H', '1': 'H'},
        '6-7':  {'7-10': 'H', '5-6': 'H', '2-4': 'H', '1': 'M'},
        '4-5':  {'7-10': 'H', '5-6': 'M', '2-4': 'M', '1': 'M'},
        '2-3':  {'7-10': 'M', '5-6': 'M', '2-4': 'L', '1': 'L'},
        '1':    {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L', '1-10': 'L'},
    },
    '4-6': {
        '8-10': {'7-10': 'H', '5-6': 'H', '2-4': 'M', '1': 'M'},
        '6-7':  {'7-10': 'M', '5-6': 'M', '2-4': 'M', '1': 'L'},
        '4-5':  {'7-10': 'M', '5-6': 'L', '2-4': 'L', '1': 'L'},
        '2-3':  {'7-10': 'L', '5-6': 'L', '2-4': 'L', '1': 'L'},
        '1':    {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L', '1-10': 'L'},
    },
    '2-3': {
        '8-10': {'7-10': 'M', '5-6': 'M', '2-4': 'L', '1': 'L'},
        '6-7':  {'7-10': 'L', '5-6': 'L', '2-4': 'L', '1': 'L'},
        '4-5':  {'7-10': 'L', '5-6': 'L', '2-4': 'L', '1': 'L'},
        '2-3':  {'7-10': 'L', '5-6': 'L', '2-4': 'L', '1': 'L'},
        '1':    {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L', '1-10': 'L'},
    },
    '1': {
        # When severity is 1, the AP is always low regardless of O and D【160702036562110†L435-L437】.
        '1':    {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L', '1-10': 'L'},
        '2-3':  {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L'},
        '4-5':  {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L'},
        '6-7':  {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L'},
        '8-10': {'1': 'L', '2-4': 'L', '5-6': 'L', '7-10': 'L'},
    }
}


def calculate_ap(severity: int, occurrence: int, detection: int) -> str:
    """
    Determine the Action Priority (AP) rating for a given set of Severity (S),
    Occurrence (O) and Detection (D) ratings.  This implementation follows
    the official AIAG–VDA Action Priority table by classifying each rating into
    a band and looking up the AP value in the `_AP_TABLE` mapping【160702036562110†L392-L437】.

    Args:
        severity (int): Severity rating on a 1–10 scale.
        occurrence (int): Occurrence rating on a 1–10 scale.
        detection (int): Detection rating on a 1–10 scale.

    Returns:
        str: The Action Priority as 'H', 'M' or 'L'.

    Raises:
        ValueError: If any rating is outside the 1–10 range.
    """
    if not (1 <= severity <= 10 and 1 <= occurrence <= 10 and 1 <= detection <= 10):
        raise ValueError("Severity, occurrence and detection must be between 1 and 10.")

    # Map the numeric ratings into their respective bands
    s_band = _classify_severity(severity)
    o_band = _classify_occurrence(occurrence)
    d_band = _classify_detection(detection)

    # Retrieve the AP value from the nested mapping.  Not every combination
    # explicitly exists in the table (e.g. severity 9–10 & occurrence 1).  In
    # those cases we fall back to 'L' as per the handbook’s guidance【160702036562110†L435-L437】.
    severity_map = _AP_TABLE.get(s_band, {})
    occurrence_map = severity_map.get(o_band, {})
    # Some severity/occurrence bands have a catch‑all entry keyed by '1-10'.
    ap = occurrence_map.get(d_band)
    if ap is None:
        # Try a catch‑all detection key if present
        ap = occurrence_map.get('1-10')
    if ap is None:
        # Unknown combination defaults to Low priority
        ap = 'L'
    return ap