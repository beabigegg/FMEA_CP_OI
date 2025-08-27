"""
Enhanced parser for AIAG‑VDA Control Plan workbooks.

This module exposes a single ``parse`` function which reads the
``REV.04`` sheet from a Control Plan Excel file and returns
structured records.  Compared to the original implementation this
version:

* Reads the header using three rows (rows 7–9 in Excel) to capture
  multi‑level column names.
* Flattens the multi‑level header by joining non‑empty levels and
  removing newlines and redundant spaces.
* Extracts additional fields beyond the original four, including
  process and product characteristics, specification/tolerance,
  sample size/frequency, special characteristic class, equipment and
  reaction plan.
* Performs forward‑fill on the process name and characteristic
  columns to handle merged cells.
* Filters out rows without a product characteristic.

The function accepts either a string path to a ``.xlsx`` file or any
file‑like object that ``pandas.read_excel`` can consume (e.g. a
``BytesIO`` stream).
"""

from __future__ import annotations

import re
import pandas as pd
from typing import Any, Dict, List, Union


def _flatten_columns(columns: pd.MultiIndex) -> List[str]:
    """Flatten a pandas MultiIndex into single strings.

    Each level in the index is stripped of whitespace and newlines; any
    level starting with ``Unnamed`` or evaluating to NaN is ignored.
    Remaining parts are joined with a single space.  Multiple
    consecutive spaces and newlines are reduced to a single space.
    """
    flattened: List[str] = []
    for col in columns:
        parts: List[str] = []
        for level in col:
            if level is None:
                continue
            level_str = str(level).strip()
            if not level_str or level_str.startswith("Unnamed"):
                continue
            # Replace all whitespace (including newlines) with single spaces
            level_str = re.sub(r"\s+", " ", level_str)
            parts.append(level_str)
        flattened.append(" ".join(parts))
    return flattened


def parse(file_source: Union[str, Any]) -> Dict[str, Any]:
    """Parse a Control Plan Excel file and extract structured records.

    Parameters
    ----------
    file_source : Union[str, Any]
        The path to a ``.xlsx`` file or a file‑like object containing
        the workbook.

    Returns
    -------
    dict
        A dictionary with keys ``status`` and ``data``.  On success
        ``status`` will be ``"success"`` and ``data`` contains a list
        of dictionaries representing each row of the Control Plan.  On
        failure ``status`` will be ``"error"`` and ``message`` will
        describe the problem.
    """
    target_sheet = "REV.04"
    header_rows = [6, 7, 8]  # rows 7–9 in Excel (0-indexed)
    try:
        df = pd.read_excel(
            file_source,
            sheet_name=target_sheet,
            header=header_rows,
        )
    except Exception as exc:
        return {"status": "error", "message": f"Failed to read Excel: {exc}"}

    # Flatten the multi‑level column names
    flattened_cols = _flatten_columns(df.columns)
    df.columns = flattened_cols

    # Mapping of friendly field names to flattened column names
    col_map = {
        "process_name": "Process Name Operation Description",
        "product_characteristic": "Characteristics Product",
        "process_characteristic": "Characteristics Process",
        "evaluation_technique": "Methods Evaluation Measurement Technique",
        "control_method": "Methods Control Method",
        "spec_tolerance": "Methods Product/ Process Specification / Tolerance",
        "sample_size": "Methods Sample Size",
        "sample_freq": "Methods Sample Freq.",
        "special_character_class": "Special Char. Class",
        "equipment": "Machine, Device, Jig Tools for Mfg.",
        "reaction_plan": "Reaction Plan",
    }

    # Create a DataFrame containing only the desired columns
    extracted: Dict[str, Any] = {}
    for friendly, raw in col_map.items():
        if raw in df.columns:
            extracted[friendly] = df[raw]
        else:
            extracted[friendly] = pd.NA

    records_df = pd.DataFrame(extracted)

    # Forward‑fill hierarchical fields to handle merged cells
    for col in ["process_name", "product_characteristic", "process_characteristic"]:
        if col in records_df.columns:
            records_df[col] = records_df[col].ffill()

    # Filter out rows without a product characteristic (blank or containing only header text)
    mask = records_df["product_characteristic"].astype(str).str.strip() != ""
    records_df = records_df[mask]

    # Remove rows where the product characteristic is literally 'Product' or 'Process' (header remnants)
    records_df = records_df[
        ~records_df["product_characteristic"].astype(str).str.contains(r"^Product$|^Process$", case=False)
    ]

    # Fill NaN values in string columns with empty strings
    for col in records_df.columns:
        if records_df[col].dtype == object or pd.api.types.is_string_dtype(records_df[col]):
            records_df[col] = records_df[col].fillna("")

    data_records: List[Dict[str, Any]] = records_df.to_dict("records")
    return {"status": "success", "data": data_records}