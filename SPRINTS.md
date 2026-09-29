# Prospect Digital Analyzer — Sprint Roadmap & Architecture 🚀

This document outlines the systematic, sprint-by-sprint development plan for **Prospect Digital Analyzer** — a production-grade B2B sales intelligence platform that crawls and audits prospect websites to generate high-converting client pitch decks and audit reports.

---

## 📅 Sprint Overview & Status Matrix

| Sprint | Focus Area | Status | Deliverables |
| :--- | :--- | :---: | :--- |
| **Sprint 1** | Project Scaffold & Core Config | ✅ **Completed** | FastAPI, React/Vite, Docker Compose, PostgreSQL 16, Redis 7, Celery skeleton, Health endpoint (`/health`). |
| **Sprint 2** | Data Models & Database Schema | ✅ **Completed** | SQLAlchemy 2.0 models (`Prospect`, `BatchJob`, `ScoreResult`, `RatingFlag`, `Report`), Alembic migrations, Common Prospect Pydantic schema, Seed script. |
| **Sprint 3** | Single Prospect Intake (Web Form) | ✅ **Completed** | `POST /prospect/web-form`, Pydantic normalization, Postgres persistence, React `WebForm.tsx`, `prospectService.ts`. |
| **Sprint 4** | External Services (PageSpeed, SEMrush, Logo) | ✅ **Completed** | Google PageSpeed client (Core Web Vitals), SEMrush client, Multi-tiered Logo Extractor, Redis caching, Synchronous parallel orchestrator. |
| **Sprint 5** | Internal Crawler Service | ✅ **Completed** | Depth-limited async spider (`spider.py`), `robots.txt` parser, Lead Gen gap analysis, Broken link detector, UI/UX audit, 5-score synthesis. |
| **Sprint 6** | Scoring Engine & Moderation | ✅ **Completed** | Weighted scoring engine (0–100), letter grade (A–F), critical focus areas, automated content moderation gate (`MODERATION_FLAGGED` status), `RatingFlag` persisted to PostgreSQL. |
| **Sprint 7** | Multi-Format Report Generator | ✅ **Completed** | Jinja2 dark-theme HTML report template, WeasyPrint 323KB PDF generator, python-docx 38KB Word generator, `GET /reports/{id}/preview|pdf|docx` endpoints. |
| **Sprint 8** | Intake Channels & Celery Batch | ✅ **Completed** | HubSpot API list/contact picker, Excel bulk upload (`openpyxl`/`pandas`), Asynchronous Celery distributed worker tasks. |
| **Sprint 9** | Frontend Batch Dashboard & Report UI | ✅ **Completed** | Batch monitoring dashboard, polling hooks, interactive report viewing (HTML preview/PDF/Word). |
| **Sprint 10** | Hardening, Security, Deploy | ✅ **Completed** | Rate-limit middleware (`slowapi`), global error handler, CI pipeline, K8s manifests, final hardening. |

---

## 📋 Detailed Sprint Breakdowns

### Sprint 1 — Project Scaffold & Core Config (Completed)
- **Goal**: Establish the full-stack skeleton with isolated Docker Compose services and verified connectivity.
- **Key Modules**:
  - FastAPI backend with async architecture (`app/core/config.py`, `app/core/database.py`).
  - PostgreSQL 16 + Redis 7 + Celery worker container setup.
  - React + Vite + TypeScript frontend with Zustand state store and Axios client.
  - Health check probes at `/health` and `/api/v1/health` verifying live DB and Redis states.

---

### Sprint 2 — Data Models & Database Schema (Current)
- **Goal**: Build the relational data layer, migration pipeline, and normalized input schemas.
- **Key Deliverables**:
  - **SQLAlchemy 2.0 ORM Models**:
    - `Prospect`: Core target company entity with contact info, source channel, domain indexing, and status tracking.
    - `BatchJob`: Tracks bulk upload sessions, HubSpot list syncs, and progress counters.
    - `ScoreResult`: Stores 5 category scores (Performance, SEO, Lead Gen, UI/UX, Broken Links), overall score, critical focus areas, and raw JSON payloads.
    - `RatingFlag`: Automated heuristic content moderation flags (adult, political, parked domain, etc.).
    - `Report`: Tracks generated PDF, DOCX, and live HTML preview cache.
  - **Common Prospect Schema (Pydantic v2)**:
    - Normalization pipeline for Manual, HubSpot, and Excel intake.
    - Automated domain extraction, URL protocol validation, and email sanitization.
  - **Alembic Migrations**:
    - Versioned migration script establishing tables, foreign keys with cascading rules, and indexes.
  - **Database Seed Script**:
    - Generates realistic test data across all sources and status states for development.

---

### Sprint 3 — Internal Crawler Service & External APIs
- **Goal**: Implement high-throughput, respectful crawling and external API clients.
- **Key Deliverables**:
  - **Internal Asynchronous Crawler**:
    - Lead Generation Gap Analysis: Detects contact forms, click-to-call phone numbers, CTAs, live chat widgets, newsletter signups.
    - Broken Link Detection: Internal/external link crawler, 404 detector, redirect chain tracking.
    - Technical UI/UX Audit: Mobile viewport tags, image alt text coverage, HTTPS/SSL validity, heading structure.
    - Rate limiter & safety: Max 2 concurrent requests per domain, 1.5s delay, max 20 pages/depth 2, robots.txt parser, custom User-Agent.
  - **External API Clients**:
    - Google PageSpeed Insights API (Core Web Vitals, Performance metrics).
    - SEMrush API (Organic traffic, keyword count, backlink authority) with cost caching.
    - Hunter.io API (Company logo extraction & domain search).
    - HubSpot API (Read-only contacts & list picker integration).

---

### Sprint 4 — Scoring Engine & Automated Content Moderation
- **Goal**: Transform raw audit data into actionable scores and filter inappropriate targets.
- **Key Deliverables**:
  - **Scoring Engine**:
    - Configurable weighted category score calculation:
      - Performance (25%)
      - SEO (25%)
      - Lead Generation (25%)
      - UI/UX & Mobile (15%)
      - Broken Links (10%)
    - Weighted synthesis into 0–100 overall score.
    - "Areas Requiring Critical Focus" heuristic algorithm that pinpoints top pitch angles for sales reps.
  - **Content Appropriateness Rating (Automated Heuristic)**:
    - Analyzes crawled text and meta tags for unsuitable content (adult, political campaigns, parked domains, under construction).
    - Automatically flags prospects before reports are generated.

---

### Sprint 5 — Multi-Format Client-Facing Report Generation
- **Goal**: Produce beautiful, branded pitch collateral across multiple formats.
- **Key Deliverables**:
  - **Jinja2 Shared Templates**:
    - Single source of truth for report layout, scoring visualization, critical focus callouts, and recommendations.
  - **WeasyPrint PDF Generator**:
    - High-resolution, pixel-perfect executive PDF report.
  - **python-docx Generator**:
    - Editable Microsoft Word document for sales reps who want to customize pitch copy.
  - **In-Browser HTML Preview**:
    - Responsive, interactive live report view inside the web application.

---

### Sprint 6 — Intake Channels & Celery Async Batch Processing
- **Goal**: Enable frictionless prospect data ingestion and asynchronous queue handling.
- **Key Deliverables**:
  - **Intake Pipeline 1: Manual Web Form**:
    - Single-click prospect submission with instant preview.
  - **Intake Pipeline 2: HubSpot CRM Picker**:
    - Read-only OAuth / Private App token connection to fetch active contact lists and companies.
  - **Intake Pipeline 3: Excel / CSV Bulk Upload**:
    - `pandas` / `openpyxl` parser validating spreadsheet columns against the Common Prospect Schema.
  - **Celery Task Orchestration**:
    - Asynchronous workflow: Intake → Moderation Check → Crawler + PageSpeed + SEMrush in parallel → Scoring → Report Generation → Batch Completion.

---

### Sprint 7 — Sales Rep Frontend UI & Reporting Hub
- **Goal**: Deliver a high-converting, modern web application for sales teams.
- **Key Deliverables**:
  - **Prospect Intake Dashboard**: Tabs for Manual, HubSpot, and Excel uploads with instant validation feedback.
  - **Batch Queue Monitor**: Real-time polling with progress bars, status indicators, and error summaries.
  - **Interactive Report Viewer**: Visual score gauges, category breakdowns, lead-gen gaps, and critical focus highlights.
  - **Export Suite**: One-click download for PDF, DOCX, and batch ZIP bundles.

---

### Sprint 8 — Production Hardening, Security & Deployment
- **Goal**: Harden for enterprise scale and multi-tenant deployment.
- **Key Deliverables**:
  - Nginx reverse proxy configuration with gzip and static asset caching.
  - Rate limiting middleware per IP / API token.
  - Production Docker builds with non-root security contexts.
  - Kubernetes manifests (Deployments, Services, ConfigMaps, Secrets, Ingress).
