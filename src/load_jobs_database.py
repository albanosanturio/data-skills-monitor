#imports
import re
import json
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
raw_dir = Path(raw_files_path)
processed_files_path = 'test_data/processed_html/'
processed_dir = Path(processed_files_path)

#db connection
#load_dotenv()
#db_url = os.getenv("DATABASE_URL")

def read_file(filepath):
    """Read HTML file and return content"""
    """Deprecated and integrated in read_parse_html()"""
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

def read_parse_html2(filepath):
    """Read HTML file and extract job data from JSON-LD
    
    Args:
        filepath: Path to HTML file
    
    Returns:
        dict: Job data with all extracted fields
    """
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        logger.info(f"Read: {filepath.name}")
        
        # Extract JSON-LD (more reliable than DOM parsing)
        json_ld_match = re.search(r'<script type="application/ld\+json">({.*?})</script>', html, re.DOTALL)
        
        if not json_ld_match:
            logger.error(f"No JSON-LD found in {filepath.name}")
            return None
        
        # Parse JSON-LD
        try:
            job_json = json.loads(json_ld_match.group(1))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON-LD in {filepath.name}: {e}")
            return None
        
        # Extract country from URL or address
        country = job_json.get('jobLocation', {}).get('address', {}).get('addressCountry')
        
        # Extract posted date
        posted_date_str = job_json.get('datePosted')
        posted_date = None
        if posted_date_str:
            try:
                posted_date = datetime.fromisoformat(posted_date_str.replace('Z', '+00:00')).isoformat()
            except:
                posted_date = posted_date_str
        
        # Build job_url with country if available
        job_id = filepath.name.replace('job_', '').replace('.html', '')

        # Extract job_id from filename (handle both formats)
        filename = filepath.name.replace('.html', '')


        # Try to extract 'jk' parameter if it's a SingleFile URL-encoded filename
        jk_match = re.search(r'jk=([a-f0-9]+)', filename)
        if jk_match:
            job_id = jk_match.group(1)
        else:
            # Fallback for old format (job_XXXXX)
            job_id = filename.replace('job_', '')

        if country:
            job_url = f"https://{country.lower()}.indeed.com/viewjob?jk={job_id}"
        else:
            job_url = f"https://indeed.com/viewjob?jk={job_id}"
        
        # Parse description (unescape HTML entities)
        description_html = job_json.get('description', '')
        # Clean HTML
        if description_html:
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator=' ', strip=True)
        else:
            description_text = None
            #description_text = job_json.get('description')  # Use text field if available
        
        job_data = {
            'source': 'indeed',
            'job_id': job_id,
            'country': country,
            'job_title': job_json.get('title'),
            'company_name': job_json.get('hiringOrganization', {}).get('name'),
            'job_url': job_url,
            'job_description': description_text,
            'posted_date': posted_date,
        }
        
        logger.info(f"Parsed: {job_data['job_title']} at {job_data['company_name']} ({country})")
        return job_data
    
    except Exception as e:
        logger.error(f"Error parsing {filepath.name}: {e}")
        return None


def insert_to_db(jobs_list):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    print(f"URL: {db_url}")

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
    raw_dir = Path(raw_files_path)
    html_files = list(raw_dir.glob("*.html"))
    #db_url = os.getenv("DATABASE_URL")
    
    jobs_dict_list = []
    for filepath in html_files:
        job_data = read_parse_html(filepath)
        if job_data:
            jobs_dict_list.append(job_data)
    insert_to_db(jobs_dict_list)
    move_to_processed(html_files)
    
    logger.info("Pipeline complete!")

# Main loop
# for file in get_html_files():
#     process_job_html(file)