"""
API routes for retrieving Failure Effects (FE) options from FMEA documents.

When an FMEA Excel file is uploaded, the ``LIST`` sheet is parsed and its
records are stored as ``FmeaFeItem`` entries.  Each FE entry has a
``failure_effect`` and a ``severity``.
This router exposes endpoints for clients to query those options for a
specific document.  The client can then use these options to present a
dropdown list where selecting a failure effect automatically populates its
severity value.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from src.database import models, database
from src.utils.time_utils import to_local

router = APIRouter(
    prefix="/fe",
    tags=["Failure Effects"]
)

@router.get("/documents/{document_id}")
def get_fe_options(
    document_id: int = Path(..., description="ID of the FMEA document"),
    db: Session = Depends(database.get_db)
):
    """
    Retrieves all Failure Effect options for a given FMEA document.  Each
    option includes the effect description and its severity rating.  The
    document must exist and be of type ``FMEA``.

    Returns a list of objects with ``id`` (item id), ``failure_effect`` and
    ``severity``.  Timestamps are also provided for auditing.
    """
    # Fetch the document
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.document_type != 'FMEA':
        raise HTTPException(status_code=400, detail="Failure Effects are only defined for FMEA documents")

    options = []
    for item in document.fmea_fe_items:
        options.append({
            'item_id': item.id,
            'failure_effect': item.failure_effect,
            'severity': item.severity,
            'created_at': to_local(item.created_at),
            'updated_at': to_local(item.updated_at)
        })
    # Sort options by severity descending then alphabetically for consistency
    options.sort(key=lambda x: (-x['severity'], x['failure_effect']))
    return options
