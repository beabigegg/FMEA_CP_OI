#!/usr/bin/env python3
"""
Check what fields are actually being created by the current parser
"""

import sys
from pathlib import Path

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parsers.fmea_parser import parse

def check_current_fields():
    """Check current fields"""
    file_path = r"docs\W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    
    try:
        result = parse(file_path)
        
        if result.get('status') != 'success':
            print(f"ERROR: {result.get('message')}")
            return False
            
        data = result.get('data', [])
        print(f"SUCCESS: Parsed {len(data)} records")
        
        if data:
            first_record = data[0]
            print(f"\nActual fields created ({len(first_record)}):")
            print("-" * 60)
            
            for i, (field, value) in enumerate(first_record.items()):
                print(f"{i:2d}: {field:<50} = {repr(str(value)[:50]) if value is not None else 'None'}")
                
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_current_fields()