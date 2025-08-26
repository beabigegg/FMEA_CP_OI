from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from src.database import models, database

router = APIRouter(
    prefix="/associations",
    tags=["Associations"],
)

@router.post("/")
def create_association(
    fmea_item_id: int = Body(...),
    cp_item_id: int = Body(...),
    user: str = Body(...),
    db: Session = Depends(database.get_db)
):
    """
    Creates an association between an FMEA item and a Control Plan item.
    """
    try:
        # Check if the items exist and are of the correct type
        fmea_item = db.query(models.Item).join(models.Document).filter(
            models.Item.id == fmea_item_id, 
            models.Document.document_type == 'FMEA'
        ).first()
        cp_item = db.query(models.Item).join(models.Document).filter(
            models.Item.id == cp_item_id, 
            models.Document.document_type == 'CP'
        ).first()

        if not fmea_item:
            raise HTTPException(status_code=404, detail=f"FMEA item with id {fmea_item_id} not found.")
        if not cp_item:
            raise HTTPException(status_code=404, detail=f"CP item with id {cp_item_id} not found.")

        # Create the new association
        new_association = models.Association(
            fmea_item_id=fmea_item_id,
            cp_item_id=cp_item_id,
            created_by=user
        )
        db.add(new_association)
        db.commit()
        db.refresh(new_association)

        return {
            "message": "Association created successfully",
            "association_id": new_association.id
        }
    except Exception as e:
        db.rollback()
        # Handle unique constraint violation
        if 'unique_association' in str(e).lower():
            raise HTTPException(status_code=409, detail="This association already exists.")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
