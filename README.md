# Tech Skills Monitor

## Overview & Problem

Track what technical skills employers are actually demanding in data engineering, analytics engineering, and BI roles. Aggregate job postings initially from indeed but extensible to multiple sources, extract skill requirements, and visualize demand patterns.

**Why?** As a data engineer re-entering the job market, I need to understand what skills are in demand, what tools companies are using, and how trends are shifting. This project automates that analysis.

---

## Architecture & Flow

```
Data Sources (Indeed, others)
        ↓
[Daily / Weekly] Scrape job postings
        ↓
Store raw data (PostgreSQL-Supabase)
        ↓
Extract skills from descriptions (regex + Claude API fallback)
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
| **Skill Extraction** | Parse job descriptions for skills | Regex |
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
- Add new job posting sources

## Data Collection: Indeed Scraper Implementation

### Architecture
The scraper uses Playwright to automate browser navigation and BeautifulSoup-style DOM querying to extract job data from Indeed.com listing pages.

Note on changes 29/07, decoupled scraping script:

- `scrape_job_listings` → extracts jobs listings and saves links, saves raw JSON to `data/raw/`
- `fetch_job_details.py` → goes through links and retrieves raw html `data/html_raw/`
- `load_jobs_database.py` → reads HTML, validates, inserts jobs to Supabase

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

### Supabase connection
- Changed to a pooler IPV4 connection, ipv6 was blocked

### Anti-Scraping Considerations
- **Headless=False**: Required (headless mode gets blocked)
- **Rate limiting**: 10s delay between pages, 0.5s between jobs
- **Stealth mode**: Hide automation signals from Indeed

### Source
Remote data engineering/analytics roles via Indeed.com (pagination: 16 jobs/page).

### MVP Scope
- Single country (Argentina)
- First 80 jobs (5 pages)
- Daily/Weekly scrape via GitHub Actions
- Rate limit: 1 request/2 seconds

### Data per Job
Job title, company, location, description, URL, posted date, scraped date.
Mandatory: title, description, url, scraped date. The rest can be implemented later on

### Future
Multi-country support, date filtering, additional sources.

### TODO: Next Phase
- [ ] Extract skills from descriptions via regex
- [ ] Store skills in job_skills table
- [ ] Streamlit webapp