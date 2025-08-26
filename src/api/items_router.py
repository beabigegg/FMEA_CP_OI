"""
API routes for individual FMEA/CP items.

This router implements item update functionality and includes a fix for
returning timestamps in the Asia/Taipei timezone.  When an item is updated
the response will include the `updated_at` field converted from UTC to the
local timezone using `to_local`【695493780409242†L24-L25】.
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from sqlalchemy.orm import Session

from src.database import models, database
from src.utils.time_utils import to_local
from src import security

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)

@router.put("/{item_id}")
def update_item(
    item_id: int = Path(..., description="ID of the item to update"),
    updated_content: Dict[str, Any] = Body(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Updates the content of a specific item.  The provided `updated_content`
    should be a JSON‑serialisable object which will replace the existing
    content stored for the item.  The `edited_by` field is set to the
    provided user.  The updated timestamp is converted to Asia/Taipei in the
    response.【695493780409242†L24-L25】
    """
    try:
        item_to_update = db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item_to_update:
            raise HTTPException(status_code=404, detail="Item not found")

        # --- Start Change History Logging ---
        # Preserve old content before making changes
        old_content_json = item_to_update.content

        # Create a new history record
        new_history_record = models.ItemHistory(
            item_id=item_to_update.id,
            old_content=old_content_json,
            new_content=updated_content, # updated_content is already a dict
            change_type='UPDATE',
            changed_by=current_user.username
        )
        db.add(new_history_record)
        # --- End Change History Logging ---

        # Update the content and editor
        try:
            # The content in the DB must be a JSON string
            item_to_update.content = json.dumps(updated_content, ensure_ascii=False)
        except TypeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid updated_content format: {e}")
        item_to_update.edited_by = current_user.username

        db.commit()
        db.refresh(item_to_update)

        # Build response with localised timestamp
        response = {
            "message": f"Item {item_id} updated successfully",
            "updated_item": {
                "id": item_to_update.id,
                "content": updated_content,
                "edited_by": item_to_update.edited_by,
                "updated_at": to_local(item_to_update.updated_at)
            }
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{item_id}/history")
def get_item_history(
    item_id: int = Path(..., description="ID of the item to retrieve history for"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieves the change history for a specific item, ordered from newest to oldest.
    """
    history_records = (
        db.query(models.ItemHistory)
        .filter(models.ItemHistory.item_id == item_id)
        .order_by(models.ItemHistory.changed_at.desc())
        .all()
    )

    if not history_records:
        # It's not an error if an item has no history, just return an empty list.
        return []

    # Format the response, converting timestamps to local time
    return [
        {
            "id": record.id,
            "item_id": record.item_id,
            "old_content": record.old_content,
            "new_content": record.new_content,
            "change_type": record.change_type,
            "changed_by": record.changed_by,
            "changed_at": to_local(record.changed_at)
        }
        for record in history_records
    ]
