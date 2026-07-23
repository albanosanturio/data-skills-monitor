# Tech Skills Monitor

## Overview & Problem

Track what technical skills employers are actually demanding in data engineering, analytics engineering, and BI roles. Aggregate job postings from multiple sources, extract skill requirements, monitor Python package adoption trends, and visualize demand patterns.

**Why?** As a data engineer re-entering the job market, I need to understand what skills are in demand, what tools companies are using, and how trends are shifting. This project automates that analysis.

---

## Architecture & Flow

```
Data Sources (Indeed, Stack Overflow Jobs)
        ↓
[Daily] Scrape job postings
        ↓
Store raw data (PostgreSQL)
        ↓
Extract skills from descriptions (regex + Claude API fallback)
        ↓
Fetch PyPI download trends for key packages
        ↓
Transform & normalize (dbt models)
        ↓
Query analytics tables
        ↓
Visualize in Streamlit dashboard
```

### Component Breakdown

| Component | Purpose | Tech |
|-----------|---------|------|
| **Scraper** | Collect job postings | Python (BeautifulSoup, Playwright) |
| **Storage** | Raw data warehouse | PostgreSQL (Supabase) |
| **Skill Extraction** | Parse job descriptions for skills | Regex + Claude API |
| **PyPI Tracker** | Monitor package adoption | pypistats.org API |
| **Transform** | Clean & model data | dbt |
| **Orchestration** | Daily automation | GitHub Actions + Airflow |
| **Dashboard** | Interactive visualizations | Streamlit |

---

## Dependencies

- `python-dotenv` — Load environment variables from .env
- `sqlalchemy` — Database ORM for PostgreSQL
- `requests` — HTTP client for scraping
- `beautifulsoup4` — HTML parsing
- `playwright` — Browser automation
- `pandas` — Data manipulation

## Possible improvements
- Add a LLM skill extraction (this can help include new skills)
- Assign confidence scores to skill extraction

## Data Collection: Indeed Scraper

### Source
Remote data engineering/analytics roles via Indeed.com (pagination: 10 jobs/page).

### MVP Scope
- Single country (Argentina)
- First 50 jobs (5 pages)
- Daily scrape via GitHub Actions
- Rate limit: 1 request/2 seconds

### Data per Job
Job title, company, location, description, URL, posted date, scraped date.

### Future
Multi-country support, date filtering, additional sources.