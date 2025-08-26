import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import json

from src.database import models, database
from src.parsers import fmea_parser, cp_parser

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...), # User must specify 'FMEA' or 'CP'
    user: str = Form(...), # The user performing the upload
    db: Session = Depends(database.get_db)
):
    """
    Uploads an FMEA or CP Excel file, parses it, and stores it in the database.
    """
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

    # Choose the correct parser based on the document type
    parser = fmea_parser if document_type.upper() == 'FMEA' else cp_parser
    parsed_result = parser.parse(file_like_object)

    if parsed_result.get('status') != 'success':
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {parsed_result.get('message')}")

    # --- Database Transaction ---
    try:
        # 1. Create a new document record
        new_document = models.Document(
            file_name=file.filename,
            document_type=document_type.upper(),
            uploaded_by=user
        )
        db.add(new_document)
        db.flush() # Flush to get the new_document.id for the items

        # 2. Create item records in bulk
        items_to_create = []
        for i, record in enumerate(parsed_result.get('data', [])):
            item = models.Item(
                document_id=new_document.id,
                row_index=i, # Simple index for now
                content=json.dumps(record, ensure_ascii=False)
            )
            items_to_create.append(item)
        
        db.bulk_save_objects(items_to_create)
        db.commit()
        db.refresh(new_document)

        return {
            "message": "Document uploaded and processed successfully",
            "document_id": new_document.id,
            "file_name": new_document.file_name,
            "items_created": len(items_to_create)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


@router.get("/")
def list_documents(db: Session = Depends(database.get_db)):
    """
    Retrieves a list of all uploaded documents from the database.
    """
    try:
        documents = db.query(models.Document).order_by(models.Document.created_at.desc()).all()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{document_id}")
def get_document_details(document_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves details for a specific document, including all its associated items.
    """
    try:
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # The 'items' are automatically loaded thanks to the relationship in models.py
        # We need to manually parse the JSON content string back into an object for each item
        result = {
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type,
            "version": document.version,
            "uploaded_by": document.uploaded_by,
            "created_at": document.created_at,
            "items": [
                {
                    "id": item.id,
                    "row_index": item.row_index,
                    "content": json.loads(item.content) # Deserialize JSON string to object
                } for item in document.items
            ]
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
