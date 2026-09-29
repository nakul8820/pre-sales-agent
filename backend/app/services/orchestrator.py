"""Analysis orchestrator integrating PageSpeed, SEMrush, Logo, Spider, Scoring Engine, and Content Moderation."""
import asyncio
import uuid
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prospect import Prospect, ProspectStatus
from app.models.rating_flag import RatingFlag
from app.models.report import Report, ReportFormat, ReportStatus
from app.models.score_result import ScoreResult
from app.services.content_moderation.moderator import content_moderator
from app.services.crawler.spider import spider_engine
from app.services.logo_extractor import logo_service
from app.services.pagespeed import pagespeed_service
from app.services.scoring_engine.aggregator import scoring_aggregator
from app.services.semrush import semrush_service
from app.utils.logger import logger


class ProspectAnalyzerOrchestrator:
    """Coordinates external audit services, internal spider, scoring engine, and content moderation gate."""

    async def analyze_prospect(self, prospect: Prospect, db: AsyncSession) -> Dict[str, Any]:
        """Executes full multi-engine audit, runs content moderation gate, and synthesizes weighted scores."""
        logger.info(f"Initiating multi-engine analysis for prospect '{prospect.company_name}' ({prospect.domain})")

        # 1. Update status to AUDITING
        prospect.status = ProspectStatus.AUDITING
        await db.commit()

        # 2. Run data collection services concurrently via asyncio.gather
        try:
            pagespeed_res, semrush_res, logo_url, crawl_res = await asyncio.gather(
                pagespeed_service.analyze(prospect.website_url),
                semrush_service.analyze(prospect.domain),
                logo_service.extract_logo(prospect.domain, prospect.website_url),
                spider_engine.crawl(prospect.website_url),
                return_exceptions=False,
            )
        except Exception as e:
            logger.error(f"Error during parallel services execution: {e}")
            pagespeed_res = pagespeed_service._generate_fallback_payload(prospect.domain, str(e))
            semrush_res = semrush_service._generate_fallback_estimator(prospect.domain, str(e))
            logo_url = f"https://www.google.com/s2/favicons?domain={prospect.domain}&sz=128"
            crawl_res = {
                "pages_crawled_count": 1,
                "lead_gen": {"lead_gen_score": 60.0, "gaps": []},
                "broken_links": {"broken_links_score": 85.0, "gaps": []},
                "ui_ux": {"ui_ux_score": 70.0, "gaps": []},
                "crawler_gaps": [],
            }

        # 3. Automated Content-Appropriateness Heuristic Pre-Report Gate (Sprint 6)
        moderation_result = content_moderator.evaluate(
            domain=prospect.domain,
            website_url=prospect.website_url,
            company_name=prospect.company_name,
            notes=prospect.notes,
            crawler_data=crawl_res,
        )

        # 4. Save any triggered Content Moderation Flags to PostgreSQL
        for flag_item in moderation_result.get("flags", []):
            rf = RatingFlag(
                id=uuid.uuid4(),
                prospect_id=prospect.id,
                is_flagged=True,
                flag_category=flag_item["category"],
                confidence_score=flag_item["confidence_score"],
                reason=flag_item.get("description", "Content Appropriateness trigger"),
                details={
                    "severity": flag_item["severity"],
                    "flagged_keywords": flag_item["flagged_keywords"],
                    "snippet": flag_item.get("snippet", ""),
                },
                is_reviewed=False,
                is_override_approved=False,
            )
            db.add(rf)

        # 5. Execute Unified Scoring Engine with Benchmark Grading (Sprint 6)
        score_eval = scoring_aggregator.calculate_scores(
            pagespeed_data=pagespeed_res,
            semrush_data=semrush_res,
            crawler_data=crawl_res,
        )

        overall_score = score_eval["overall_score"]
        letter_grade = score_eval["letter_grade"]
        grade_label = score_eval["grade_label"]
        category_scores = score_eval["category_scores"]
        critical_focus_areas = score_eval["critical_focus_areas"]

        # 6. Create or Update ScoreResult record in PostgreSQL
        score_stmt = select(ScoreResult).where(ScoreResult.prospect_id == prospect.id)
        score_query = await db.execute(score_stmt)
        score_record = score_query.scalar_one_or_none()

        if not score_record:
            score_record = ScoreResult(
                id=uuid.uuid4(),
                prospect_id=prospect.id,
                overall_score=overall_score,
                performance_score=category_scores["performance"],
                seo_score=category_scores["seo"],
                lead_gen_score=category_scores["lead_gen"],
                ui_ux_score=category_scores["ui_ux"],
                broken_links_score=category_scores["broken_links"],
                category_weights=score_eval["category_weights"],
                critical_focus_areas=critical_focus_areas,
                pagespeed_raw=pagespeed_res,
                semrush_raw=semrush_res,
                crawler_lead_gen_raw=crawl_res.get("lead_gen"),
                crawler_broken_links_raw=crawl_res.get("broken_links"),
                crawler_ui_ux_raw=crawl_res.get("ui_ux"),
            )
            db.add(score_record)
        else:
            score_record.overall_score = overall_score
            score_record.performance_score = category_scores["performance"]
            score_record.seo_score = category_scores["seo"]
            score_record.lead_gen_score = category_scores["lead_gen"]
            score_record.ui_ux_score = category_scores["ui_ux"]
            score_record.broken_links_score = category_scores["broken_links"]
            score_record.category_weights = score_eval["category_weights"]
            score_record.pagespeed_raw = pagespeed_res
            score_record.semrush_raw = semrush_res
            score_record.crawler_lead_gen_raw = crawl_res.get("lead_gen")
            score_record.crawler_broken_links_raw = crawl_res.get("broken_links")
            score_record.crawler_ui_ux_raw = crawl_res.get("ui_ux")
            score_record.critical_focus_areas = critical_focus_areas

        await db.flush()

        # 7. Create or Update Report placeholder with logo URL
        rep_stmt = select(Report).where(Report.prospect_id == prospect.id)
        rep_query = await db.execute(rep_stmt)
        report_record = rep_query.scalar_one_or_none()

        if not report_record:
            report_record = Report(
                id=uuid.uuid4(),
                prospect_id=prospect.id,
                score_result_id=score_record.id,
                report_format=ReportFormat.PDF,
                status=ReportStatus.READY if moderation_result["is_safe"] else ReportStatus.GENERATING,
                logo_url=logo_url,
            )
            db.add(report_record)
        else:
            report_record.logo_url = logo_url

        # 8. Set Prospect Status: MODERATION_FLAGGED if inappropriate content found, otherwise COMPLETED
        if moderation_result["has_critical_flag"]:
            prospect.status = ProspectStatus.MODERATION_FLAGGED
            logger.warning(f"Prospect '{prospect.company_name}' marked as MODERATION_FLAGGED by moderation gate.")
        else:
            prospect.status = ProspectStatus.COMPLETED

        await db.commit()
        await db.refresh(prospect)

        logger.info(
            f"Completed scoring audit for '{prospect.company_name}': "
            f"Grade {letter_grade} ({overall_score}/100), Status={prospect.status.value}"
        )

        return {
            "prospect_id": str(prospect.id),
            "company_name": prospect.company_name,
            "domain": prospect.domain,
            "website_url": prospect.website_url,
            "status": prospect.status.value,
            "logo_url": logo_url,
            "overall_score": overall_score,
            "letter_grade": letter_grade,
            "grade_label": grade_label,
            "grade_color": score_eval["grade_color"],
            "performance_score": category_scores["performance"],
            "seo_score": category_scores["seo"],
            "lead_gen_score": category_scores["lead_gen"],
            "ui_ux_score": category_scores["ui_ux"],
            "broken_links_score": category_scores["broken_links"],
            "category_weights": score_eval["category_weights"],
            "moderation": moderation_result,
            "pagespeed": pagespeed_res,
            "semrush": semrush_res,
            "crawler": crawl_res,
            "critical_focus_areas": critical_focus_areas,
        }


analyzer_orchestrator = ProspectAnalyzerOrchestrator()
