from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from src.database import models, database
from src import security

router = APIRouter(
    prefix="/associations",
    tags=["Associations"],
)

# --- Pydantic Schemas ---
class AssociationCreate(BaseModel):
    fmea_item_id: int
    cp_item_ids: List[int]

# --- API Endpoints ---
@router.post("", status_code=201)
def create_associations(
    association_data: AssociationCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Creates new associations between one FMEA item and multiple CP items.
    It will overwrite existing associations for the given FMEA item.
    """
    fmea_item_id = association_data.fmea_item_id
    cp_item_ids = association_data.cp_item_ids

    # 1. Validate that the FMEA item exists
    fmea_item = db.query(models.Item).filter(models.Item.id == fmea_item_id).first()
    if not fmea_item:
        raise HTTPException(status_code=404, detail=f"FMEA item with id {fmea_item_id} not found.")

    # 2. (Transactional) Delete all existing associations for this FMEA item
    try:
        db.query(models.Association).filter(models.Association.fmea_item_id == fmea_item_id).delete()

        # 3. Create new association objects
        new_associations = []
        for cp_id in cp_item_ids:
            new_assoc = models.Association(
                fmea_item_id=fmea_item_id,
                cp_item_id=cp_id,
                created_by=current_user.username
            )
            new_associations.append(new_assoc)
        
        if new_associations:
            db.bulk_save_objects(new_associations)
        
        db.commit()
        return {"message": f"Associations for FMEA item {fmea_item_id} have been updated successfully."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
