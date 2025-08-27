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

def format_fmea_item_for_prompt(item: models.FmeaItem) -> str:
    return f"[FMEA Item ID: {item.id}] Failure Mode: {item.failure_mode}, Cause: {item.failure_cause}"

def format_cp_item_for_prompt(item: models.CpItem) -> str:
    return f"[CP Item ID: {item.id}] Characteristic: {item.product_characteristic}, Method: {item.control_method}"

@router.post("/suggest-association/{fmea_item_id}")
def suggest_association(
    fmea_item_id: int,
    db: Session = Depends(database.get_db)
):
    """
    For a given FMEA item, suggests the top 3 most suitable CP items for association.
    It excludes CP items that are already associated with the target FMEA item.
    """
    try:
        # 1. Get the target FMEA item with its document info
        target_fmea_item = db.query(models.FmeaItem).options(joinedload(models.FmeaItem.document)).filter(models.FmeaItem.id == fmea_item_id).first()
        if not target_fmea_item:
            raise HTTPException(status_code=404, detail="Target FMEA item not found.")

        # 2. Get IDs of CP items already associated with this FMEA item to exclude them
        associated_cp_ids = [
            assoc.cp_item_id for assoc in
            db.query(models.Association).filter(models.Association.fmea_item_id == fmea_item_id).all()
        ]

        # 3. Get existing associations as examples for the prompt (few-shot learning)
        examples = db.query(models.Association).options(
            joinedload(models.Association.fmea_item).joinedload(models.FmeaItem.document),
            joinedload(models.Association.cp_item).joinedload(models.CpItem.document)
        ).limit(5).all()
        
        example_text = "\n".join([
            f"- Example: {format_fmea_item_for_prompt(ex.fmea_item)} IS LINKED TO {format_cp_item_for_prompt(ex.cp_item)}"
            for ex in examples
        ]) if examples else "No examples available."

        # 4. Get all un-associated CP items as candidates
        candidates_query = db.query(models.CpItem).options(joinedload(models.CpItem.document))
        if associated_cp_ids:
            candidates_query = candidates_query.filter(models.CpItem.id.notin_(associated_cp_ids))
        cp_items = candidates_query.all()

        if not cp_items:
            return {"message": "No un-associated Control Plan items available to suggest.", "suggestions": []}
        options_text = "\n".join([format_cp_item_for_prompt(cp_item) for cp_item in cp_items])

        # 5. Construct the enhanced prompt
        prompt = f"""
        You are an expert assistant for quality control in manufacturing. Your task is to find the best matches for a target FMEA item from a list of available Control Plan (CP) items.

        ### EXAMPLES OF EXISTING LINKS:
        {example_text}

        ### AVAILABLE CP ITEMS (OPTIONS):
        {options_text}

        ### TARGET FMEA ITEM:
        {format_fmea_item_for_prompt(target_fmea_item)}

        Analyze the target FMEA item and the list of available CP items. Identify the top 3 most suitable CP Item IDs from the list. Respond with ONLY a comma-separated list of the 3 numeric IDs, ordered from the most relevant to the least relevant (e.g., 123, 456, 789).
        """
        
        # 6. Call DIFY AI
        if not settings.DIFY_API_KEY or not settings.DIFY_API_URL:
            raise HTTPException(status_code=500, detail="DIFY API is not configured on the server.")

        dify_response = dify_client.call_text_generation(prompt, settings.DIFY_API_KEY, settings.DIFY_API_URL)

        if dify_response['status'] != 'success':
            raise HTTPException(status_code=502, detail=f"AI service error: {dify_response['message']}")

        # 7. Parse the AI's response to get a list of suggested IDs
        suggested_ids_str = str(dify_response['ai_response']).strip()
        suggested_ids = []
        try:
            # Clean up potential non-numeric characters and split
            cleaned_str = ''.join(filter(lambda x: x.isdigit() or x == ',', suggested_ids_str))
            if cleaned_str:
                suggested_ids = [int(id_str.strip()) for id_str in cleaned_str.split(',') if id_str.strip()]
        except (ValueError, TypeError):
            # AI response was not in the expected format
            pass # Keep suggested_ids as an empty list

        return {
            "message": "AI suggestions received successfully.",
            "target_fmea_item_id": fmea_item_id,
            "suggestions": [
                {"suggested_cp_item_id": sid} for sid in suggested_ids
            ],
            "raw_ai_response": suggested_ids_str
        }

    except Exception as e:
        # Re-raise HTTPException to avoid being caught by the generic 500
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))