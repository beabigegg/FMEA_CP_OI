"""
API routes for retrieving Failure Effects (FE) options from FMEA documents.

When an FMEA Excel file is uploaded, the ``LIST`` sheet is parsed and its
records are stored as ``Item`` entries alongside the process‑step items.  Each
FE entry has a JSON structure with keys ``failure_effect`` and ``severity``.
This router exposes endpoints for clients to query those options for a
specific document.  The client can then use these options to present a
dropdown list where selecting a failure effect automatically populates its
severity value.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
import json

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
    for item in document.items:
        # Try to parse the item content.  Items inserted by the FE parser
        # contain 'failure_effect' and 'severity'.
        try:
            content = json.loads(item.content)
        except Exception:
            continue
        if isinstance(content, dict) and 'failure_effect' in content and 'severity' in content:
            options.append({
                'item_id': item.id,
                'failure_effect': content['failure_effect'],
                'severity': content['severity'],
                'created_at': to_local(item.created_at),
                'updated_at': to_local(item.updated_at)
            })
    # Sort options by severity descending then alphabetically for consistency
    options.sort(key=lambda x: (-x['severity'], x['failure_effect']))
    return options