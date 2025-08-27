"""
Debug script to analyze the exact Excel header structure
Row 9 (B9:AG9) - Main headers with merged cells
Row 10 (B10:AG10) - Sub headers without merged cells
"""

import pandas as pd
import sys
import os

# Add the project root to sys.path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_header_structure():
    """Analyze the exact header structure in the Excel file"""
    file_path = "docs/W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    sheet_name = "00"
    
    print("ANALYZING EXCEL HEADER STRUCTURE")
    print("=" * 60)
    
    try:
        # Read the Excel file to analyze header structure
        # First, read row 9 and 10 separately to understand the structure
        
        # Read row 9 (index 8) - Main headers
        df_row9 = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=8, nrows=1)
        
        # Read row 10 (index 9) - Sub headers  
        df_row10 = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=9, nrows=1)
        
        print("ROW 9 ANALYSIS (Main Headers - B9:AG9)")
        print("-" * 40)
        print(f"Total columns in row 9: {len(df_row9.columns)}")
        
        # Print each column from B (column 1) to AG (column 32)
        for i in range(len(df_row9.columns)):
            excel_col = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
            value = df_row9.iloc[0, i]
            if pd.notna(value) and str(value).strip():
                print(f"  {excel_col}{9}: '{value}'")
            else:
                print(f"  {excel_col}{9}: [EMPTY]")
        
        print("\nROW 10 ANALYSIS (Sub Headers - B10:AG10)")
        print("-" * 40)
        print(f"Total columns in row 10: {len(df_row10.columns)}")
        
        # Print each column from B (column 1) to AG (column 32)
        for i in range(len(df_row10.columns)):
            excel_col = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
            value = df_row10.iloc[0, i]
            if pd.notna(value) and str(value).strip():
                print(f"  {excel_col}{10}: '{value}'")
            else:
                print(f"  {excel_col}{10}: [EMPTY]")
        
        print("\nCOMBINED HEADER STRUCTURE ANALYSIS")
        print("-" * 40)
        
        # Now read with multi-level headers as the current parser does
        df_multi = pd.read_excel(file_path, sheet_name=sheet_name, header=[8, 9])
        print(f"Multi-level header columns count: {len(df_multi.columns)}")
        
        print("\nMulti-level column structure:")
        for i, col in enumerate(df_multi.columns):
            excel_col = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
            print(f"  Column {i} ({excel_col}): {col}")
        
        print("\nDATA ANALYSIS - First row of actual data")
        print("-" * 40)
        
        # Get first row of actual data to see what's in each column
        if len(df_multi) > 0:
            first_row = df_multi.iloc[0]
            for i, (col_name, value) in enumerate(first_row.items()):
                excel_col = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
                if pd.notna(value) and str(value).strip():
                    print(f"  {excel_col} ({col_name}): {str(value)[:50]}...")
                else:
                    print(f"  {excel_col} ({col_name}): [EMPTY]")
        
    except Exception as e:
        print(f"Error analyzing header structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_header_structure()