# In your main execution script (e.g., main.py or test_main.py):

# ... imports ...
from agents.scraper_agent import scraper_agent


# ...
def run_scraper_test():
    JOB_POSTING_URL = (
        "https://ca.indeed.com/viewjob?jk=7fb0e3648215b251&from=shareddesktop_copy"
    )

    raw_job_description = scraper_agent(JOB_POSTING_URL)

    if raw_job_description:
        # Pass the fetched text to the Analysis Agent
        print(raw_job_description)
        # ... continue workflow ...
    else:
        print("FATAL: Could not fetch Job Description. Terminating process.")
