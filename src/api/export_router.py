import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from src.database import models, database
from src import security

router = APIRouter(
    prefix="/export",
    tags=["Exporting"],
)

@router.get("/{document_id}", response_class=StreamingResponse)
def export_document_to_excel(
    document_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Exports the FMEA data for a given document, including its associations
    with Control Plan items, into a formatted Excel file.
    """
    # 1. Fetch the document and ensure it's an FMEA document
    document = db.query(models.Document).options(
        joinedload(models.Document.fmea_items),
        joinedload(models.Document.fmea_header)
    ).filter(models.Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.document_type != 'FMEA':
        raise HTTPException(status_code=400, detail="Export is only supported for FMEA documents.")

    fmea_item_ids = [item.id for item in document.fmea_items]

    # 2. Fetch all associations for the items in this document
    associations = db.query(models.Association).options(
        joinedload(models.Association.cp_item)
    ).filter(models.Association.fmea_item_id.in_(fmea_item_ids)).all()

    # 3. Create a map for easy lookup: {fmea_item_id: [list of cp_items]}
    assoc_map = {fmea_id: [] for fmea_id in fmea_item_ids}
    for assoc in associations:
        if assoc.cp_item:
            assoc_map[assoc.fmea_item_id].append(assoc.cp_item)

    # 4. Prepare data for DataFrame
    export_data = []
    for item in document.fmea_items:
        row_data = {
            'FMEA Item ID': item.id,
            'Process Step': item.process_step,
            'Process Function': item.process_function,
            'Failure Mode': item.failure_mode,
            'Failure Cause': item.failure_cause,
            'Prevention Controls': item.prevention_controls,
            'Detection Controls': item.detection_controls,
            'Severity': item.severity,
            'Occurrence': item.occurrence,
            'Detection': item.detection,
            'AP': item.ap
        }

        # Format associated CP items into a single string
        linked_cps = assoc_map.get(item.id, [])
        cp_strings = []
        for cp_item in linked_cps:
            cp_strings.append(
                f"[ID: {cp_item.id}] {cp_item.product_characteristic} - {cp_item.control_method}"
            )
        
        row_data['Associated Control Plan Items'] = "\n".join(cp_strings) if cp_strings else "None"
        export_data.append(row_data)

    if not export_data:
        raise HTTPException(status_code=404, detail="No valid FMEA items found in the document to export.")

    # 5. Create Excel file in memory
    df = pd.DataFrame(export_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'FMEA_{document_id}_Export')
    output.seek(0)

    # 6. Return as a downloadable file
    headers = {
        'Content-Disposition': f'attachment; filename="{document.file_name}_export.xlsx"'
    }

    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')