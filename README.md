# Tech Skills Monitor

## Overview & Problem

Track what technical skills employers are actually demanding in data engineering, analytics engineering, and BI roles. Aggregate job postings initially from indeed but extensible to multiple sources, extract skill requirements, and visualize demand patterns.

**Why?** As a data engineer re-entering the job market, I need to understand what skills are in demand, what tools companies are using, and how trends are shifting. This project automates that analysis.

EDIT 07/08/2026:
Slightly changing the scope and flow of the project.
After toying around scraping the job-board, i realized its a subtle work itself. *cough cough* thank you cloudflare *cough cough*. So I'm backtracking a bit and ~~wasting~~ investing some time getting some good amount of seed data to feed this reports. I'll find a way later to ingest new data.

So far for now I'll parse job offers and analyze the skills demanded for data roles.
Also I'll be adding a python package dowloand monitor through pypi, first ingesting benchmark data through their archive data vault in BQ, but periodically ingesting fresh data through pypi api.

TLDR: Live ingestion of jobs paused, pivoting to analyising current data and addition of pypi analysis.

---

### Source data
Remote data engineering/analytics roles via Indeed.com (Argentina, Chile and Uruguay)
Job title, company, location, description, URL, posted date, scraped date.

## Architecture & Flow

```
Data Sources (Indeed, others)
        ↓
Extract job data
        ↓
Store raw data (PostgreSQL-Supabase)
        ↓
Extract skills from descriptions (regex based on skill list)
        ↓
Query analytics tables
        ↓
Visualize in Streamlit dashboard
```

## On Hold (Next Phase)
- **Live scraping** — Cloudflare blocks headless browsers; paused for MVP
- **dbt transformations** — Not needed yet; skill extraction is direct
- **GitHub Actions scheduler** — Will add after POC ships
- **PyPI package monitor** — Planned enhancement, not in MVP

### Current Pipeline (Working ✅)
- `parse_htmls.py` — Parse Indeed HTML, extract job data (title, description, company, date)
- `load_to_db.py` — Load parsed jobs into Supabase `jobs` table
- `skill_extract.py` — Regex-match 88 curated skills from descriptions, populate `job_skills` table
- `Streamlit app` — Query & visualize job postings + skill demand (🚀 shipping Monday)

### Data Model
- **jobs** — Raw job postings (14 live)
- **skills** — 88 curated skills (languages, platforms, tools, BI) with tags
- **job_skills** — Extracted skill-job links (regex-based extraction)

## Stack

| Component | Purpose | Tech |
|-----------|---------|------|

| **Storage** | Raw data warehouse | PostgreSQL (Supabase) |
| **Skill Extraction** | Parse job descriptions for skills | Regex |
| **PyPI Tracker** | Monitor package adoption | pypistats.org API |
| **Dashboard** | Interactive visualizations | Streamlit |
| **DB Client** | Warehouse connections | SQLAlchemy |

on hold:
~~| **Scraper** | Collect job postings | Python (BeautifulSoup, Playwright) |~~ on hold
~~| **Transform** | Clean & model data | dbt |~~ on hold
~~| **Orchestration** | Daily automation | GitHub Actions + Airflow |~~ on hold
---

## Dependencies

- `python-dotenv` — Load environment variables from .env
- `sqlalchemy` — Database ORM for PostgreSQL
- `requests` — HTTP client for scraping
- `beautifulsoup4` — HTML parsing
- `playwright` — Browser automation
- `pandas` — Data manipulation
- `streamlit` — Data visualization


## Status & Roadmap - last edit 08/08

### Monday POC (Ship)
- [ ] Build Streamlit app (jobs table + skills display)
- [ ] Skill demand chart (bar chart: top 10 skills)
- [ ] Test locally
- [ ] Deploy to Streamlit Cloud
- [ ] Update README with live link

### Post-Launch Improvements
- [ ] Skill co-occurrence analysis (which skills appear together)
- [ ] Trend over time (skill demand by week/month)
- [ ] Job filters (by location, company, skills)
- [ ] Dynamic skill list from skills.json (no DB query)
- [ ] Hybrid regex + Claude fallback for skill extraction
- [ ] Job descriptions full-text search
- [ ] Export jobs as CSV
- [ ] GitHub Actions scheduler (daily scrape + extract)
- [ ] Unit tests for regex extraction
