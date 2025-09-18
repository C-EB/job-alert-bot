# job_alert_bot/scrapers/wework.py

import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

async def scrape(html: str, selectors: dict):
    """
    Scrapes job postings from the HTML content of weworkremotely.com.

    Args:
        html (str): The HTML content of the job board page.
        selectors (dict): A dictionary of CSS selectors for parsing.

    Returns:
        list: A list of dictionaries, where each dictionary represents a job.
    """
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []

    job_cards = soup.select(selectors['job_card'])

    if not job_cards:
        logger.warning("No job cards found for WeWorkRemotely. Check selectors.")
        return []

    for card in job_cards:
        job_id = card.get(selectors['id_attribute'])
        title_element = card.select_one(selectors['title'])
        company_element = card.select_one(selectors['company'])
        
        # WeWorkRemotely has multiple links, we want the main job link
        link_elements = card.find_all('a', href=True)
        job_link = None
        for a in link_elements:
            if '/remote-jobs/' in a['href']:
                job_link = a['href']
                break
        
        if not all([job_id, title_element, company_element, job_link]):
            logger.debug(f"Skipping a card on WeWorkRemotely, missing required elements.")
            continue
            
        link = f"https://weworkremotely.com{job_link}"

        job = {
            "id": f"wework_{job_id}", # Prefix for uniqueness
            "title": title_element.text.strip(),
            "company": company_element.text.strip(),
            "link": link,
            "source": "WeWorkRemotely"
        }
        jobs.append(job)
        
    logger.info(f"Scraped {len(jobs)} jobs from WeWorkRemotely.")
    return jobs