import json

def compare(dify_fmea_response, dify_cp_response):
    """
    Formats and presents the responses from the DIFY AI.

    In a future step, this function will contain the logic to cross-reference
    the structured data from both responses.

    Args:
        dify_fmea_response (dict): The full response object from the DIFY client for FMEA.
        dify_cp_response (dict): The full response object from the DIFY client for CP.

    Returns:
        str: A formatted string report of the AI's analysis.
    """
    print("[Analyzer] Formatting AI responses...")

    report = """
    ==================================
    DIFY AI Analysis Report
    ==================================

    --- FMEA Analysis Summary ---
    {}

    --- Control Plan Analysis Summary ---
    {}
    """

    # Helper to safely extract and format AI output
    def format_response(response):
        if response.get('status') != 'success':
            return f"AI analysis failed: {response.get('message', 'Unknown error')}"
        
        ai_response_data = response.get('ai_response')
        if not ai_response_data:
            return "No AI response data found."

        # DIFY's output is often in a specific key. Common ones are 'answer' or inside 'outputs'.
        # We will try to find it, assuming the output is a string.
        # This might need adjustment based on your specific DIFY workflow output.
        output_text = ai_response_data.get('answer', json.dumps(ai_response_data, indent=2, ensure_ascii=False))
        return output_text

    fmea_summary = format_response(dify_fmea_response)
    cp_summary = format_response(dify_cp_response)

    return report.format(fmea_summary, cp_summary)
