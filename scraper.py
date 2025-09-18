# job_alert_bot/scraper.py (MODIFIED)

import httpx
import asyncio
import logging
import importlib
import pkgutil
import urllib.parse
from config import HTTP_HEADERS
from cssselectors import SELECTORS
import scrapers
import database as db # Import the database
from config import LOGGING_LEVEL

# Convert string to logging level constant
level = getattr(logging, LOGGING_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def fetch_html(url: str) -> str | None:
    # ... (this function remains the same) ...
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=15.0)
            response.raise_for_status()
            return response.text
        except httpx.RequestError as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None

async def scrape_all_sites():
    """
    Dynamically discovers and runs scrapers for each unique keyword.
    """
    logger.info("Starting dynamic scraping process...")
    unique_keywords = await db.get_all_unique_keywords()
    
    if not unique_keywords:
        logger.info("No keywords to scrape for. Aborting.")
        return []

    logger.info(f"Found unique keywords to search for: {unique_keywords}")
    
    all_jobs = []
    processed_job_ids = set() # To avoid duplicate jobs from different keyword searches

    tasks = []
    scraper_modules = {name: importlib.import_module(f"scrapers.{name}") for _, name, _ in pkgutil.iter_modules(scrapers.__path__)}

    for site_name, selectors in SELECTORS.items():
        if site_name not in scraper_modules:
            continue
            
        for keyword in unique_keywords:
            # URL-encode the keyword to handle spaces, e.g., "Data Entry" -> "Data%20Entry"
            safe_keyword = urllib.parse.quote_plus(keyword)
            url = selectors['url'].format(keyword=safe_keyword)
            
            # Add a task to run the scraper for this specific site and keyword
            tasks.append(run_scraper(site_name, scraper_modules[site_name], selectors, url))

    # Gather results from all scraping tasks
    results = await asyncio.gather(*tasks)
    
    for job_list in results:
        if job_list:
            for job in job_list:
                # Add job only if we haven't processed it before
                if job['id'] not in processed_job_ids:
                    all_jobs.append(job)
                    processed_job_ids.add(job['id'])
            
    logger.info(f"Total unique jobs scraped from all sites: {len(all_jobs)}")
    return all_jobs

async def run_scraper(site_name: str, module, selectors: dict, url: str):
    """
    Runs a specific scraper module for a given URL, handling both HTML and API types.
    """
    try:
        logger.info(f"Scraping {site_name} for URL: {url}")
        
        # Fetch the raw text content (could be HTML or JSON)
        response_text = await fetch_html(url)
        if not response_text:
            logger.error(f"Failed to fetch content for {url}. Aborting scrape for this URL.")
            return None
        
        # Check the 'type' and call the scraper accordingly
        scraper_type = selectors.get("type", "html") # Default to 'html' if not specified

        if scraper_type == "api":
            # For APIs, we pass the raw JSON text directly
            jobs = await module.scrape(response_text, selectors)
        else:
            # For HTML, we need to import BeautifulSoup here
            from bs4 import BeautifulSoup
            
            # This is the old logic, now inside a condition
            soup = BeautifulSoup(response_text, 'html.parser')
            jobs = []
            
            job_cards = soup.select(selectors['job_card'])
            if not job_cards:
                 logger.warning(f"No job cards found for {site_name}. Check HTML structure or selectors.")
                 return []
            
            # We need to re-implement the parsing logic here or, even better,
            # refactor the HTML scrapers to accept the BeautifulSoup object.
            # For simplicity, let's just pass the raw HTML and let the scraper parse it.
            jobs = await module.scrape(response_text, selectors)

        return jobs
    except Exception as e:
        logger.error(f"An unexpected error occurred in scraper '{site_name}' for URL {url}: {e}", exc_info=True)
    return None