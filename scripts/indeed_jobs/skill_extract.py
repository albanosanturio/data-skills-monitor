# Extract skills from job descriptions using regex, save to JSON, then load into job_skills table.
#
# POC approach: query live skills table, build regex from that. One source of truth.
#
# Two-step process:
#   1. skill_extract_regex_json() - reads unprocessed jobs, regex-extracts skills, writes JSON
#   2. skill_extract_to_db() - reads JSON, inserts into job_skills table, marks jobs as processed

import sys
import os
from pathlib import Path
import json
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

exports_dir = Path('data/exports/')


def get_db_engine():
    """Create and return SQLAlchemy engine from DATABASE_URL."""
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set (check your .env)")
    return create_engine(db_url)


def build_regex_from_db(engine):
    """Query live skills table and build a dynamic regex pattern.

    Returns:
        tuple: (compiled regex pattern, dict mapping skill_name -> skill_id)
    """
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT skill_id, skill_name
            FROM skills
            ORDER BY LENGTH(skill_name) DESC
        """))
        skills = result.fetchall()

    if not skills:
        logger.error("No skills found in skills table")
        return None, {}

    # Build mapping and escape skill names for regex
    skill_mapping = {}
    skill_mapping_lower = {} 
    escaped_skills = []

    for skill_id, skill_name in skills:
        skill_mapping[skill_name] = skill_id  # store original casing for later
        skill_mapping_lower[skill_name.lower()] = skill_name  # "r" -> "R"
        escaped_skills.append(re.escape(skill_name))

    # Build pattern: (skill1|skill2|skill3) with case-insensitive flag
    pattern_str = '|'.join(escaped_skills)
    pattern = re.compile(pattern_str, re.IGNORECASE)

    logger.info(f"Built regex pattern from {len(skills)} skills in DB")
    return pattern, skill_mapping, skill_mapping_lower


def skill_extract_regex_json():
    """Extract skills from unprocessed jobs using regex, write results to JSON.

    Reads live skills table, builds regex, extracts from unprocessed jobs.

    Returns:
        str: Path to the exported JSON file
    """
    engine = get_db_engine()
    pattern, skill_mapping, skill_mapping_lower = build_regex_from_db(engine)

    if not pattern:
        logger.error("Could not build regex pattern, aborting")
        return None

    # Query unprocessed jobs (skill_extraction_date IS NULL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT job_id, job_title, job_description
            FROM jobs
            WHERE skill_extraction_date IS NULL
            AND job_description IS NOT NULL
        """))
        unprocessed_jobs = result.fetchall()

    logger.info(f"Found {len(unprocessed_jobs)} unprocessed jobs")

    # Extract skills from each job description
    extraction_results = []

    for job_id, job_title, description in unprocessed_jobs:
        # Find all skill matches (case-insensitive)
        matches = pattern.finditer(description)

        # Deduplicate per job (track unique skill names)
        found_skills = set()

        for match in matches:
            matched_text = match.group()
            original_name = skill_mapping_lower.get(matched_text.lower(), matched_text)
            found_skills.add(original_name)  # Add "R" not "r"

        # Write each unique skill for this job to results
        for skill_name in found_skills:
            extraction_results.append({
                "job_id": str(job_id),
                "job_title": job_title,
                "skill_name": skill_name
            })

    # Write to JSON file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = exports_dir / f"skills_export_{timestamp}.json"

    exports_dir.mkdir(parents=True, exist_ok=True)
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(extraction_results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Extracted {len(extraction_results)} job-skill pairs from {len(unprocessed_jobs)} jobs")
    logger.info(f"✅ JSON exported: {json_filename}")

    return str(json_filename)


def skill_extract_to_db(json_path):
    """Read skills JSON export and insert into job_skills table, mark jobs as processed.

    Args:
        json_path: Path to the JSON file from skill_extract_regex_json()

    Returns:
        dict: {"inserted": int, "duplicates": int, "failed": int, "total": int}
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        extraction_results = json.load(f)

    logger.info(f"Loaded {len(extraction_results)} job-skill pairs from {json_path}")

    engine = get_db_engine()

    # Build skill_name -> skill_id mapping from DB (cache to avoid repeated queries)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT skill_name, skill_id FROM skills"))
        skill_name_to_id = {row[0]: row[1] for row in result.fetchall()}

    inserted = 0
    duplicates = 0
    failed = 0
    processed_job_ids = set()

    insert_sql = text("""
        INSERT INTO job_skills (job_id, skill_id, job_title, skill_name, extraction_method)
        VALUES (:job_id, :skill_id, :job_title, :skill_name, :extraction_method)
    """)

    with engine.connect() as conn:
        for entry in extraction_results:
            job_id = entry['job_id']
            skill_name = entry['skill_name']

            # Look up skill_id from cached mapping
            skill_id = skill_name_to_id.get(skill_name)
            if not skill_id:
                failed += 1
                logger.warning(f"Skill not found in DB: {skill_name}")
                continue

            try:
                with conn.begin():
                    result = conn.execute(insert_sql, {
                        'job_id': job_id,
                        'skill_id': skill_id,
                        'job_title': entry['job_title'],
                        'skill_name': entry['skill_name'],
                        'extraction_method': 'regex'
                    })
                    if result.rowcount:
                        inserted += 1
                        processed_job_ids.add(job_id)

            except Exception as e:
                # Unique constraint violation (job_id, skill_id) already exists
                if 'unique constraint' in str(e).lower():
                    duplicates += 1
                else:
                    failed += 1
                    logger.error(f"Failed to insert job_id={job_id}, skill={skill_name}: {e}")

    # Mark processed jobs as done (update skill_extraction_date)
    if processed_job_ids:
        with engine.connect() as conn:
            placeholders = ','.join([f"'{jid}'" for jid in processed_job_ids])
            update_sql = text(f"""
                UPDATE jobs
                SET skill_extraction_date = NOW()
                WHERE job_id IN ({placeholders})
            """)
            with conn.begin():
                conn.execute(update_sql)

        logger.info(f"Updated skill_extraction_date for {len(processed_job_ids)} jobs")

    summary = {
        "inserted": inserted,
        "duplicates": duplicates,
        "failed": failed,
        "total": len(extraction_results),
    }
    logger.info(f"Load complete: {summary}")
    return summary


def main():
    logger.info("Starting skill extraction pipeline...")

    # Step 1: Extract skills to JSON
    json_path = skill_extract_regex_json()
    if not json_path:
        logger.error("Skill extraction failed, aborting")
        return

    # Step 2: Load JSON into DB
    summary = skill_extract_to_db(json_path)
    logger.info(f"Pipeline complete: {summary}")


if __name__ == "__main__":
    main()