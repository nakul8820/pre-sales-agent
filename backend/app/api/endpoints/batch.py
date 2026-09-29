import io
import uuid
import zipfile
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.batch_job import BatchJob, BatchSource, BatchStatus
from app.models.prospect import Prospect, ProspectStatus, ProspectSource
from app.models.report import Report, ReportFormat, ReportStatus
from app.schemas.batch import BatchJobListResponse, BatchJobRead
from app.schemas.prospect import ProspectWebFormResponse
from app.services.hubspot_client import hubspot_client
from app.tasks.process_batch import process_batch_task
from app.utils.excel_parser import parse_excel_upload
from app.utils.logger import logger


router = APIRouter()


@router.post("/excel", response_model=BatchJobRead, status_code=status.HTTP_201_CREATED)
async def submit_excel_batch(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Parse an Excel/CSV file, create a BatchJob, and queue it for Celery processing."""
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .csv files are supported.")
        
    contents = await file.read()
    valid_prospects, errors = parse_excel_upload(contents, file.filename)
    
    if not valid_prospects:
        raise HTTPException(
            status_code=422, 
            detail={"message": "No valid prospects found in file.", "errors": errors}
        )
        
    # Create BatchJob
    batch_job = BatchJob(
        id=uuid.uuid4(),
        name=name,
        source=BatchSource.EXCEL_UPLOAD,
        status=BatchStatus.QUEUED,
        total_count=len(valid_prospects),
        metadata_payload={"filename": file.filename, "errors": errors}
    )
    db.add(batch_job)
    
    # Create Prospects
    for p_input in valid_prospects:
        prospect = Prospect(
            id=uuid.uuid4(),
            batch_id=batch_job.id,
            company_name=p_input.company_name,
            website_url=p_input.website_url,
            domain=p_input.domain,
            contact_name=p_input.contact_name,
            contact_email=str(p_input.contact_email) if p_input.contact_email else None,
            contact_title=p_input.contact_title,
            contact_phone=p_input.contact_phone,
            source=ProspectSource.EXCEL_UPLOAD,
            status=ProspectStatus.PENDING,
            notes=p_input.notes,
        )
        db.add(prospect)
        
    await db.commit()
    await db.refresh(batch_job)
    
    # Dispatch batch task
    process_batch_task.delay(str(batch_job.id))
    
    return BatchJobRead.model_validate(batch_job)


@router.get("/hubspot/lists")
async def get_hubspot_lists():
    """Get available HubSpot contact lists."""
    lists = hubspot_client.get_contact_lists()
    return {"items": lists}


@router.post("/hubspot", response_model=BatchJobRead, status_code=status.HTTP_201_CREATED)
async def submit_hubspot_batch(
    name: str = Form(...),
    list_id: str = Form(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Fetch contacts from a HubSpot list, create a BatchJob, and queue it."""
    hs_contacts = hubspot_client.get_contacts_from_list(list_id)
    
    if not hs_contacts:
        raise HTTPException(status_code=404, detail="No valid contacts found in the specified HubSpot list.")
        
    batch_job = BatchJob(
        id=uuid.uuid4(),
        name=name,
        source=BatchSource.HUBSPOT,
        status=BatchStatus.QUEUED,
        total_count=len(hs_contacts),
        metadata_payload={"list_id": list_id}
    )
    db.add(batch_job)
    
    for hs_item in hs_contacts:
        p_input = hs_item.to_common_input()
        prospect = Prospect(
            id=uuid.uuid4(),
            batch_id=batch_job.id,
            company_name=p_input.company_name,
            website_url=p_input.website_url,
            domain=p_input.domain,
            contact_name=p_input.contact_name,
            contact_email=str(p_input.contact_email) if p_input.contact_email else None,
            contact_title=p_input.contact_title,
            contact_phone=p_input.contact_phone,
            source=ProspectSource.HUBSPOT,
            status=ProspectStatus.PENDING,
            hubspot_id=p_input.hubspot_id,
            notes=p_input.notes,
        )
        db.add(prospect)
        
    await db.commit()
    await db.refresh(batch_job)
    
    process_batch_task.delay(str(batch_job.id))
    
    return BatchJobRead.model_validate(batch_job)


@router.get("/status/{batch_id}", response_model=BatchJobRead)
async def get_batch_status(
    batch_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get the current progress and status of a BatchJob."""
    stmt = select(BatchJob).where(BatchJob.id == batch_id)
    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="BatchJob not found")
        
    # Dynamically compute counts from Prospect statuses
    p_stmt = select(Prospect.status, func.count(Prospect.id)).where(Prospect.batch_id == batch_id).group_by(Prospect.status)
    p_res = await db.execute(p_stmt)
    counts = {status: count for status, count in p_res.all()}
    
    completed = counts.get(ProspectStatus.COMPLETED, 0)
    flagged = counts.get(ProspectStatus.MODERATION_FLAGGED, 0)
    failed = counts.get(ProspectStatus.FAILED, 0)
    
    batch.processed_count = completed + flagged + failed
    batch.completed_count = completed
    batch.flagged_count = flagged
    batch.failed_count = failed
    
    # Update status if all done
    if batch.processed_count == batch.total_count and batch.status != BatchStatus.COMPLETED:
        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime.now(timezone.utc)
        await db.commit()
        
    return BatchJobRead.model_validate(batch)


@router.get("/", response_model=BatchJobListResponse)
async def list_batches(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db)
):
    """List paginated batch jobs."""
    count_stmt = select(func.count()).select_from(BatchJob)
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0
    
    stmt = select(BatchJob).order_by(BatchJob.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    batches = result.scalars().all()
    
    return BatchJobListResponse(
        items=[BatchJobRead.model_validate(b) for b in batches],
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/download/{batch_id}/zip")
async def download_batch_zip(
    batch_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Download a ZIP archive containing all PDF reports for a completed batch."""
    stmt = select(Report).join(Prospect).where(
        Prospect.batch_id == batch_id, 
        Report.report_format == ReportFormat.PDF,
        Report.status == ReportStatus.READY,
        Report.file_path != None
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    if not reports:
        raise HTTPException(status_code=404, detail="No PDF reports ready for this batch.")
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for r in reports:
            try:
                import os
                if os.path.exists(r.file_path):
                    filename = os.path.basename(r.file_path)
                    zip_file.write(r.file_path, arcname=filename)
            except Exception as e:
                logger.error(f"Failed to add {r.file_path} to zip: {e}")
                
    zip_buffer.seek(0)
    
    batch_res = await db.execute(select(BatchJob).where(BatchJob.id == batch_id))
    batch = batch_res.scalar_one_or_none()
    safe_name = batch.name.replace(" ", "_") if batch else "batch"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_reports.zip"'}
    )
