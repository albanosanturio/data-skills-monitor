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
from src.indeed_jobs.utils import  move_to_processed, read_parse_html_file, read_parse_folder, write_json_export

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this is for db - move to db script
# load_dotenv()
# db_url = os.getenv("DATABASE_URL")
# print(f"URL: {db_url}")
# print(f"Type: {type(db_url)}")


# Declare file paths to use
raw_dir = Path('data/raw/')
processed_dir = Path('test_data/processed_html/')

# Parse all the html files in raw_dir path
jobs_dict_list = read_parse_folder(raw_dir)

# Timestamp used for json and for processed time
timestamp_process = datetime.now().strftime('%Y%m%d_%H%M%S')

# Write to file
write_json_export(jobs_dict_list, timestamp_process)

# Moving files to processed directory
move_to_processed(raw_dir, timestamp_process)