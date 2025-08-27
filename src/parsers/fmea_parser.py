"""
Enhanced parser for AIAG‑VDA Process FMEA workbooks.

This module exposes a single ``parse`` function which reads the
``00`` sheet from an FMEA Excel file and returns structured records.

This version handles multi-level headers and extracts all columns from the
FMEA file.
"""

from __future__ import annotations

import re
import pandas as pd
from typing import Any, Dict, List, Union
from src.utils.ap_logic import calculate_ap
import logging

logger = logging.getLogger(__name__)

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
    return [part for part in flattened if part]

def _calculate_ap(severity: int, occurrence: int, detection: int) -> str:
    """Compute the AIAG‑VDA Action Priority (AP) from S/O/D bands.

    The mapping implemented here is intentionally simplified.  See the
    official FMEA manual for the full 1000‑cell table.  The logic
    prioritises high severity combined with high occurrence and poor
    detection as high priority; medium severity with moderate occurrence
    and poor detection as high; otherwise falls back to medium or low.
    """
    # This function is not used in the new parser, but is kept for reference
    pass

def parse(file_source: Union[str, Any]) -> Dict[str, Any]:
    """
    Parse an FMEA Excel file and extract structured records.

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
    header_rows = [8, 9]  # Rows 9 and 10 in Excel (0-indexed)
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

    # Ensure the number of flattened columns matches the DataFrame columns
    if len(flattened_cols) != len(df.columns):
        logger.warning(f"Column count mismatch: flattened_cols={len(flattened_cols)}, df.columns={len(df.columns)}")
        # This handles cases where there are unnamed columns that are not filtered out
        # by _flatten_columns, but are still present in the DataFrame.
        if len(flattened_cols) < len(df.columns):
            # Append placeholder names for missing column names
            flattened_cols.extend([f"Unnamed_Column_{i}" for i in range(len(df.columns) - len(flattened_cols))])
            logger.info(f"Added {len(df.columns) - len(flattened_cols)} unnamed columns")
        else:
            # Trim flattened_cols to match df.columns length
            flattened_cols = flattened_cols[:len(df.columns)]
            logger.info(f"Trimmed flattened_cols to match df.columns length")

    df.columns = flattened_cols

    # Filter out columns that are not in the FmeaItem model
    # This list should match the columns defined in models.py for FmeaItem
    # CORRECTED MAPPING: Use cleaned column names that preserve Excel structure 
    # This approach maintains the original Excel column names while making them database-friendly
    def clean_column_name(col_name):
        """Clean column name to be database-friendly while preserving meaning"""
        return col_name.replace('/', '_').replace('(', '_').replace(')', '_').replace(' ', '_').replace('__', '_').strip('_')
    
    # Don't rename columns - keep original Excel column names
    # The database and frontend will use the cleaned versions
    column_mapping = {}
    
    # Instead, we'll create the cleaned names dynamically
    cleaned_columns = []
    for col in flattened_cols:
        if col.strip():  # Skip empty column names
            cleaned_name = clean_column_name(col)
            cleaned_columns.append(cleaned_name)
            column_mapping[col] = cleaned_name
        else:
            cleaned_columns.append(f"Unknown_Column_{len(cleaned_columns)}")
    
    # However, we need to fix the critical data mapping issues you identified:
    # The Excel has wrong data in some columns due to structure issues
    
    # Create a special mapping to fix the data placement issues
    data_fix_mapping = {}

    # Apply column name cleaning
    df.columns = [clean_column_name(col) if col.strip() else f"Unknown_Column_{i}" for i, col in enumerate(flattened_cols)]
    
    # Now we need to fix the data placement issues you identified
    # Based on the analysis, we need to create new columns with correct data
    
    # Extract the correct field mappings based on actual Excel column positions
    # Based on debug analysis: data starts from Column D (index 3) onwards
    # A(0)=empty, B(1)=Issue#(empty), C(2)=History(empty), D(3)=first data column
    
    correct_field_data = {}
    
    # Columns A, B, C are mostly empty or contain Issue#/History fields
    if len(df.columns) > 1:
        correct_field_data['issue_no'] = df.iloc[:, 1] if 1 < len(df.columns) else None  # Column B(1): Issue #
    if len(df.columns) > 2:
        correct_field_data['history_change_authorization'] = df.iloc[:, 2] if 2 < len(df.columns) else None  # Column C(2): History/Change Auth
    
    # Actual data columns start from Column D (index 3)
    if len(df.columns) > 3:
        correct_field_data['process_item'] = df.iloc[:, 3] if 3 < len(df.columns) else None  # Column D(3): Process Item
    if len(df.columns) > 4:
        correct_field_data['process_step'] = df.iloc[:, 4] if 4 < len(df.columns) else None  # Column E(4): Process Step  
    if len(df.columns) > 5:
        correct_field_data['process_work_element'] = df.iloc[:, 5] if 5 < len(df.columns) else None  # Column F(5): Process Work Element
    if len(df.columns) > 6:
        correct_field_data['function_of_process_item'] = df.iloc[:, 6] if 6 < len(df.columns) else None  # Column G(6): Function of Process Item
    if len(df.columns) > 7:
        correct_field_data['function_of_process_step_and_product_characteristic'] = df.iloc[:, 7] if 7 < len(df.columns) else None  # Column H(7): Function of Process Step & Product Characteristic
    if len(df.columns) > 8:
        correct_field_data['function_of_process_work_element_and_process_characteristic'] = df.iloc[:, 8] if 8 < len(df.columns) else None  # Column I(8): Function of Work Element & Process Characteristic
    if len(df.columns) > 9:
        correct_field_data['failure_effects_description'] = df.iloc[:, 9] if 9 < len(df.columns) else None  # Column J(9): Failure Effects (FE) to Next Higher Level
    if len(df.columns) > 10:
        correct_field_data['severity'] = df.iloc[:, 10] if 10 < len(df.columns) else None  # Column K(10): Severity (S) of FE
    if len(df.columns) > 11:
        correct_field_data['failure_mode'] = df.iloc[:, 11] if 11 < len(df.columns) else None  # Column L(11): Failure Mode (FM)
    if len(df.columns) > 12:
        correct_field_data['failure_cause'] = df.iloc[:, 12] if 12 < len(df.columns) else None  # Column M(12): Failure Cause (FC)
    if len(df.columns) > 13:
        correct_field_data['prevention_controls_description'] = df.iloc[:, 13] if 13 < len(df.columns) else None  # Column N(13): Current Prevention Controls (PC)
    if len(df.columns) > 14:
        correct_field_data['occurrence'] = df.iloc[:, 14] if 14 < len(df.columns) else None  # Column O(14): Occurrence (O) of FC
    if len(df.columns) > 15:
        correct_field_data['detection_controls'] = df.iloc[:, 15] if 15 < len(df.columns) else None  # Column P(15): Current Detection Controls (DC)
    if len(df.columns) > 16:
        correct_field_data['detection'] = df.iloc[:, 16] if 16 < len(df.columns) else None  # Column Q(16): Detection (D) of FC/FM
    if len(df.columns) > 17:
        correct_field_data['ap'] = df.iloc[:, 17] if 17 < len(df.columns) else None  # Column R(17): PFMEA AP
    if len(df.columns) > 18:
        correct_field_data['special_characteristics'] = df.iloc[:, 18] if 18 < len(df.columns) else None  # Column S(18): Special Characteristics
    if len(df.columns) > 19:
        correct_field_data['filter_code'] = df.iloc[:, 19] if 19 < len(df.columns) else None  # Column T(19): Filter Code
    
    # Add the remaining optimization fields (STEP 6)
    if len(df.columns) > 20:
        correct_field_data['prevention_action'] = df.iloc[:, 20] if 20 < len(df.columns) else None  # Column U(20): Prevention Action
    if len(df.columns) > 21:
        correct_field_data['detection_action'] = df.iloc[:, 21] if 21 < len(df.columns) else None  # Column V(21): Detection Action
    if len(df.columns) > 22:
        correct_field_data['responsible_person_name'] = df.iloc[:, 22] if 22 < len(df.columns) else None  # Column W(22): Responsible Person's Name
    if len(df.columns) > 23:
        correct_field_data['target_completion_date'] = df.iloc[:, 23] if 23 < len(df.columns) else None  # Column X(23): Target Completion Date
    if len(df.columns) > 24:
        correct_field_data['status'] = df.iloc[:, 24] if 24 < len(df.columns) else None  # Column Y(24): Status
    if len(df.columns) > 25:
        correct_field_data['action_taken'] = df.iloc[:, 25] if 25 < len(df.columns) else None  # Column Z(25): Action Taken
    if len(df.columns) > 26:
        correct_field_data['completion_date'] = df.iloc[:, 26] if 26 < len(df.columns) else None  # Column AA(26): Completion Date
    if len(df.columns) > 27:
        correct_field_data['severity_opt'] = df.iloc[:, 27] if 27 < len(df.columns) else None  # Column AB(27): Severity (S) Opt
    if len(df.columns) > 28:
        correct_field_data['occurrence_opt'] = df.iloc[:, 28] if 28 < len(df.columns) else None  # Column AC(28): Occurrence (O) Opt
    if len(df.columns) > 29:
        correct_field_data['detection_opt'] = df.iloc[:, 29] if 29 < len(df.columns) else None  # Column AD(29): Detection (D) Opt
    if len(df.columns) > 30:
        correct_field_data['ap_opt'] = df.iloc[:, 30] if 30 < len(df.columns) else None  # Column AE(30): PFMEA AP Opt
    if len(df.columns) > 31:
        correct_field_data['special_characteristics_opt'] = df.iloc[:, 31] if 31 < len(df.columns) else None  # Column AF(31): Special Characteristics Opt
    if len(df.columns) > 32:
        correct_field_data['remarks'] = df.iloc[:, 32] if 32 < len(df.columns) else None  # Column AG(32): Remarks
    
    # Note: Removed unused fields: process_function, function_of_process_work_element, 
    # failure_effects, prevention_controls - these are no longer needed
    
    # Create a new DataFrame with the correctly mapped data
    records_df = pd.DataFrame(correct_field_data)
    
    # Debug: Log what we have
    logger.info(f"Created DataFrame with {len(records_df.columns)} columns: {list(records_df.columns)}")

    # Filter out columns that are not in the FmeaItem model
    # This list should match the columns defined in models.py for FmeaItem
    valid_fmea_item_columns = [
        "process_step",
        "failure_mode",
        "failure_cause",
        "detection_controls",
        "severity",
        "occurrence",
        "detection",
        "ap",
        "issue_no",
        "history_change_authorization",
        "process_item",
        "process_work_element",
        "function_of_process_item",
        "function_of_process_step_and_product_characteristic",
        "function_of_process_work_element_and_process_characteristic",
        "failure_effects_description",
        "prevention_controls_description",
        "special_characteristics",
        "filter_code",
        "prevention_action",
        "detection_action",
        "responsible_person_name",
        "target_completion_date",
        "status",
        "action_taken",
        "completion_date",
        "severity_opt",
        "occurrence_opt",
        "detection_opt",
        "ap_opt",
        "remarks",
        "special_characteristics_opt",
    ]

    # All columns are now correctly mapped, no need to filter
    logger.info(f"Correctly mapped columns: {list(records_df.columns)}")
    
    # Ensure all expected columns exist, fill missing ones with None
    for col in valid_fmea_item_columns:
        if col not in records_df.columns:
            records_df[col] = None
            logger.info(f"Added missing column: {col}")
    
    # Reorder columns to match the expected order
    records_df = records_df.reindex(columns=valid_fmea_item_columns, fill_value=None)

    # Forward‑fill hierarchical fields to handle merged cells
    for col in records_df.columns:
        try:
            if records_df[col].dtype == object or pd.api.types.is_string_dtype(records_df[col]):
                records_df[col] = records_df[col].ffill()
        except Exception as e:
            logger.warning(f"Error forward-filling column {col}: {e}")

    # Since failure_mode is missing from this Excel format, we'll use failure_cause as the basis for filtering
    # Filter out rows without meaningful data (using failure_cause as the primary filter)
    if 'failure_cause' in records_df.columns:
        mask = records_df['failure_cause'].astype(str).str.strip() != ""
        mask = mask & (records_df['failure_cause'].notna())
        records_df = records_df[mask]
    
    # For this Excel format, we'll set failure_mode to be the same as failure_cause
    # since they appear to be combined in this particular FMEA format
    if 'failure_cause' in records_df.columns and 'failure_mode' not in records_df.columns:
        records_df['failure_mode'] = records_df['failure_cause']

    # Fill NaN values in string columns with empty strings
    for col in records_df.columns:
        try:
            if records_df[col].dtype == object or pd.api.types.is_string_dtype(records_df[col]):
                records_df[col] = records_df[col].fillna("")
        except Exception as e:
            logger.warning(f"Error filling NaN values in column {col}: {e}")

    # Calculate AP based on S, O, D values before returning data
    for index, row in records_df.iterrows():
        try:
            # Convert to int if possible, handling various input formats
            s = int(float(str(row['severity']).strip())) if pd.notna(row['severity']) and str(row['severity']).strip() != '' else None
            o = int(float(str(row['occurrence']).strip())) if pd.notna(row['occurrence']) and str(row['occurrence']).strip() != '' else None
            d = int(float(str(row['detection']).strip())) if pd.notna(row['detection']) and str(row['detection']).strip() != '' else None
            
            if s is not None and o is not None and d is not None:
                records_df.loc[index, 'ap'] = calculate_ap(s, o, d)
            else:
                records_df.loc[index, 'ap'] = None
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to calculate AP for row {index}: severity={row['severity']}, occurrence={row['occurrence']}, detection={row['detection']}, error={e}")
            records_df.loc[index, 'ap'] = None

        try:
            s_opt = int(float(str(row['severity_opt']).strip())) if pd.notna(row['severity_opt']) and str(row['severity_opt']).strip() != '' else None
            o_opt = int(float(str(row['occurrence_opt']).strip())) if pd.notna(row['occurrence_opt']) and str(row['occurrence_opt']).strip() != '' else None
            d_opt = int(float(str(row['detection_opt']).strip())) if pd.notna(row['detection_opt']) and str(row['detection_opt']).strip() != '' else None
            
            if s_opt is not None and o_opt is not None and d_opt is not None:
                records_df.loc[index, 'ap_opt'] = calculate_ap(s_opt, o_opt, d_opt)
            else:
                records_df.loc[index, 'ap_opt'] = None
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to calculate AP_opt for row {index}: severity_opt={row.get('severity_opt')}, occurrence_opt={row.get('occurrence_opt')}, detection_opt={row.get('detection_opt')}, error={e}")
            records_df.loc[index, 'ap_opt'] = None

    # Replace NaN with None for database compatibility, especially for non-string columns
    # Convert all NaN to None, forcing object type to prevent pandas from converting None back to NaN
    records_df = records_df.astype(object).where(pd.notna(records_df), None)

    logger.info(f"Columns in records_df before to_dict: {records_df.columns.tolist()}")
    data_records: List[Dict[str, Any]] = records_df.to_dict("records")
    return {"status": "success", "data": data_records}