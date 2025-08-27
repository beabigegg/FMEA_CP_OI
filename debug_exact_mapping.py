"""
Debug script to create the exact correct mapping based on the analysis results
"""

import pandas as pd
import sys
import os

# Add the project root to sys.path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_exact_mapping():
    """Create the exact mapping based on the debug analysis"""
    file_path = "docs/W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    sheet_name = "00"
    
    print("CREATING EXACT MAPPING BASED ON DEBUG ANALYSIS")
    print("=" * 60)
    
    try:
        # Read with multi-level headers as the current parser does
        df_multi = pd.read_excel(file_path, sheet_name=sheet_name, header=[8, 9])
        
        print("First row of actual data with correct mapping:")
        print("-" * 50)
        
        if len(df_multi) > 0:
            first_row = df_multi.iloc[0]
            
            # Based on debug_header_structure.py output, create exact mapping:
            mapping_data = [
                # Column D(3): Process Item - contains "�����H�ۦ@��\nEutectic DB\n1610"
                ("process_item", 3, str(first_row.iloc[3])[:50] + "..."),
                
                # Column E(4): Process Step - contains "�W��\nbefore work"  
                ("process_step", 4, str(first_row.iloc[4])[:50] + "..."),
                
                # Column F(5): Process Work Element - contains "�H\nMen"
                ("process_work_element", 5, str(first_row.iloc[5])[:50] + "..."),
                
                # Column G(6): Function of Process Item - contains factory description
                ("function_of_process_item", 6, str(first_row.iloc[6])[:50] + "..."),
                
                # Column H(7): Function of Process Step & Product Characteristic
                ("function_of_process_step_and_product_characteristic", 7, str(first_row.iloc[7])[:50] + "..."),
                
                # Column I(8): Function of Work Element & Process Characteristic
                ("function_of_process_work_element_and_process_characteristic", 8, str(first_row.iloc[8])[:50] + "..."),
                
                # Column J(9): Failure Effects Description
                ("failure_effects_description", 9, str(first_row.iloc[9])[:50] + "..."),
                
                # Column K(10): Severity - contains "2"
                ("severity", 10, str(first_row.iloc[10])),
                
                # Column L(11): Failure Mode - contains "�Ͳ����~���~\nWrong Procucts"
                ("failure_mode", 11, str(first_row.iloc[11])[:50] + "..."),
                
                # Column M(12): Failure Cause - contains "���T�{�ѳ��T"
                ("failure_cause", 12, str(first_row.iloc[12])[:50] + "..."),
                
                # Column N(13): Prevention Controls Description
                ("prevention_controls_description", 13, str(first_row.iloc[13])[:50] + "..."),
                
                # Column O(14): Occurrence - contains "3"
                ("occurrence", 14, str(first_row.iloc[14])),
                
                # Column P(15): Detection Controls
                ("detection_controls", 15, str(first_row.iloc[15])[:50] + "..."),
                
                # Column Q(16): Detection - contains "6"
                ("detection", 16, str(first_row.iloc[16])),
                
                # Column R(17): PFMEA AP - contains "L"
                ("ap", 17, str(first_row.iloc[17])),
                
                # Column S(18): Special Characteristics - EMPTY
                ("special_characteristics", 18, "[EMPTY]"),
                
                # Column T(19): Filter Code - EMPTY 
                ("filter_code", 19, "[EMPTY]"),
            ]
            
            print("CORRECT FIELD MAPPING:")
            for field_name, col_index, sample_data in mapping_data:
                excel_col = chr(65 + col_index) if col_index < 26 else f"A{chr(65 + col_index - 26)}"
                print(f"  {field_name:<50} -> Column {excel_col}({col_index}): {sample_data}")
            
            print("\nNOW I UNDERSTAND THE CORRECT MAPPING!")
            print("The issue was that the fields were shifted by incorrect column interpretation.")
        
    except Exception as e:
        print(f"Error creating exact mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_exact_mapping()