from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import json
from typing import Dict, Any

from src.database import models, database

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)

@router.put("/{item_id}")
def update_item(
    item_id: int, 
    updated_content: Dict[str, Any] = Body(...),
    user: str = Body(...),
    db: Session = Depends(database.get_db)
):
    """
    Updates the content of a specific item.
    """
    try:
        item_to_update = db.query(models.Item).filter(models.Item.id == item_id).first()

        if not item_to_update:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update the content and the editor
        item_to_update.content = json.dumps(updated_content, ensure_ascii=False)
        item_to_update.edited_by = user

        db.commit()
        db.refresh(item_to_update)

        return {
            "message": f"Item {item_id} updated successfully",
            "updated_item": {
                "id": item_to_update.id,
                "content": json.loads(item_to_update.content),
                "edited_by": item_to_update.edited_by,
                "updated_at": item_to_update.updated_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
