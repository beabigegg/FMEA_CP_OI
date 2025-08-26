from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import json

from src.database import models, database
from src.dify_client import client as dify_client
from src.database.config import settings

router = APIRouter(
    prefix="/ai",
    tags=["AI Suggestions"],
)

def format_item_for_prompt(item: models.Item) -> str:
    content = json.loads(item.content)
    # Standardize output for both FMEA and CP items
    if item.document.document_type == 'FMEA':
        return f"[FMEA Item ID: {item.id}] Failure Mode: {content.get('failure_mode', 'N/A')}, Cause: {content.get('failure_cause', 'N/A')}"
    elif item.document.document_type == 'CP':
        return f"[CP Item ID: {item.id}] Characteristic: {content.get('product_characteristic', 'N/A')}, Method: {content.get('control_method', 'N/A')}"
    return f"[Item ID: {item.id}] Content: {item.content}"

@router.post("/suggest-association/{fmea_item_id}")
def suggest_association(
    fmea_item_id: int,
    db: Session = Depends(database.get_db)
):
    """
    For a given FMEA item, suggests a suitable CP item for association.
    """
    try:
        # 1. Get the target FMEA item with its document info
        target_fmea_item = db.query(models.Item).options(joinedload(models.Item.document)).filter(models.Item.id == fmea_item_id).first()
        if not target_fmea_item or target_fmea_item.document.document_type != 'FMEA':
            raise HTTPException(status_code=404, detail="Target FMEA item not found.")

        # 2. Get existing associations as examples (with item and document info)
        examples = db.query(models.Association).options(
            joinedload(models.Association.fmea_item).joinedload(models.Item.document),
            joinedload(models.Association.cp_item).joinedload(models.Item.document)
        ).limit(10).all()
        
        example_text = "\n".join([
            f"- Example: {format_item_for_prompt(ex.fmea_item)} IS LINKED TO {format_item_for_prompt(ex.cp_item)}"
            for ex in examples
        ]) if examples else "No examples available."

        # 3. Get all CP items as candidates
        cp_items = db.query(models.Item).options(joinedload(models.Item.document)).join(models.Document).filter(models.Document.document_type == 'CP').all()
        if not cp_items:
            raise HTTPException(status_code=404, detail="No Control Plan items found in the database to use as candidates.")
        options_text = "\n".join([format_item_for_prompt(cp_item) for cp_item in cp_items])

        # 4. Construct the prompt
        prompt = f"""
        Based on the examples of existing links, find the best match for the target FMEA item from the list of available Control Plan (CP) items.

        ### EXAMPLES OF EXISTING LINKS:
        {example_text}

        ### AVAILABLE CP ITEMS (OPTIONS):
        {options_text}

        ### TARGET FMEA ITEM:
        {format_item_for_prompt(target_fmea_item)}

        Analyze the target and the options. Which CP Item ID from the list is the most suitable link? Respond with ONLY the numeric ID (e.g., 123) and nothing else.
        """
        
        # 5. Call DIFY AI
        if not settings.DIFY_API_KEY or not settings.DIFY_API_URL:
            raise HTTPException(status_code=500, detail="DIFY API is not configured on the server.")

        dify_response = dify_client.call_text_generation(prompt, settings.DIFY_API_KEY, settings.DIFY_API_URL)

        if dify_response['status'] != 'success':
            raise HTTPException(status_code=502, detail=f"AI service error: {dify_response['message']}")

        # 6. Parse the AI's response to get the suggested ID
        suggested_id_str = str(dify_response['ai_response']).strip()
        try:
            suggested_id = int(suggested_id_str)
            return {
                "message": "AI suggestion received successfully.",
                "target_fmea_item_id": fmea_item_id,
                "suggested_cp_item_id": suggested_id,
                "raw_ai_response": suggested_id_str,
                "prompt_sent_to_ai": prompt
            }
        except (ValueError, TypeError):
            return {
                "message": "AI returned a non-numeric response.",
                "target_fmea_item_id": fmea_item_id,
                "suggested_cp_item_id": None,
                "raw_ai_response": suggested_id_str,
                "prompt_sent_to_ai": prompt
            }

    except Exception as e:
        # Re-raise HTTPException to avoid being caught by the generic 500
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
