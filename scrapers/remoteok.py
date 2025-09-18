
import logging
import json

logger = logging.getLogger(__name__)

async def scrape(response_text: str, selectors: dict):
    """
    Scrapes job postings from the JSON response of the remoteok.com API.

    Args:
        response_text (str): The JSON string from the API response.
        selectors (dict): The configuration from selectors.py (not used here but kept for consistency).

    Returns:
        list: A list of dictionaries, where each dictionary represents a job.
    """
    jobs = []
    
    try:
        # The first item in the response is a legal notice, so we skip it.
        data = json.loads(response_text)[1:] 
    except (json.JSONDecodeError, IndexError):
        logger.error("Failed to decode JSON from RemoteOK or the response was empty.")
        return []

    for job_data in data:
        # Use .get() for safety in case a key is missing
        if not all([job_data.get('id'), job_data.get('position'), job_data.get('url')]):
            continue

        job = {
            "id": f"remoteok_{job_data.get('id')}",
            "title": job_data.get('position'),
            "company": job_data.get('company'),
            "link": job_data.get('url'),
            "source": "RemoteOK (API)"
        }
        jobs.append(job)

    logger.info(f"Scraped {len(jobs)} jobs from RemoteOK API.")
    return jobs