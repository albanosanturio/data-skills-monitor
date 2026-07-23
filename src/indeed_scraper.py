"""
data-skills-monitor: Indeed Job Scraper
Scrapes remote data engineering roles from Indeed.com
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'base_url': 'https://ar.indeed.com/jobs',
    'search_query': 'data engineer',
    'jobs_per_page': 10,
    'max_pages': 5,  # MVP: 50 jobs
    'timeout_ms': 30000,
    'rate_limit_seconds': 2,
}


class IndeedScraper:
    """
    Scrapes job postings from Indeed.com
    Handles pagination, error recovery, and database storage
    """

    def __init__(self, db_url: str):
        """
        Initialize scraper with database connection.
        
        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.jobs_scraped = 0
        self.errors = []

    def scrape(self) -> Dict[str, any]:
        """
        Main scrape routine: fetch jobs, extract data, store in DB.
        
        Returns:
            dict with results: {jobs_count, errors, duration}
        """
        start_time = datetime.now()
        logger.info("Starting Indeed scraper...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()

                # Scrape each page
                for page_num in range(CONFIG['max_pages']):
                    try:
                        self._scrape_page(page, page_num)
                    except Exception as e:
                        logger.error(f"Error on page {page_num}: {e}")
                        self.errors.append({'page': page_num, 'error': str(e)})

                browser.close()

        except Exception as e:
            logger.error(f"Browser error: {e}")
            self.errors.append({'type': 'browser', 'error': str(e)})

        duration = (datetime.now() - start_time).total_seconds()
        result = {
            'jobs_scraped': self.jobs_scraped,
            'errors_count': len(self.errors),
            'duration_seconds': duration,
            'errors': self.errors,
        }

        logger.info(f"Scrape complete: {self.jobs_scraped} jobs, {len(self.errors)} errors, {duration:.1f}s")
        return result

    def _scrape_page(self, page, page_num: int) -> None:
        """
        Scrape a single page of results.
        
        Args:
            page: Playwright page object
            page_num: Page number (0-indexed)
        """
        start_param = page_num * CONFIG['jobs_per_page']
        url = f"{CONFIG['base_url']}?q={CONFIG['search_query']}&start={start_param}"

        logger.info(f"Scraping page {page_num + 1} ({start_param} jobs)...")

        # Navigate and wait for jobs to load
        page.goto(url, timeout=CONFIG['timeout_ms'])
        page.wait_for_selector('[data-jk]', timeout=CONFIG['timeout_ms'])

        # Extract job elements
        job_elements = page.query_selector_all('[data-jk]')
        logger.debug(f"Found {len(job_elements)} job elements on page {page_num + 1}")

        # Parse each job
        for job_elem in job_elements:
            try:
                job_data = self._parse_job(job_elem)
                if job_data:
                    self._save_job(job_data)
                    self.jobs_scraped += 1
            except Exception as e:
                logger.error(f"Error parsing job: {e}")
                self.errors.append({'type': 'parse', 'error': str(e)})

        # Rate limiting
        import time
        time.sleep(CONFIG['rate_limit_seconds'])

    def _parse_job(self, job_elem) -> Optional[Dict[str, str]]:
        """
        Extract job data from a job element.
        
        Args:
            job_elem: Playwright element object
            
        Returns:
            dict with job data or None if parsing fails
        """
        try:
            # Extract job data from element attributes and text
            job_id = job_elem.get_attribute('data-jk')
            job_url = job_elem.get_attribute('href')
            job_title_elem = job_elem.query_selector('[class*="JobTitle"]')
            job_title = job_title_elem.text_content() if job_title_elem else "Unknown"

            # TODO: Extract company, location, description from page
            # This requires inspecting Indeed's HTML structure more deeply

            job_data = {
                'source': 'indeed',
                'job_id': job_id,
                'job_title': job_title,
                'job_url': job_url,
                'company_name': 'TBD',  # Placeholder
                'location': 'Argentina',  # Default from ar.indeed.com
                'job_description': 'TBD',  # Placeholder
                'posted_date': None,
                'job_type': None,  # To be extracted from job page
                'scraped_date': datetime.now().date(),
            }
            return job_data

        except Exception as e:
            logger.error(f"Error parsing job element: {e}")
            return None

    def _save_job(self, job_data: Dict[str, str]) -> None:
        """
        Save job to database (skip if duplicate URL).
        
        Args:
            job_data: Job information dict
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO jobs 
                    (source, job_title, company_name, location, job_description, 
                     job_url, job_type, posted_date, scraped_date)
                    VALUES (:source, :job_title, :company_name, :location, :job_description,
                            :job_url, :job_type, :posted_date, :scraped_date)
                    ON CONFLICT DO NOTHING
                """), job_data)
                conn.commit()
        except Exception as e:
            logger.error(f"Database error saving job: {e}")
            self.errors.append({'type': 'database', 'error': str(e)})


def main():
    """Entry point: run scraper"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL not set in .env")
        return

    scraper = IndeedScraper(db_url)
    result = scraper.scrape()

    # Print summary
    print(f"\n{'='*50}")
    print(f"Scrape Summary")
    print(f"{'='*50}")
    print(f"Jobs scraped: {result['jobs_scraped']}")
    print(f"Errors: {result['errors_count']}")
    print(f"Duration: {result['duration_seconds']:.1f}s")
    if result['errors']:
        print(f"\nErrors: {result['errors']}")


if __name__ == '__main__':
    main()