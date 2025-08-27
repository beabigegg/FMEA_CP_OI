#!/usr/bin/env python3
"""
Test the fixed FMEA parser with correct field mapping
"""

import sys
from pathlib import Path

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parsers.fmea_parser import parse

def test_fixed_parser():
    """Test the fixed parser"""
    file_path = r"docs\W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    
    print("TESTING FIXED FMEA PARSER")
    print("=" * 60)
    
    try:
        result = parse(file_path)
        
        if result.get('status') != 'success':
            print(f"ERROR: {result.get('message')}")
            return False
            
        data = result.get('data', [])
        print(f"SUCCESS: Parsed {len(data)} records")
        
        if data:
            first_record = data[0]
            print(f"\nFirst record structure:")
            print("-" * 60)
            
            # Check the key fields that were previously wrong
            key_fields_check = {
                'issue_no': 'Should be empty or have issue number',
                'process_item': 'Should be empty (not filled in this Excel)',
                'process_step': 'Should be "晶粒黏著共晶Eutectic DB 1610"',
                'process_work_element': 'Should be "上料before work"',
                'function_of_process_item': 'Should be "人Men"',
                'function_of_process_step_and_product_characteristic': 'Should be long process description',
                'function_of_process_work_element_and_process_characteristic': 'Should be "確認物料/工具已上機並設定製程參數準備作業"',
                'failure_effects': 'Should be "確認批號資訊"',
                'failure_effects_description': 'Should be "影響作業的效率但不影響產品良率與品質"',
                'failure_mode': 'Should be "錯置或使用錯誤Wrong Products"',
                'failure_cause': 'Should be "錯置或使用錯誤Wrong Products"',
                'severity': 'Should be 2 (numeric)',
                'prevention_controls': 'Should be prevention control description',
                'occurrence': 'Should be 3 (numeric)',
                'detection_controls': 'Should be detection control description',
                'detection': 'Should be 6 (numeric)',
                'special_characteristics': 'Should be "L"',
                'filter_code': 'Should be empty',
                'ap': 'Should be calculated from S/O/D'
            }
            
            for field, expected in key_fields_check.items():
                if field in first_record:
                    value = first_record[field]
                    print(f"{field:<50}: {repr(str(value)[:80]) if value is not None else 'None'}")
                    print(f"{'Expected':<50}: {expected}")
                    print()
                else:
                    print(f"{field:<50}: MISSING!")
                    print(f"{'Expected':<50}: {expected}")
                    print()
            
            print(f"\nCRITICAL VALUE VERIFICATION:")
            print("-" * 60)
            
            # Verify the critical S/O/D values
            s = first_record.get('severity')
            o = first_record.get('occurrence') 
            d = first_record.get('detection')
            ap = first_record.get('ap')
            
            print(f"Severity (S):   {s} (should be 2)")
            print(f"Occurrence (O): {o} (should be 3)")  
            print(f"Detection (D):  {d} (should be 6)")
            print(f"Action Priority: {ap}")
            
            # Verify data types
            severity_is_numeric = isinstance(s, (int, float)) or (isinstance(s, str) and s.isdigit())
            occurrence_is_numeric = isinstance(o, (int, float)) or (isinstance(o, str) and o.isdigit()) 
            detection_is_numeric = isinstance(d, (int, float)) or (isinstance(d, str) and d.isdigit())
            
            print(f"\nData type verification:")
            print(f"Severity is numeric:  {severity_is_numeric}")
            print(f"Occurrence is numeric: {occurrence_is_numeric}")
            print(f"Detection is numeric:  {detection_is_numeric}")
            
            if severity_is_numeric and occurrence_is_numeric and detection_is_numeric:
                print("SUCCESS: All S/O/D values are numeric!")
            else:
                print("ERROR: Some S/O/D values are not numeric!")
            
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_parser()