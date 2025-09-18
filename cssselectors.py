# job_alert_bot/selectors.py (MODIFIED for RemoteOK)

SELECTORS = {
    "remoteok": {
        "type": "api",  # <-- Add this type flag
        "url": "https://remoteok.com/api", # <-- This is the API endpoint
        # The CSS selectors below are no longer needed for this scraper
        # "job_card": "tr.job",
        # "title": "h2[itemprop='title']",
        # "company": "h3[itemprop='name']",
        # "link": "a.preventLink",
        # "id_attribute": "data-id"
    },
    "weworkremotely": {
        "type": "html", # <-- Specify that this one is still HTML
        "url": "https://weworkremotely.com/remote-jobs/search?term={keyword}",
        "job_card": "li.feature",
        "title": "span.title",
        "company": "span.company",
        "link": "a[href*='/remote-jobs/']",
        "id_attribute": "id"
    }
}