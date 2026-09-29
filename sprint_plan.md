## SPRINT PLAN

### Sprint 1 — Project Scaffold & Core Config
Set up backend (FastAPI) and frontend (React/Vite) skeletons, Docker Compose (API + Postgres + Redis), `.env.example`, `core/config.py`, DB connection, base `main.py`, health-check endpoint, and empty layered folder structure per the master prompt. Verify `docker-compose up` boots all services and `/health` returns 200.

### Sprint 2 — Data Models & Database Schema
Define SQLAlchemy models (Prospect, Report, BatchJob, ScoreResult, RatingFlag) + Alembic migrations. Define Pydantic request/response schemas for the "Common Prospect Schema" that all three intake channels normalize into. No business logic yet — just schema + migrations + a seed script.

### Sprint 3 — Single Prospect Intake (Web Form)
Build `POST /prospect/web-form` end-to-end: validate input → normalize → save Prospect to Postgres → return prospect_id. Build the matching React `WebForm.jsx` + `prospectService.js`. No external API calls yet — just intake → DB → confirmation.

### Sprint 4 — External Service Integrations (PageSpeed, SEMrush, Logo)
Build `services/pagespeed.py`, `services/semrush.py`, `services/logo_extractor.py` — client, parser, transformer for each, with caching (Redis) and error/timeout handling. Wire into a single "analyze prospect" flow triggered from the Sprint 3 endpoint, run synchronously for now.

### Sprint 5 — Crawler Service
Build `services/crawler/` — spider.py (depth-limited, rate-limited crawl per the moderate config above), lead_gen.py, broken_links.py, ui_audit.py. Include robots.txt respect and per-domain concurrency limits. Return structured findings.

### Sprint 6 — Scoring Engine + Content Appropriateness
Build `services/scoring_engine/` — category scorers, configurable weights, benchmark thresholds, aggregator producing overall score + critical-focus list. Build the automated content-appropriateness heuristic as a pre-report gate.

### Sprint 7 — Report Generation (PDF/Word/Preview)
Build Jinja2 templates (base, header, scores, details, supplementary, critical_focus), `report_generator.py` for PDF (WeasyPrint), Word (python-docx), and HTML live preview. Wire up `GET /report/preview/{id}`, `/report/pdf/{id}`, `/report/word/{id}`.

### Sprint 8 — Async Batch Processing (Celery + Excel/HubSpot)
Set up `celery_app.py`, `tasks/process_prospect.py`, `tasks/process_batch.py`. Build Excel upload parsing (`utils/excel_parser.py`) and HubSpot read-only client (`services/hubspot.py`). Build `/batch/submit`, `/batch/status/{id}`, `/batch/results/{id}`, `/batch/download/{id}/zip`.

### Sprint 9 — Frontend Batch Dashboard & Report UI
Build `BatchDashboard.jsx`, `ProspectStatusRow.jsx`, polling hook (`useBatchStatus.js`), `ReportPreview.jsx`, `ScoreGauge.jsx`/`ScoreChart.jsx`, `ExportButtons.jsx`. Wire fully to backend from Sprints 7–8.

### Sprint 10 — Hardening, Rate Limiting, Security, Deploy
Add rate-limit middleware, global error handler, input validation pass, HubSpot OAuth/token security review, CI pipeline (GitHub Actions), production Docker Compose / K8s manifests, and a deployment runbook.