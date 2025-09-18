# job_alert_bot/test_scraper_simple.py

import asyncio
import logging
import importlib
import pkgutil
import urllib.parse

# --- CORE IMPORTS FROM YOUR PROJECT ---
from scraper import run_scraper # We will use the 'run_scraper' function directly
from cssselectors import SELECTORS
import scrapers # This is the package in the 'scrapers/' folder
from config import LOGGING_LEVEL
# --- CONFIGURATION FOR THIS TEST ---
# Add any keywords you want to test here
KEYWORDS_TO_TEST = ["Python", "JavaScript", "Go"]

# --- Basic Logging ---


# Convert string to logging level constant
level = getattr(logging, LOGGING_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """
    A simple, direct test of the scraping mechanism for a fixed list of keywords.
    This test DOES NOT use or interact with the database.
    """
    logger.info("--- Starting SIMPLE Scraper Test ---")
    logger.info(f"Testing with keywords: {KEYWORDS_TO_TEST}")
    
    all_jobs = []
    processed_job_ids = set() # To prevent showing duplicate jobs
    tasks = []

    # Dynamically load all scraper modules from the 'scrapers/' folder
    scraper_modules = {
        name: importlib.import_module(f"scrapers.{name}")
        for _, name, _ in pkgutil.iter_modules(scrapers.__path__)
    }

    # Loop through each website defined in your selectors
    for site_name, selectors in SELECTORS.items():
        if site_name not in scraper_modules:
            logger.warning(f"No scraper module found for '{site_name}', skipping.")
            continue
            
        # For each website, loop through our test keywords
        for keyword in KEYWORDS_TO_TEST:
            # Prepare the URL for the search
            safe_keyword = urllib.parse.quote_plus(keyword)
            url = selectors['url'].format(keyword=safe_keyword)
            
            # Create a task to scrape that specific URL
            module = scraper_modules[site_name]
            tasks.append(run_scraper(site_name, module, selectors, url))

    # Run all the scraping tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Process the results
    for job_list in results:
        if job_list:
            for job in job_list:
                if job['id'] not in processed_job_ids:
                    all_jobs.append(job)
                    processed_job_ids.add(job['id'])

    # --- Display the results ---
    if all_jobs:
        logger.info(f"\n[SUCCESS] Found a total of {len(all_jobs)} unique jobs.")
        logger.info("--- First 5 Jobs Found ---")
        for i, job in enumerate(all_jobs[:5]):
            print(f"  Job {i+1}:")
            print(f"    Title: {job['title']}")
            print(f"    Company: {job['company']}")
            print(f"    Source: {job['source']}")
            print(f"    Link: {job['link']}")
    else:
        logger.warning("\n[INFO] No jobs were found.")

    logger.info("\n--- SIMPLE Scraper Test Finished ---")


if __name__ == "__main__":
    asyncio.run(main())