import pandas as pd

def parse(file_source):
    """
    Performs targeted data extraction from the '00' sheet of the FMEA Excel file.
    Can accept either a file path (str) or a file-like object (e.g., io.BytesIO).

    Args:
        file_source (str or io.BytesIO): The path to the .xlsx file or the file content stream.

    Returns:
        dict: A dictionary containing a list of structured records.
    """
    target_sheet = '00'
    header_row = 9  # The actual header is on the 10th row
    cols_to_use = [4, 8, 12, 13, 14, 16]
    col_names = [
        'process_step',
        'process_function',
        'failure_mode',
        'failure_cause',
        'prevention_controls',
        'detection_controls'
    ]

    print(f"[FMEA Parser] Extracting data from sheet '{target_sheet}'...")
    try:
        df = pd.read_excel(
            file_source, 
            sheet_name=target_sheet, 
            header=header_row, 
            usecols=cols_to_use
        )
        df.columns = col_names

        df.dropna(subset=['failure_mode'], inplace=True)

        # Fill NaN values with empty strings for cleaner JSON
        df.fillna('', inplace=True)

        records = df.to_dict('records')
        print(f"[FMEA Parser] Successfully extracted {len(records)} records.")

        return {
            "status": "success",
            "data": records
        }
    except Exception as e:
        print(f"[FMEA Parser] Error extracting data: {e}")
        return {"status": "error", "message": str(e)}
