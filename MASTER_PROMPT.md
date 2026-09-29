## MASTER PROMPT (paste once, at the top of the session)

```
You are helping me build "Prospect Digital Analyzer" — a B2B sales tool that
automatically analyzes a prospect company's website and produces a client-facing
report highlighting weaknesses (performance, SEO, broken links, missing lead-gen
elements, UI/UX issues), used by sales reps to pitch web/marketing services.

ARCHITECTURE (already decided, do not deviate without asking):
- Backend: FastAPI (Python), async where sensible
- Database: PostgreSQL (persistent — prospects, reports, batch history all stored
  permanently, not just cached). Use SQLAlchemy + Alembic for migrations.
- Task queue: Celery + Redis (Redis is broker/cache only now, NOT primary storage)
- Frontend: React + Vite, Redux Toolkit or Zustand for state, Axios for API calls
- Intake channels: (1) manual web form, (2) HubSpot list/contact picker (read-only
  API), (3) Excel upload (openpyxl/pandas)
- External services:
  - Google PageSpeed Insights API (performance/Core Web Vitals) — free, rate-limited
  - SEMrush API (SEO/traffic/keywords) — paid, we have an API key/quota, treat calls
    as cost-bearing, cache results
  - Hunter.io (logo extraction)
  - HubSpot API (read-only contacts/lists/companies)
  - Internal Crawler service (our own code, no external cost) — checks:
      a) Lead Generation Gap Analysis — contact forms, phone numbers, CTAs, chat,
         signup forms
      b) Broken Link Detection — internal/external link crawl, 404s, dead redirects
      c) UI/UX Technical Audit — mobile responsiveness, alt text, meta tags,
         https/SSL, accessibility basics
    Crawler config (moderate limits — implement as constants, not hardcoded):
      - 2 concurrent requests per domain, 1–2s delay between requests same domain
      - 5–10 concurrent domains crawled in parallel across batch
      - Max 15–25 pages per site, max crawl depth 2
      - Per-request timeout 8–10s, total per-site timeout 60–90s
      - Respect robots.txt, identifiable custom User-Agent, 1 retry w/ backoff
- Scoring Engine: weighted category scores (Performance, SEO, Lead Gen, Technical/
  UI, Broken Links) → aggregated overall score + "Areas Requiring Critical Focus"
  section for the report
- Content Appropriateness rating: FULLY AUTOMATED heuristic (not manual) — flags
  prospects whose site content may be unsuitable to pitch against (e.g. adult
  content, political content, under-construction sites) before a report is
  generated or sent
- Report output: PDF (WeasyPrint) and Word (.docx via python-docx), generated from
  shared Jinja2 templates, plus an in-browser live HTML preview
- Batch processing: Excel/HubSpot list → Celery tasks per prospect → async
  processing → React polls batch status → download individually or as zip
- Security: API keys server-side only (.env, never in frontend), Pydantic input
  validation, rate-limiting middleware, HTTPS in prod, HubSpot read-only scope
- Deployment target: Docker Compose for dev, Kubernetes-ready for prod, Nginx +
  load balancer in front of multiple FastAPI instances, scalable Celery worker pool

FOLDER STRUCTURE: follow a standard FastAPI layered structure — api/endpoints,
core, models, schemas, services, tasks (celery), utils, templates — mirrored by a
React structure with components/{common,intake,batch,report,admin}, hooks,
services, store. (Full reference structure available if you want me to paste it.)

WORKING STYLE:
- I will give you one sprint at a time. Fully build out that sprint before moving
  on — don't skip ahead into future sprints' scope.
- Write production-quality code with error handling, not just happy-path demos.
- Call out any assumptions you make explicitly.
- After each sprint, tell me how to run/test what you built.
- Ask before introducing new dependencies not already listed above.
```