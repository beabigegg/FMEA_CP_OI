import os
from dotenv import load_dotenv

from src.parsers import fmea_parser, cp_parser
from src.dify_client import client as dify_client
from src.analyzer import comparator

def main():
    """
    Main function to orchestrate the FMEA, CP, and OI document analysis.
    """
    # 1. Load configuration from .env file
    load_dotenv()
    dify_api_key = os.getenv("DIFY_API_KEY")
    dify_api_url = os.getenv("DIFY_API_URL")

    if not dify_api_key or not dify_api_url:
        print("FATAL ERROR: DIFY_API_KEY and DIFY_API_URL must be set in the .env file.")
        print("Please create a .env file in the root directory with your DIFY credentials.")
        return

    print("Configuration loaded successfully.")

    # 2. Define file paths
    fmea_file_path = "docs/W-PE2169-01 潛在失效模式及後果分析AIAG-VDA Process FMEA (晶粒黏著共晶Eutectic DB 1610).xlsx"
    cp_file_path = "docs/W-PE0229-04 製程品質計劃Control Plan (晶粒黏著共晶 Eutectic DB 1610).xlsx"

    print(f"\nTarget FMEA: {fmea_file_path}")
    print(f"Target Control Plan: {cp_file_path}")

    # 3. Parse documents
    print("\n--- Step 1: Parsing Documents ---")
    parsed_fmea = fmea_parser.parse(fmea_file_path)
    parsed_cp = cp_parser.parse(cp_file_path)

    # 4. Send data to DIFY for structuring
    print("\n--- Step 2: Structuring with DIFY AI ---")
    dify_fmea_response = dify_client.structure_data(parsed_fmea, "fmea", dify_api_key, dify_api_url)
    dify_cp_response = dify_client.structure_data(parsed_cp, "cp", dify_api_key, dify_api_url)

    # 5. Compare/Present structured data
    print("\n--- Step 3: Generating AI Analysis Report ---")
    report = comparator.compare(dify_fmea_response, dify_cp_response)

    # 6. Output report
    print("\n--- Step 4: Final Report ---")
    print(report)

if __name__ == "__main__":
    main()
