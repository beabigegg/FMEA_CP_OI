import pandas as pd

def parse(file_source):
    """
    Performs targeted data extraction from the 'REV.04' sheet of the CP Excel file.
    Can accept either a file path (str) or a file-like object (e.g., io.BytesIO).

    Args:
        file_source (str or io.BytesIO): The path to the .xlsx file or the file content stream.

    Returns:
        dict: A dictionary containing a list of structured records.
    """
    target_sheet = 'REV.04'
    header_row = 6  # The main header starts on the 7th row

    print(f"[CP Parser] Extracting data from sheet '{target_sheet}'...")
    try:
        df = pd.read_excel(
            file_source, 
            sheet_name=target_sheet, 
            header=header_row
        )
        
        process_name_col = df.columns[2]
        product_char_col = df.columns[4]
        eval_tech_col = df.columns[8]
        control_method_col = df.columns[11]

        df_selected = df[[process_name_col, product_char_col, eval_tech_col, control_method_col]].copy()
        df_selected.columns = [
            'process_name',
            'product_characteristic',
            'evaluation_technique',
            'control_method'
        ]

        df_selected.dropna(subset=['product_characteristic'], inplace=True)
        df_selected = df_selected[~df_selected['product_characteristic'].str.contains('Product', na=False)]

        df_selected['process_name'] = df_selected['process_name'].ffill()

        # Fill NaN values with empty strings for cleaner JSON
        df_selected.fillna('', inplace=True)

        records = df_selected.to_dict('records')
        print(f"[CP Parser] Successfully extracted {len(records)} records.")

        return {
            "status": "success",
            "data": records
        }
    except Exception as e:
        print(f"[CP Parser] Error extracting data: {e}")
        return {"status": "error", "message": str(e)}
