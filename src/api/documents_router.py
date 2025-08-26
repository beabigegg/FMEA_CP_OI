"""
API routes for uploading and retrieving FMEA and Control Plan documents.

This router mirrors the functionality of the original GitHub project’s
`documents_router.py` and includes a fix for the timezone conversion issue
described in the project’s to‑do list【695493780409242†L24-L25】.  All timestamps
returned in responses are converted from UTC to the Asia/Taipei timezone using
the helper in `src.utils.time_utils`.
"""

import io
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import pandas as pd  # Used by the parsers

from src.database import models, database
from src.parsers import fmea_parser, cp_parser
from src.utils import fe_list_parser  # New parser for FE options
from src.utils.time_utils import to_local
from src import security # Import the new security module

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),  # User must specify 'FMEA' or 'CP'
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Uploads an FMEA or CP Excel file, parses it, and stores it in the database.

    The file is parsed according to its document type.  On success the new
    document and associated items are persisted in the database.
    """
    # Validate content type
    if file.content_type not in [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")

    if document_type.upper() not in ['FMEA', 'CP']:
        raise HTTPException(status_code=400, detail="Invalid document_type. Must be 'FMEA' or 'CP'.")

    # Read file content into a pandas-readable format
    file_content = file.file.read()
    file_like_object = io.BytesIO(file_content)

    # Choose the correct parser based on the document type.
    # For FMEA we additionally extract FE options from the LIST sheet.
    parser = fmea_parser if document_type.upper() == 'FMEA' else cp_parser

    # Parse the main data sheet
    parsed_result = parser.parse(file_like_object)
    if parsed_result.get('status') != 'success':
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {parsed_result.get('message')}")

    # If FMEA, parse the FE list from the same file content
    fe_records = []
    if document_type.upper() == 'FMEA':
        # Recreate the file-like object since the first parser consumed it
        file_like_for_fe = io.BytesIO(file_content)
        fe_parse_result = fe_list_parser.parse(file_like_for_fe)
        if fe_parse_result.get('status') != 'success':
            raise HTTPException(status_code=500, detail=f"Failed to parse FE list: {fe_parse_result.get('message')}")
        fe_records = fe_parse_result.get('data', [])

    # --- Database Transaction ---
    try:
        # 1. Create a new document record
        new_document = models.Document(
            file_name=file.filename,
            document_type=document_type.upper(),
            uploaded_by=current_user.username
        )
        db.add(new_document)
        db.flush()  # Flush to get the new_document.id for the items

        # 2. Create item records in bulk
        items_to_create = []
        # Add main parsed data (process items for FMEA or CP)
        main_records = parsed_result.get('data', [])
        for i, record in enumerate(main_records):
            item = models.Item(
                document_id=new_document.id,
                row_index=i,
                content=json.dumps(record, ensure_ascii=False)
            )
            items_to_create.append(item)

        # Append FE records (only for FMEA).  Row indices continue after main items.
        if fe_records:
            base_index = len(main_records)
            for j, fe_record in enumerate(fe_records):
                item = models.Item(
                    document_id=new_document.id,
                    row_index=base_index + j,
                    content=json.dumps(fe_record, ensure_ascii=False)
                )
                items_to_create.append(item)

        db.bulk_save_objects(items_to_create)
        db.commit()
        db.refresh(new_document)

        return {
            "message": "Document uploaded and processed successfully",
            "document_id": new_document.id,
            "file_name": new_document.file_name,
            "items_created": len(items_to_create),
            "created_at": to_local(new_document.created_at),
            "updated_at": to_local(new_document.updated_at)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("")
def list_documents(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    Retrieves a list of all uploaded documents from the database.  Each
    document’s timestamps are converted to the Asia/Taipei timezone.
    """
    try:
        documents = db.query(models.Document).order_by(models.Document.created_at.desc()).all()
        results = []
        for doc in documents:
            results.append({
                "id": doc.id,
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "version": doc.version,
                "uploaded_by": doc.uploaded_by,
                "created_at": to_local(doc.created_at),
                "updated_at": to_local(doc.updated_at)
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{document_id}")
def get_document_details(document_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    Retrieves details for a specific document, including all its associated items.
    Timestamps on the document and its items are converted to the local
    timezone.
    """
    try:
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        result = {
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type,
            "version": document.version,
            "uploaded_by": document.uploaded_by,
            "created_at": to_local(document.created_at),
            "updated_at": to_local(document.updated_at),
            "items": []
        }

        for item in document.items:
            # Deserialize the JSON content string to a Python object if possible
            try:
                content_obj = json.loads(item.content)
            except Exception:
                content_obj = item.content
            result["items"].append({
                "id": item.id,
                "row_index": item.row_index,
                "content": content_obj,
                "edited_by": item.edited_by,
                "created_at": to_local(item.created_at),
                "updated_at": to_local(item.updated_at)
            })
        return result
    except HTTPException:
        # Allow HTTPException to propagate unchanged
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")