"""
Enhanced parser for AIAG‑VDA Process FMEA workbooks.

This module exposes a single ``parse`` function which reads the
``00`` sheet from an FMEA Excel file and returns structured records.

Compared to the original implementation this version:

* Selects the correct columns for process step/function, failure mode,
  failure cause, prevention and detection controls, severity (S),
  occurrence (O), detection (D) and the action priority (AP).
* Performs forward‑fill on the process step and function columns to
  account for merged cells in the source workbook.
* Optionally computes an AP rating from S/O/D values when an AP is
  missing using a simplified AIAG‑VDA priority matrix.
* Returns a consistent list of dictionaries under the ``data`` key.

The function accepts either a string path to a ``.xlsx`` file or any
file‑like object that ``pandas.read_excel`` can consume (e.g. a
``BytesIO`` stream).  It does not extract the header metadata (rows
0–6) because those are intended to be supplied by the user at upload
time.
"""

from __future__ import annotations

import pandas as pd
from typing import Any, Dict, List, Union


def _classify_severity(value: int) -> str:
    """Map a numeric severity rating (1–10) into an AIAG‑VDA band."""
    if value == 1:
        return "1"
    if 2 <= value <= 3:
        return "2-3"
    if 4 <= value <= 6:
        return "4-6"
    if 7 <= value <= 8:
        return "7-8"
    return "9-10"


def _classify_occurrence(value: int) -> str:
    """Map an occurrence rating into an AIAG‑VDA band."""
    if value == 1:
        return "1"
    if 2 <= value <= 3:
        return "2-3"
    if 4 <= value <= 5:
        return "4-5"
    if 6 <= value <= 7:
        return "6-7"
    return "8-10"


def _classify_detection(value: int) -> str:
    """Map a detection rating into an AIAG‑VDA band."""
    if value == 1:
        return "1"
    if 2 <= value <= 4:
        return "2-4"
    if 5 <= value <= 6:
        return "5-6"
    return "7-10"

def _calculate_ap(severity: int, occurrence: int, detection: int) -> str:
    """Compute the AIAG‑VDA Action Priority (AP) from S/O/D bands.

    The mapping implemented here is intentionally simplified.  See the
    official FMEA manual for the full 1000‑cell table.  The logic
    prioritises high severity combined with high occurrence and poor
    detection as high priority; medium severity with moderate occurrence
    and poor detection as high; otherwise falls back to medium or low.
    """
    s_band = _classify_severity(severity)
    o_band = _classify_occurrence(occurrence)
    d_band = _classify_detection(detection)

    # Top‑level table derived from AIAG‑VDA guidance
    table = {
        "9-10": {
            "8-10": {"7-10": "H", "5-6": "H", "2-4": "H", "1": "H"},
            "6-7": {"7-10": "H", "5-6": "H", "2-4": "H", "1": "H"},
            "4-5": {"7-10": "H", "5-6": "H", "2-4": "H", "1": "M"},
            "2-3": {"7-10": "H", "5-6": "M", "2-4": "L", "1": "L"},
            "1": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
        },
        "7-8": {
            "8-10": {"7-10": "H", "5-6": "H", "2-4": "H", "1": "H"},
            "6-7": {"7-10": "H", "5-6": "H", "2-4": "H", "1": "M"},
            "4-5": {"7-10": "H", "5-6": "M", "2-4": "M", "1": "M"},
            "2-3": {"7-10": "M", "5-6": "M", "2-4": "L", "1": "L"},
            "1": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
        },
        "4-6": {
            "8-10": {"7-10": "H", "5-6": "H", "2-4": "M", "1": "M"},
            "6-7": {"7-10": "M", "5-6": "M", "2-4": "M", "1": "L"},
            "4-5": {"7-10": "M", "5-6": "L", "2-4": "L", "1": "L"},
            "2-3": {"7-10": "L", "5-6": "L", "2-4": "L", "1": "L"},
            "1": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
        },
        "2-3": {
            "8-10": {"7-10": "M", "5-6": "M", "2-4": "L", "1": "L"},
            "6-7": {"7-10": "L", "5-6": "L", "2-4": "L", "1": "L"},
            "4-5": {"7-10": "L", "5-6": "L", "2-4": "L", "1": "L"},
            "2-3": {"7-10": "L", "5-6": "L", "2-4": "L", "1": "L"},
            "1": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
        },
        "1": {
            "1": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
            "2-3": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
            "4-5": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
            "6-7": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
            "8-10": {"1": "L", "2-4": "L", "5-6": "L", "7-10": "L"},
        },
    }
    ap = table.get(s_band, {}).get(o_band, {}).get(d_band)
    if ap is None:
        # Fallback if combination is not explicitly listed
        ap = "L"
    return ap

def parse(file_source: Union[str, Any]) -> Dict[str, Any]:
    """Parse an FMEA Excel file and extract structured records.

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
        of dictionaries representing each row of the FMEA table.  On
        failure ``status`` will be ``"error"`` and ``message`` will
        describe the problem.
    """
    target_sheet = "00"
    header_row = 9  # Row 10 in Excel (0-indexed)
    # Map of friendly column names to the exact header strings found in row 9
    column_map = {
        "process_step": "2. Process Step 過程步驟  Station No. and Name of Focus Element 工作站別與聚焦分析(關注)的要項名稱",
        "process_function": "2. Function of the Process Step and Product Characteristic 過程步驟的功能與產品特性描述 (Quantitative value is optional可選用計量值的特性) ",
        "failure_mode": "2. Failure Mode (FM) of the Focus Element (Process Step) 聚焦分析(關注)要項(或過程步驟)的(潛在)失效模式",
        "failure_cause": "3. Failure Cause (FC) of the Work Element / Failure Cause (FC) of the Next Lower Level Element or Characteristic 工作要項的失效原因 /次一個較低要項或特性的失效原因",
        "prevention_controls": "Current Prevention Controls (PC) of FC  \n現行過程設計管制對失效原因的預防方法",
        "detection_controls": "Current Detection Controls (DC) of FC or FM \n現行過程設計管制對失效原因或失效模式的偵測方法",
        "severity": "Severity (S) of FE \n失效效應的嚴重度",
        "occurrence": "Occurance (O) of FC\n失效原因的發生度",
        "detection": "Detection (D) of FC/ FM\n失效原因/模式的難檢度",
        "ap": "PFMEA AP \n採取措施優先性",
    }

    try:
        # Read the sheet with pandas
        df = pd.read_excel(
            file_source,
            sheet_name=target_sheet,
            header=header_row,
        )
    except Exception as exc:
        return {"status": "error", "message": f"Failed to read Excel: {exc}"}

    # Ensure all expected columns exist; if not present set them to None
    extracted: Dict[str, Any] = {}
    for friendly, raw in column_map.items():
        if raw in df.columns:
            extracted[friendly] = df[raw]
        else:
            extracted[friendly] = pd.NA

    # Create DataFrame and forward‑fill process step/function
    records_df = pd.DataFrame(extracted)
    if "process_step" in records_df.columns:
        records_df["process_step"] = records_df["process_step"].ffill()
    if "process_function" in records_df.columns:
        records_df["process_function"] = records_df["process_function"].ffill()

    # Filter out rows without a failure mode
    valid_mask = records_df["failure_mode"].notna() & (records_df["failure_mode"].astype(str).str.strip() != "")
    records_df = records_df[valid_mask]

    # Fill NaN with empty strings for string fields
    for col in [
        "process_step",
        "process_function",
        "failure_mode",
        "failure_cause",
        "prevention_controls",
        "detection_controls",
    ]:
        if col in records_df.columns:
            records_df[col] = records_df[col].fillna("")

    # Compute AP if missing and severity/occurrence/detection are numeric
    ap_values: List[str] = []
    for s, o, d, existing_ap in zip(
        records_df["severity"],
        records_df["occurrence"],
        records_df["detection"],
        records_df["ap"],
    ):
        if pd.isna(existing_ap) or str(existing_ap).strip() == "":
            # Only compute if all three ratings are present and numeric
            if not pd.isna(s) and not pd.isna(o) and not pd.isna(d):
                try:
                    ap_values.append(_calculate_ap(int(s), int(o), int(d)))
                except Exception:
                    ap_values.append("")
            else:
                ap_values.append("")
        else:
            ap_values.append(str(existing_ap))
    records_df["ap"] = ap_values

    # Coerce numeric columns to integers where possible
    for col in ["severity", "occurrence", "detection"]:
        if col in records_df.columns:
            records_df[col] = pd.to_numeric(records_df[col], errors="coerce").astype("Int64")

    # Convert to list of dictionaries
    data_records: List[Dict[str, Any]] = records_df.to_dict("records")
    return {"status": "success", "data": data_records}