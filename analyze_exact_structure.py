#!/usr/bin/env python3
"""
Analyze exact Excel structure to fix field mapping errors
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parsers.fmea_parser import _flatten_columns

def analyze_exact_structure():
    """Analyze exact Excel structure"""
    file_path = r"docs\W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    
    print("ANALYZING EXACT EXCEL STRUCTURE FOR CORRECT MAPPING")
    print("=" * 80)
    
    try:
        # Read Excel with multi-header
        df = pd.read_excel(file_path, sheet_name='00', header=[8, 9])
        
        # Flatten columns
        flattened_cols = _flatten_columns(df.columns)
        
        print(f"Total columns: {len(flattened_cols)}")
        print(f"DataFrame shape: {df.shape}")
        
        print(f"\nEXACT COLUMN STRUCTURE WITH SAMPLE DATA:")
        print("=" * 80)
        
        # Get first few rows of actual data
        sample_rows = []
        for i in range(min(3, len(df))):
            row_data = []
            for j in range(len(flattened_cols)):
                if j < len(df.columns):
                    value = df.iloc[i, j]
                    if pd.notna(value) and str(value).strip():
                        row_data.append(str(value)[:50])
                    else:
                        row_data.append("")
            sample_rows.append(row_data)
        
        # Analyze each column with its actual data
        for i, col_name in enumerate(flattened_cols):
            print(f"\nColumn {i:2d}: {col_name}")
            print(f"    Sample values:")
            for row_idx, row_data in enumerate(sample_rows):
                if i < len(row_data) and row_data[i]:
                    print(f"      Row {row_idx}: {repr(row_data[i])}")
        
        print(f"\n" + "=" * 80)
        print("PROPOSING CORRECT FIELD MAPPING")
        print("=" * 80)
        
        # Based on your feedback, create the correct mapping
        correct_mapping = {
            # Column 0: Issue #
            "Issue #": "issue_no",
            
            # Column 1: History/Change Authorization  
            "Continuous improvement 持續改進 History/ Change Authorization (As Applicable) 過去的履歷/變更授權(當適用時)": "history_change_authorization",
            
            # Column 2: Process Item
            "STRUCTURE ANALYSIS (STEP 2) 結構分析 1. Process Item 過程項目 System, Subsystem, Part Element or Name of Process 系統、次(分/子)系統、零件要項或過程名稱": "process_item",
            
            # Column 3: Process Step  
            "STRUCTURE ANALYSIS (STEP 2) 結構分析 2. Process Step 過程步驟 Station No. and Name of Focus Element 工作站別與聚焦分析(關注)的要項名稱": "process_step",
            
            # Column 4: Process Work Element (4M Type)
            "STRUCTURE ANALYSIS (STEP 2) 結構分析 3. Process Work Element 過程工作要項 4M Type 四大管理要素 (Men, Machine, Material, Milieu (Environment), etc.) 人、機、料、法、環、測等)": "process_work_element",
            
            # Column 5: Function of the Process Item
            "FUNCTION ANALYSIS (STEP 3) 功能分析 1. Function of the Process Item過程項目的功能; Function of System, Subsystem, Part Element or Process 系統、次系統、零件要項或過程的功能": "function_of_process_item",
            
            # Column 6: Function of the Process Step and Product Characteristic  
            "FUNCTION ANALYSIS (STEP 3) 功能分析 2. Function of the Process Step and Product Characteristic 過程步驟的功能與產品特性描述 (Quantitative value is optional可選用計量值的特性)": "function_of_process_step_and_product_characteristic",
            
            # Column 7: Function of the Process Work Element and Process Characteristic
            "FUNCTION ANALYSIS (STEP 3) 功能分析 3. Function of the Process Work Element and Process Characteristic 過程工作要項功能與過程的特性": "function_of_process_work_element_and_process_characteristic",
            
            # Column 8: Failure Effects (FE) to the Next Higher Level Element
            "FAILURE ANALYSIS (STEP 4) 失效分析 1. Failure Effects (FE) to the Next Higher Level Element (Process Item) and/or End User 對上一個(緊鄰)較高層級(過程項目)與/或最終使用者的失效影響(效應)": "failure_effects",
            
            # Column 9: Severity (S) of FE - This is actually text description, not numeric
            "FAILURE ANALYSIS (STEP 4) 失效分析 Severity (S) of FE 失效效應的嚴重度": "severity_description_of_fe",
            
            # Column 10: This contains the numeric Severity value
            "FAILURE ANALYSIS (STEP 4) 失效分析 2. Failure Mode (FM) of the Focus Element (Process Step) 聚焦分析(關注)要項(或過程步驟)的(潛在)失效模式": "severity",
            
            # Column 11: Failure Cause
            "FAILURE ANALYSIS (STEP 4) 失效分析 3. Failure Cause (FC) of the Work Element / Failure Cause (FC) of the Next Lower Level Element or Characteristic 工作要項的失效原因 /次一個較低要項或特性的失效原因": "failure_cause",
            
            # Column 12: Current Prevention Controls
            "RISK ANALYSIS (STEP 5) 風險分析 Current Prevention Controls (PC) of FC 現行過程設計管制對失效原因的預防方法": "current_prevention_controls",
            
            # Column 13: This is text, not numeric occurrence
            "RISK ANALYSIS (STEP 5) 風險分析 Occurance (O) of FC 失效原因的發生度": "occurrence_description",
            
            # Column 14: This contains numeric Occurrence value
            "RISK ANALYSIS (STEP 5) 風險分析 Current Detection Controls (DC) of FC or FM 現行過程設計管制對失效原因或失效模式的偵測方法": "occurrence", 
            
            # Column 15: Current Detection Controls  
            "RISK ANALYSIS (STEP 5) 風險分析 Detection (D) of FC/ FM 失效原因/模式的難檢度": "current_detection_controls",
            
            # Column 16: This contains numeric Detection value
            "RISK ANALYSIS (STEP 5) 風險分析 PFMEA AP 採取措施優先性": "detection",
            
            # Column 17: Special Characteristics (currently getting Filter Code data)
            "RISK ANALYSIS (STEP 5) 風險分析 Special Characteristics 特殊特性": "special_characteristics",
            
            # Column 18: Filter Code (currently empty)
            "RISK ANALYSIS (STEP 5) 風險分析 Filter Code (Optional)": "filter_code",
        }
        
        print("Correct mapping should be:")
        for excel_col, db_field in correct_mapping.items():
            if excel_col in flattened_cols:
                col_idx = flattened_cols.index(excel_col)
                sample = df.iloc[0, col_idx] if col_idx < len(df.columns) else "N/A"
                print(f"{db_field:<40}: {excel_col[:60]}...")
                print(f"{'':40}  Sample: {repr(str(sample)[:50])}")
            else:
                print(f"{db_field:<40}: NOT FOUND - {excel_col[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_exact_structure()