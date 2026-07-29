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

## Data Collection: Indeed Scraper Implementation

### Architecture
The scraper uses Playwright to automate browser navigation and BeautifulSoup-style DOM querying to extract job data from Indeed.com listing pages.

Note on changes 29/07, decoupled scraping script:

- `indeed_scraper.py` → extracts job data, saves raw JSON to `data/raw/`
- `populate_db.py` → reads JSON, validates, inserts to Supabase

**Why**: Scraper failures don't corrupt DB. Raw data preserved for auditing. Schema changes don't require re-scraping.

### Key Components
- `IndeedScraper` class: Main scraper logic
- `_scrape_page()`: Handles pagination (navigates each page URL)
- `_parse_job()`: Extracts title and URL from each job card

### Playwright Methods Used
- `.goto()` — Navigate to Indeed page
- `.wait_for_selector()` — Wait for jobs to load
- `.query_selector_all()` — Find all job cards
- `.get_attribute()` / `.text_content()` — Extract job data

### Anti-Scraping Considerations
- **Headless=False**: Required (headless mode gets blocked)
- **Rate limiting**: 10s delay between pages, 0.5s between jobs
- **Stealth mode**: Hide automation signals from Indeed

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

### TODO: Next Phase
- [ ] Test and fix Supabase database connection
- [ ] Uncomment _save_job() to store jobs in database
- [ ] Scrape job detail pages to extract description
- [ ] Extract skills from descriptions via regex
- [ ] Store skills in job_skills table