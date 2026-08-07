# Read the input folder, parse the jobs, create a json and move the input files to processed

import sys
from pathlib import Path
import os
import json
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.indeed_jobs.utils import  insert_to_db, move_to_processed, read_parse_html_file, read_parse_folder, write_json_export

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this is for db - move to db script
# load_dotenv()
# db_url = os.getenv("DATABASE_URL")
# print(f"URL: {db_url}")
# print(f"Type: {type(db_url)}")


# Declare file paths to use
raw_files_path = 'html_manual/'
raw_dir = Path(raw_files_path)
processed_files_path = 'test_data/processed_html/'
processed_dir = Path(processed_files_path)


jobs_dict_list = []  # init an empty list to store results before saving
seen_job_ids = set() # this set helps track duplicates

# Read and parse all the files in html_files path, and append to list


# for filepath in html_files:
#     job_data = read_parse_html_file(filepath)
#     if job_data:
#         job_id = job_data['job_id']
#         # Skip if already seen
#         if job_id in seen_job_ids:
#             logger.warning(f"Duplicate job_id: {job_id} (skipping {filepath.name})")
#             continue
# 
#         seen_job_ids.add(job_id)
#         jobs_dict_list.append(job_data)

jobs_dict_list, total_htmls, repeated_htmls = read_parse_folder(raw_dir)


# Printing the urls processed just to check
print("urls processed:")
for jobs in jobs_dict_list: print(jobs['job_url'], jobs['job_title'])
print("# of htmls processed: ", total_htmls)
print("# of jobs saved in json: ",len(jobs_dict_list))
print("# of repeated jobs: ", repeated_htmls)

# Timestamp used for json and for processed time
timestamp_process = datetime.now().strftime('%Y%m%d_%H%M%S')

# Write to file
write_json_export(jobs_dict_list, timestamp_process)

# Moving files to processed directory
move_to_processed(raw_dir, timestamp_process)