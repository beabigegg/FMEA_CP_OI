#!/usr/bin/env python3
"""
Debug column assignment to see what data is actually in each column
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parsers.fmea_parser import _flatten_columns

def debug_column_assignment():
    """Debug column assignment"""
    file_path = r"docs\W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    
    print("DEBUGGING COLUMN ASSIGNMENT")
    print("=" * 60)
    
    try:
        # Read Excel with multi-header
        df = pd.read_excel(file_path, sheet_name='00', header=[8, 9])
        
        # Flatten columns
        flattened_cols = _flatten_columns(df.columns)
        
        # Show the actual data in each column for first row
        print(f"Checking data in first 20 columns:")
        print("-" * 60)
        
        for i in range(min(20, len(df.columns))):
            col_name = flattened_cols[i] if i < len(flattened_cols) else f"Column_{i}"
            value = df.iloc[0, i] if i < len(df.columns) else "N/A"
            
            print(f"Column {i:2d}: {col_name}")
            print(f"    Value: {repr(str(value)[:100]) if pd.notna(value) else 'NaN/None'}")
            print()
            
        # Based on your requirements, these should be the correct assignments:
        correct_assignments = {
            0: ("issue_no", "Should be empty or issue number"),
            1: ("history_change_authorization", "Should be empty or change auth"),
            2: ("process_item", "Should be empty (not filled in this Excel)"),
            3: ("process_step", "Should have 'Eutectic DB 1610'"),
            4: ("process_work_element", "Should have '上料before work'"),
            5: ("function_of_process_item", "Should have '人Men'"),
            6: ("function_of_process_step_and_product_characteristic", "Should have long process description"),
            7: ("function_of_process_work_element_and_process_characteristic", "Should have confirm material/tool description"),
            8: ("failure_effects", "Should have failure effects description"),
            9: ("failure_effects_description", "Should have severity description text"),
            10: ("severity", "Should have numeric 2"),
            11: ("failure_cause", "Should have 'Wrong Products'"),
            12: ("prevention_controls", "Should have prevention controls description"),
            13: ("prevention_controls_description", "Should have occurrence description text"),
            14: ("occurrence", "Should have numeric 3"),
            15: ("detection_controls", "Should have detection controls description"), 
            16: ("detection", "Should have numeric 6"),
            17: ("special_characteristics", "Should have 'L'"),
            18: ("filter_code", "Should be empty")
        }
        
        print(f"PROPOSED CORRECT ASSIGNMENTS:")
        print("-" * 60)
        
        for col_idx, (field_name, expected) in correct_assignments.items():
            if col_idx < len(df.columns):
                actual_value = df.iloc[0, col_idx]
                print(f"Column {col_idx:2d} -> {field_name}")
                print(f"    Expected: {expected}")
                print(f"    Actual: {repr(str(actual_value)[:80]) if pd.notna(actual_value) else 'NaN/None'}")
                print()
            else:
                print(f"Column {col_idx:2d} -> {field_name} (MISSING - beyond available columns)")
                print()
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_column_assignment()