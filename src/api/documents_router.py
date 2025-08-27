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
import logging
import traceback
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session, joinedload
import pandas as pd  # Used by the parsers
from datetime import datetime

from src.database import models, database
from src.parsers import fmea_parser, cp_parser
from src.utils import fe_list_parser
from src.utils.time_utils import to_local
from src import security # Import the new security module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),  # User must specify 'FMEA' or 'CP'
    company_name: str = Form(None),
    customer_name: str = Form(None),
    model_year_platform: str = Form(None),
    plant_location: str = Form(None),
    subject: str = Form(None),
    pfmea_start_date: str = Form(None),
    pfmea_revision_date: str = Form(None),
    pfmea_id: str = Form(None),
    process_responsibility: str = Form(None),
    cross_functional_team: str = Form(None),
    confidentiality_level: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Uploads an FMEA or CP Excel file, parses it, and stores it in the database.

    The file is parsed according to its document type.  On success the new
    document and associated items are persisted in the database.
    """
    try:
        logger.info(f"Received upload request for document type: {document_type}")
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

            if document_type.upper() == 'FMEA':
                # Parse the FMEA data
                parsed_result = fmea_parser.parse(file_like_object)
                if parsed_result.get('status') != 'success':
                    raise HTTPException(status_code=500, detail=f"Failed to parse FMEA file: {parsed_result.get('message')}")
                
                # Create FMEA header and items
                try:
                    start_date = datetime.strptime(pfmea_start_date, '%a %b %d %Y %H:%M:%S GMT%z (%Z)').strftime('%Y-%m-%d') if pfmea_start_date and pfmea_start_date.strip() != "" else None
                    revision_date = datetime.strptime(pfmea_revision_date, '%a %b %d %Y %H:%M:%S GMT%z (%Z)').strftime('%Y-%m-%d') if pfmea_revision_date and pfmea_revision_date.strip() != "" else None
                except ValueError as e:
                    logger.error(f"Date parsing error: {e}")
                    raise HTTPException(status_code=400, detail=f"Invalid date format: {e}. Please use YYYY-MM-DD.")

                header_data = {
                    "company_name": company_name,
                    "customer_name": customer_name,
                    "model_year_platform": model_year_platform,
                    "plant_location": plant_location,
                    "subject": subject,
                    "pfmea_start_date": start_date,
                    "pfmea_revision_date": revision_date,
                    "pfmea_id": pfmea_id,
                    "process_responsibility": process_responsibility,
                    "cross_functional_team": cross_functional_team,
                    "confidentiality_level": confidentiality_level
                }
                logger.info(f"Header data: {header_data}")
                fmea_header = models.FmeaHeader(document_id=new_document.id, **header_data)
                db.add(fmea_header)

                items_to_create = []
                for i, record in enumerate(parsed_result.get('data', [])):
                    item = models.FmeaItem(document_id=new_document.id, row_index=i, **record)
                    items_to_create.append(item)
                db.bulk_save_objects(items_to_create)

                # Parse and store FE items
                file_like_object.seek(0)
                fe_parse_result = fe_list_parser.parse(file_like_object)
                if fe_parse_result.get('status') == 'success':
                    fe_items_to_create = []
                    for record in fe_parse_result.get('data', []):
                        item = models.FmeaFeItem(document_id=new_document.id, **record)
                        fe_items_to_create.append(item)
                    db.bulk_save_objects(fe_items_to_create)

            elif document_type.upper() == 'CP':
                # Parse the CP data
                parsed_result = cp_parser.parse(file_like_object)
                if parsed_result.get('status') != 'success':
                    raise HTTPException(status_code=500, detail=f"Failed to parse CP file: {parsed_result.get('message')}")

                # Create CP items
                items_to_create = []
                for i, record in enumerate(parsed_result.get('data', [])):
                    item = models.CpItem(document_id=new_document.id, row_index=i, **record)
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
            logger.error(f"Database error during upload: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {traceback.format_exc()}")


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
        document = db.query(models.Document).options(
            joinedload(models.Document.fmea_header),
            joinedload(models.Document.fmea_items),
            joinedload(models.Document.cp_items)
        ).filter(models.Document.id == document_id).first()

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
        }

        if document.document_type == 'FMEA':
            if document.fmea_header:
                result['header'] = {
                    'company_name': document.fmea_header.company_name,
                    'customer_name': document.fmea_header.customer_name,
                    'model_year_platform': document.fmea_header.model_year_platform,
                    'plant_location': document.fmea_header.plant_location,
                    'subject': document.fmea_header.subject,
                    'pfmea_start_date': document.fmea_header.pfmea_start_date,
                    'pfmea_revision_date': document.fmea_header.pfmea_revision_date,
                    'pfmea_id': document.fmea_header.pfmea_id,
                    'process_responsibility': document.fmea_header.process_responsibility,
                    'cross_functional_team': document.fmea_header.cross_functional_team,
                    'confidentiality_level': document.fmea_header.confidentiality_level
                }
            result['fmea_items'] = document.fmea_items
        elif document.document_type == 'CP':
            result['cp_items'] = document.cp_items

        return result
    except HTTPException:
        # Allow HTTPException to propagate unchanged
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")