#imports
import re
import os
import json
import logging
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


def read_parse_html_file(filepath):
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

def read_parse_folder(folder_path):

    html_files_list = list(folder_path.glob("*.html"))
    jobs_dict_list = []  # init an empty list to store results before saving
    seen_job_ids = set() # this set helps track duplicates
    duplicates = 0
    failed = 0

    for single_html_path in html_files_list:
        try:
            job_data = read_parse_html_file(single_html_path)

            if not job_data:
                failed +=1
                logger.warning(f"Duplicate job_id: {job_id} (skipping {single_html_path.name})")
                continue


            if job_data:
                job_id = job_data['job_id']

                # Skip if already seen
                if job_id in seen_job_ids:
                    duplicates +=1
                    continue

                seen_job_ids.add(job_id)
                jobs_dict_list.append(job_data)

        except Exception as e:
            failed += 1
            logger.error(f"Failed to parse {single_html_path.name}: {e}")
           
    print("# of htmls processed: ", len(html_files_list))
    print("# of jobs saved in json: ",len(jobs_dict_list))
    print("# of repeated jobs: ", duplicates)
    print("# of failed jobs: ", failed)
        
    return jobs_dict_list


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

def write_json_export(jobs_dict_list, timestamp):# Write to file
    json_filename = f"data/exports/jobs_export_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(jobs_dict_list, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON exported: {json_filename}")

def move_to_processed(folder_path, timestamp):
    html_files_list = list(folder_path.glob("*.html"))
    processed_dir = Path('data/processed/') / timestamp
    processed_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    failed = []
    
    for filepath in html_files_list:
        try:
            dest = processed_dir / filepath.name
            filepath.rename(dest)
            moved += 1
        except Exception as e:
            logger.error(f"Failed to move {filepath.name}: {e}")
            failed.append(filepath.name)
    
    logger.info(f"Moved {moved}/{len(html_files_list)} files to {processed_dir}")
    if failed:
        logger.warning(f"Failed to move: {failed}")

    print("moved ",moved," files")
    print("failed to move ",len(failed)," files")
    return None



if __name__ == "__main__":
    raw_dir = Path(raw_files_path)
    html_files_list = list(raw_dir.glob("*.html"))
    #db_url = os.getenv("DATABASE_URL")
    
    jobs_dict_list = []
    for filepath in html_files_list:
        job_data = read_parse_html(filepath)
        if job_data:
            jobs_dict_list.append(job_data)
    insert_to_db(jobs_dict_list)
    move_to_processed(html_files_list)
    
    logger.info("Pipeline complete!")

