SELECTORS = {
    "remoteok": {
        "type": "api", 
        "url": "https://remoteok.com/api",
        # The CSS selectors below are no longer needed for this scraper
        # "job_card": "tr.job",
        # "title": "h2[itemprop='title']",
        # "company": "h3[itemprop='name']",
        # "link": "a.preventLink",
        # "id_attribute": "data-id"
    },
    "weworkremotely": {
        "type": "html",
        "url": "https://weworkremotely.com/remote-jobs/search?term={keyword}",
        "job_card": "li.feature",
        "title": "span.title",
        "company": "span.company",
        "link": "a[href*='/remote-jobs/']",
        "id_attribute": "id"
    }
}