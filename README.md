# Prospect Digital Analyzer 🚀

A high-performance B2B sales intelligence platform that automatically crawls and analyzes prospect websites, diagnosing performance bottlenecks, SEO deficiencies, broken links, missing lead generation funnels, and UI/UX issues to produce client-facing sales pitch reports.

---

## 🏗 Architecture & Stack

- **Backend**: FastAPI (Python 3.11+), asynchronous endpoint handling.
- **Database**: PostgreSQL 16 (persistent storage for prospects, audit payloads, batches, and reports) via SQLAlchemy 2.0 (Asyncpg + Psycopg2) and Alembic migrations.
- **Task Queue**: Celery with Redis broker and result backend for asynchronous distributed background processing.
- **Frontend**: React + Vite (TypeScript), Zustand for state management, Axios for API orchestration, and Lucide icons.
- **Auditing Integrations**:
  - Google PageSpeed Insights API (Core Web Vitals & Performance)
  - SEMrush API (SEO, traffic, keyword gaps)
  - Hunter.io (Logo & company enrichment)
  - HubSpot API (Read-only contacts & list imports)
  - Internal Asynchronous Crawler Service (Lead-gen gap analysis, broken link crawl, mobile/UX audit)
- **Scoring Engine**: Multi-category weighted score synthesis with automated content appropriateness heuristics.
- **Report Generation**: PDF (WeasyPrint), Word (.docx), and in-browser interactive HTML live preview.

---

## 📁 Layered Project Structure

```
pre-sales-agent/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── router.py
│       │   └── endpoints/ (health, prospects, audits, reports, batch)
│       ├── core/ (config, database, security)
│       ├── models/ (base, prospect, audit, report)
│       ├── schemas/ (health, prospect, audit)
│       ├── services/ (crawler, pagespeed, semrush, scoring, report_generator)
│       ├── tasks/ (celery_app, audit_tasks)
│       ├── utils/ (logger)
│       └── templates/reports/
└── frontend/
    ├── Dockerfile
    ├── Dockerfile.dev
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── components/ (common, intake, batch, report, admin)
        ├── hooks/ (useHealth)
        ├── services/ (api, healthService)
        ├── store/ (healthStore)
        └── styles/ (theme.css)
```

---

## ⚡ Quick Start (Docker Compose)

1. **Clone & Set Up Environment**:
   ```bash
   cp .env.example .env
   ```

2. **Boot All Services**:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify Service Health**:
   - **Frontend UI**: [http://localhost:5173](http://localhost:5173)
   - **FastAPI Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health) or [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

4. **Shutdown Services**:
   ```bash
   docker-compose down
   ```

---

## 🛠 Local Development Setup (Without Docker)

### Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Run Alembic Migrations
alembic upgrade head

# Start Celery Worker (requires Redis running locally)
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```
