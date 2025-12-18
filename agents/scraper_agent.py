# auto_resume_builder/agents/scraper_agent.py

import requests
from bs4 import BeautifulSoup
import time
import random
import sys
from typing import Optional

# --- NEW IMPORTS for Headless Scraping ---
try:
    from playwright.sync_api import (
        sync_playwright,
        TimeoutError as PlaywrightTimeoutError,
    )

    # Import the Stealth Plugin from the installed package
    from playwright_stealth import Stealth
except ImportError:
    # Set a flag if Playwright is not installed
    PLAYWRIGHT_AVAILABLE = False

    class MockPlaywrightError(Exception):
        pass

    TimeoutError = MockPlaywrightError
    PlaywrightError = MockPlaywrightError
else:
    PLAYWRIGHT_AVAILABLE = True

# Import core configurations using the absolute path
try:
    from core.config import DEFAULT_SCRAPER_TIMEOUT
except ImportError:
    print("FATAL ERROR: Could not import core modules in Scraper Agent.")
    sys.exit(1)

# --- Common Scraper Configurations ---
USER_AGENTS = [
    # Using more modern, less suspicious user agents
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]
DEFAULT_SCRAPER_TIMEOUT = 15  # Time in seconds

# --- Helper Functions ---


def get_random_headers() -> dict:
    """Returns a dictionary with a random User-Agent to mimic a real browser."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }


def clean_html_to_text(html_content: str) -> str:
    """Uses BeautifulSoup to remove HTML tags and extract clean, readable text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove common irrelevant elements (scripts, styles, header/footer boilerplate)
    for element in soup(["script", "style", "header", "footer", "nav", ".sidebar"]):
        element.decompose()

    # Get text and clean up excess whitespace/newlines
    text = soup.get_text(separator=" ", strip=True)
    return text


# --- Headless Scraper Function ---


# REVISED scrape_with_playwright function in scraper_agent.py


def scrape_with_playwright(job_url: str) -> Optional[str]:
    """
    Uses a headless browser (Playwright) with stealth enhancements to render the page.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed. Dynamic scraping skipped.")
        return None

    print("--- Initiating Dynamic (Playwright) Fallback with Stealth Enhancements ---")

    # Use standard sync_playwright() context manager
    with sync_playwright() as p:
        browser = None
        try:
            # Launch Options: Chromium is often the most stable with stealth
            browser = p.chromium.launch(headless=True)

            # Context Options: Apply random user agent and mimic real screen
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1400, "height": 900},
            )

            # --- CRITICAL CHANGE 1: Apply Stealth Patches to the Context ---
            Stealth().apply_stealth_sync(context)

            page = context.new_page()

            # 1. Go to the page using a DOM content strategy
            page.goto(
                job_url, timeout=30000, wait_until="domcontentloaded"  # 30 seconds
            )

            # --- CRITICAL CHANGE 2: Wait for Cloudflare Challenge to potentially resolve ---

            # Check if the page is still showing a Cloudflare challenge (look for specific text)
            page_content = page.content()
            if (
                "Just a moment..." in page_content
                or "Additional Verification Required" in page_content
            ):
                print(
                    "   ⚠️ Bot Challenge detected. Waiting for 10 seconds for"
                    " resolution..."
                )

                # Introduce a longer, mandatory wait for the JS challenge to run
                time.sleep(10)

                # OPTIONAL: Simulate human-like interaction (scroll)
                page.mouse.wheel(0, random.randint(100, 300))
                time.sleep(random.uniform(1, 2))

                # Force a reload or wait for network idle after the challenge might have resolved
                page.wait_for_load_state("networkidle", timeout=15000)

            # 2. Wait for the specific Job Description content
            try:
                # Wait for the main job content container
                # (This selector is reliable for Indeed job posts)
                page.wait_for_selector('div[data-testid="job-details"]', timeout=10000)
            except PlaywrightTimeoutError:
                print(
                    "   Warning: Job details selector not found after challenge wait,"
                    " proceeding after short delay."
                )

            # 3. Final Delay: A short, mandatory human-like delay before extraction
            time.sleep(random.uniform(2, 4))

            # 4. Extraction
            html_content = page.content()

            # --- Assuming clean_html_to_text is defined elsewhere ---
            # NOTE: You must ensure the clean_html_to_text function is robust.
            job_description = clean_html_to_text(html_content)

            if len(job_description) > 500 and "job-details" in html_content:
                print(f"✅ Dynamic fetch successful. JD length: {len(job_description)}")
                return job_description

            if "job-details" not in html_content:
                print(
                    "❌ Dynamic fetch failed: Could not locate job description content."
                )
                return None

        # --- EXCEPTION HANDLING REMAINS THE SAME ---
        except PlaywrightTimeoutError as e:
            print(
                "❌ Playwright TimeoutError: Page did not load/content was not"
                f" ready. {e}"
            )
            return None
        except Exception as e:
            print(f"❌ Unexpected Error in Playwright block: {e}")
            return None
        finally:
            if browser:
                browser.close()

    return None


def scraper_agent(job_url: str) -> Optional[str]:
    """
    Tries static scraping first, then falls back to headless dynamic scraping.
    """
    print(f"\n--- Scraper Agent: Attempting to fetch URL: {job_url} ---")

    # 1. INITIAL STATIC ATTEMPT (Fastest method)
    for attempt in range(2):  # Reduced retries, prioritizing the faster fallback
        try:
            headers = get_random_headers()
            response = requests.get(
                job_url,
                headers=headers,
                timeout=DEFAULT_SCRAPER_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()

            job_description = clean_html_to_text(response.text)

            if len(job_description) > 500:
                print(f"✅ Static fetch successful on attempt {attempt + 1}.")
                return job_description

        except requests.exceptions.HTTPError as e:
            print(
                f"❌ HTTP Error ({e.response.status_code}) on static attempt"
                f" {attempt + 1}."
            )
            if e.response.status_code in [403, 429]:
                print(
                    "   Server blocked request (403/429). Proceeding to dynamic"
                    " fallback."
                )
                break  # Exit the loop immediately
            time.sleep(random.uniform(2, 5))

        except requests.exceptions.RequestException as e:
            print(f"❌ Network/Timeout Error on static attempt {attempt + 1}: {e}")
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"❌ Unexpected Error during static attempt {attempt + 1}: {e}")
            time.sleep(random.uniform(1, 3))

    # 2. DYNAMIC FALLBACK (Only runs if static attempts failed/were blocked)
    return scrape_with_playwright(job_url)


if __name__ == "__main__":
    # --- Example Usage ---
    # NOTE: Use a URL that you know uses JavaScript to render content for a full test.
    # EXAMPLE_DYNAMIC_URL = "https://www.indeed.com/viewjob?jk=..."
    # EXAMPLE_STATIC_URL = "https://www.msft.com/..."

    # Test with a placeholder URL
    test_url = "https://example.com"
    content = scraper_agent(test_url)

    if content:
        print("\nSuccessfully retrieved content (first 200 chars):")
        print("--------------------------------------------------")
        print(content[:200] + "...")
    else:
        print("\nFinal failure: Could not reliably fetch the job description.")
