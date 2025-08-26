import requests
import json

def call_text_generation(prompt: str, api_key: str, base_api_url: str) -> dict:
    """
    Sends a generic prompt to a DIFY workflow endpoint.

    Args:
        prompt (str): The fully constructed prompt to send to the AI.
        api_key (str): The DIFY API key.
        base_api_url (str): The base URL of the DIFY API (e.g., 'https://dify.theaken.com/v1').

    Returns:
        dict: A dictionary containing the status and the AI's final response.
    """
    workflow_url = f"{base_api_url.rstrip('/')}/workflows/run"
    print(f"[DIFY Client] Sending prompt to DIFY workflow at: {workflow_url}")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'inputs': {
            "query": prompt 
        },
        'response_mode': 'blocking',
        'user': 'fmea-cp-analyzer'
    }

    try:
        response = requests.post(workflow_url, json=payload, headers=headers)
        response.raise_for_status()
        
        ai_response = response.json()
        print(f"[DIFY Client] Successfully received raw response from DIFY: {ai_response}")

        # [FIX] Extract the final text answer from the nested JSON structure
        # The path is data -> outputs -> text
        final_answer = ai_response.get('data', {}).get('outputs', {}).get('text')

        if final_answer is None:
            # If the expected structure is not found, return an error with the full response
            return {"status": "error", "message": f"Could not find 'text' in DIFY response outputs. Full response: {ai_response}"}

        return {"status": "success", "ai_response": final_answer}
    
    except requests.exceptions.RequestException as e:
        error_message = f"API call failed: {e}"
        if e.response is not None:
            error_message += f" | Response: {e.response.text}"
        print(f"[DIFY Client] Error: {error_message}")
        return {'status': 'error', 'message': error_message}
