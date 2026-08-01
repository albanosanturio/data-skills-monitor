
#TEMPLATE

import logging
import os
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

raw_files_path = 'test_data/raw_html/'
processed_files_path = 'test_data/processed_html/'
processed_dir = Path(processed_files_path)

def read_file(filepath):
    """Read HTML file and return content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        logger.info(f"Read: {filepath.name}")
        return html
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return None


def read_parse_html(filepath):
    """Read HTML file and extract job data
    
    Args:
        filepath: Path to HTML file (e.g., Path('data/raw_html/jobs_2026-07-30/job_2e13383963c495ed.html'))
    
    Returns:
        dict: Job data with fields: source, job_title, company_name, location, job_url, job_description, posted_date, job_type
    """
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        logger.info(f"Read: {filepath.name}")
        
        # Extract job_id from filename for URL
        job_id = filepath.name.replace('job_', '').replace('.html', '')
        job_url = f"https://indeed.com/viewjob?jk={job_id}"
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find description
        desc_tag = soup.find('div', id='jobDescriptionText')
        desc = desc_tag.get_text(strip=True) if desc_tag else None
 
        # Find title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else None
 
        # Find company (in meta or header)
        company_elem = soup.find('a', {'data-company-name': 'true'})
        company = company_elem.text.strip() if company_elem else None
 
        # Find location
        location_elem = soup.find('div', {'data-testid': 'inlineHeader-companyLocation'})
        location = location_elem.text.strip() if location_elem else None
 
        job_data = {
            'source': 'indeed',
            'job_title': title,
            'company_name': company,
            'location': location,
            'job_url': job_url,
            'job_description': desc,
            'posted_date': None,
            'job_type': None,
        }
 
        logger.info(f"Parsed: {title} at {company}")
        print(job_data)
        return job_data
 
    except Exception as e:
        logger.error(f"Error parsing HTML {filepath.name}: {e}")
        return None


def insert_to_db(jobs_list,db_url):
    print(f"URL: {db_url}")
    print(f"Type: {type(db_url)}")
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    print(f" Engine created: {engine}")

    try:
        print("Attempting to connect...")
        with engine.connect() as conn:
            for job in jobs_list:
                insert_sql = text("""
                    INSERT INTO jobs (source, job_title, company_name, location, job_url, job_description, scraped_date)
                    VALUES (:source, :job_title, :company_name, :location, :job_url, :job_description, :scraped_date)
                    ON CONFLICT (job_url) DO NOTHING
                """)
                job['scraped_date'] = datetime.now().date()
                conn.execute(insert_sql, job)

            conn.commit()
            logger.info(f"Inserted {len(jobs_list)} jobs")

    except Exception as e:
        logger.error(f"Error inserting to DB: {e}")


def move_to_processed(html_files):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    processed_dir = Path(processed_files_path) / timestamp
    processed_dir.mkdir(parents=True, exist_ok=True)
    try:
        for filepath in html_files:
            dest = processed_dir / filepath.name
            filepath.rename(dest)
            logger.info(f"Moved: {filepath.name} → processed/")
        
        logger.info(f"Moved {len(html_files)} files to processed")
    except Exception as e:
        logger.error(f"Error moving files: {e}")
    """Move file to processed folder"""
    pass


def get_html_files():
    """Get all HTML files from raw folder"""
    pass


def process_job_html(filepath):
    """Parse HTML, extract data, insert to DB"""
    try:
        job_data = read_parse_html(filepath)
        insert_to_db(job_data)
        move_to_processed(filepath)
        return True
    except Exception as e:
        logger.error(f"Failed {filepath}: {e}")
        return False


if __name__ == "__main__":
    for file in get_html_files():
        process_job_html(file)

# Main loop
# for file in get_html_files():
#     process_job_html(file)