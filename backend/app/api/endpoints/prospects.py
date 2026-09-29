"""Prospect endpoints for manual intake, external analysis orchestration, listing, and inspection."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.prospect import Prospect, ProspectSource, ProspectStatus
from app.schemas.common_prospect import ManualIntakeRequest
from app.schemas.prospect import (
    ProspectListResponse,
    ProspectRead,
    ProspectWebFormResponse,
)
from app.services.orchestrator import analyzer_orchestrator
from app.utils.logger import logger

router = APIRouter()


@router.post(
    "/web-form",
    response_model=ProspectWebFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manual Prospect Intake, Scoring & Moderation",
    description="Validates single prospect, saves to PostgreSQL, and runs PageSpeed, SEMrush, Logo, Crawler, Scoring Engine, and Content Moderation.",
)
async def intake_web_form(
    payload: ManualIntakeRequest,
    db: AsyncSession = Depends(get_async_db),
) -> ProspectWebFormResponse:
    """End-to-end manual web form ingestion with full multi-engine audit, scoring, and content moderation."""
    # 1. Normalize input via CommonProspectInput adapter
    common = payload.to_common_input()

    logger.info(
        f"Processing manual intake for company='{common.company_name}' "
        f"url='{common.website_url}' domain='{common.domain}'"
    )

    # 2. Instantiate and persist initial Prospect model
    prospect = Prospect(
        id=uuid.uuid4(),
        company_name=common.company_name,
        website_url=common.website_url,
        domain=common.domain,
        contact_name=common.contact_name,
        contact_email=str(common.contact_email) if common.contact_email else None,
        contact_title=common.contact_title,
        contact_phone=common.contact_phone,
        source=ProspectSource.MANUAL,
        status=ProspectStatus.PENDING,
        notes=common.notes,
    )

    db.add(prospect)
    await db.commit()
    await db.refresh(prospect)

    # 3. Trigger synchronous analysis & scoring
    audit_results = await analyzer_orchestrator.analyze_prospect(prospect, db)

    return ProspectWebFormResponse(
        prospect_id=prospect.id,
        company_name=prospect.company_name,
        domain=prospect.domain,
        website_url=prospect.website_url,
        source=prospect.source,
        status=prospect.status,
        message="Prospect successfully evaluated and scored.",
        created_at=prospect.created_at,
        logo_url=audit_results.get("logo_url"),
        overall_score=audit_results.get("overall_score"),
        letter_grade=audit_results.get("letter_grade"),
        grade_label=audit_results.get("grade_label"),
        grade_color=audit_results.get("grade_color"),
        performance_score=audit_results.get("performance_score"),
        seo_score=audit_results.get("seo_score"),
        lead_gen_score=audit_results.get("lead_gen_score"),
        ui_ux_score=audit_results.get("ui_ux_score"),
        broken_links_score=audit_results.get("broken_links_score"),
        category_weights=audit_results.get("category_weights"),
        moderation=audit_results.get("moderation"),
        pagespeed_data=audit_results.get("pagespeed"),
        semrush_data=audit_results.get("semrush"),
        crawler_data=audit_results.get("crawler"),
        critical_focus_areas=audit_results.get("critical_focus_areas"),
    )


@router.post(
    "/{prospect_id}/analyze",
    response_model=ProspectWebFormResponse,
    summary="Re-analyze existing prospect",
    description="Re-runs all audit engines, scoring, and moderation on an existing prospect in the database.",
)
async def trigger_prospect_analysis(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> ProspectWebFormResponse:
    """Manually triggers audit scoring & moderation for an existing prospect."""
    stmt = select(Prospect).where(Prospect.id == prospect_id)
    res = await db.execute(stmt)
    prospect = res.scalar_one_or_none()

    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect with ID {prospect_id} not found.",
        )

    audit_results = await analyzer_orchestrator.analyze_prospect(prospect, db)

    return ProspectWebFormResponse(
        prospect_id=prospect.id,
        company_name=prospect.company_name,
        domain=prospect.domain,
        website_url=prospect.website_url,
        source=prospect.source,
        status=prospect.status,
        message="Prospect scoring and moderation completed successfully.",
        created_at=prospect.created_at,
        logo_url=audit_results.get("logo_url"),
        overall_score=audit_results.get("overall_score"),
        letter_grade=audit_results.get("letter_grade"),
        grade_label=audit_results.get("grade_label"),
        grade_color=audit_results.get("grade_color"),
        performance_score=audit_results.get("performance_score"),
        seo_score=audit_results.get("seo_score"),
        lead_gen_score=audit_results.get("lead_gen_score"),
        ui_ux_score=audit_results.get("ui_ux_score"),
        broken_links_score=audit_results.get("broken_links_score"),
        category_weights=audit_results.get("category_weights"),
        moderation=audit_results.get("moderation"),
        pagespeed_data=audit_results.get("pagespeed"),
        semrush_data=audit_results.get("semrush"),
        crawler_data=audit_results.get("crawler"),
        critical_focus_areas=audit_results.get("critical_focus_areas"),
    )


@router.get(
    "/",
    response_model=ProspectListResponse,
    summary="List all prospects",
    description="Retrieves paginated list of prospects with optional filtering by status or source.",
)
async def list_prospects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    source: Optional[ProspectSource] = Query(None, description="Filter by intake source"),
    prospect_status: Optional[ProspectStatus] = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_async_db),
) -> ProspectListResponse:
    """Lists prospects with pagination and filters."""
    query = select(Prospect)

    if source:
        query = query.where(Prospect.source == source)
    if prospect_status:
        query = query.where(Prospect.status == prospect_status)

    count_stmt = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = query.order_by(Prospect.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    prospects = result.scalars().all()

    return ProspectListResponse(
        items=[ProspectRead.model_validate(p) for p in prospects],
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{prospect_id}",
    response_model=ProspectRead,
    summary="Get single prospect",
    description="Fetches full details of a specific prospect by its UUID.",
)
async def get_prospect(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> ProspectRead:
    """Fetches single prospect by ID."""
    stmt = select(Prospect).where(Prospect.id == prospect_id)
    result = await db.execute(stmt)
    prospect = result.scalar_one_or_none()

    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect with ID {prospect_id} not found.",
        )

    return ProspectRead.model_validate(prospect)
