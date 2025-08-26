"""
Utility for parsing the Failure Effects (FE) list from an FMEA Excel file.

The AIAG‑VDA FMEA templates include a sheet called ``LIST`` which provides
qualitative descriptions of potential failure effects and an associated
severity score.  This parser extracts those pairs so they can be presented
to users as selectable options.  When a user picks an FE description, the
corresponding severity (S) value can be automatically populated and later
combined with occurrence (O) and detection (D) values to compute an Action
Priority (AP).

The sheet structure is loosely standardised: the first column (index 0)
contains the textual description of the failure effect and the last
column (index 7) contains a numeric severity rating.  The first row
provides headers (e.g. ``S`` and ``分數``); this row is skipped during
extraction.  Only rows with valid numeric severities are returned.

Example usage:

```python
from src.utils import fe_list_parser
fe_records = fe_list_parser.parse(io.BytesIO(excel_bytes))
for rec in fe_records['data']:
    print(rec['failure_effect'], rec['severity'])
```

"""

import pandas as pd

def parse(file_source):
    """
    Extracts the failure effect descriptions and severity values from the
    ``LIST`` sheet of an FMEA Excel file.

    Args:
        file_source (str or file‑like): Path to the Excel file or a stream
            containing the file data (e.g. ``io.BytesIO``).

    Returns:
        dict: A dictionary with keys ``status`` and ``data``.  On success
            ``status`` will be ``"success"`` and ``data`` will be a list of
            dictionaries with keys ``failure_effect`` and ``severity``.  If
            an error occurs, ``status`` will be ``"error"`` and ``message``
            will describe the problem.
    """
    sheet_name = 'LIST'
    try:
        # Load the sheet as a DataFrame.  We don't specify ``header`` so
        # pandas will treat the first row as column names.  This row
        # contains the Chinese headings ``S`` and ``分數`` among others.
        df = pd.read_excel(file_source, sheet_name=sheet_name)
        if df.empty:
            return {"status": "success", "data": []}

        # Drop the first row (index 0) which holds the header values.
        df = df.drop(0).reset_index(drop=True)

        # The first column contains the FE descriptions; the last column
        # (index 7) contains the severity values.  We select by position
        # rather than by name because the sheet uses unnamed columns.
        if df.shape[1] < 8:
            return {
                "status": "error",
                "message": f"Expected at least 8 columns in '{sheet_name}' sheet, found {df.shape[1]}"
            }
        fe_df = df.iloc[:, [0, 7]].copy()
        fe_df.columns = ['failure_effect', 'severity']

        # Convert severity to numeric values; drop rows without a valid number.
        fe_df['severity_numeric'] = pd.to_numeric(fe_df['severity'], errors='coerce')
        fe_df.dropna(subset=['severity_numeric'], inplace=True)

        # Build the list of records.  Severity is cast to int for clarity.
        records = []
        for _, row in fe_df.iterrows():
            records.append({
                'failure_effect': str(row['failure_effect']).strip(),
                'severity': int(row['severity_numeric'])
            })

        return {"status": "success", "data": records}
    except Exception as e:
        return {"status": "error", "message": str(e)}