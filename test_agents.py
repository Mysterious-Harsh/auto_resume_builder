from tests.test_indexing import run_indexing_test
from tests.test_analysis_agent import run_analysis_test

from tests.test_rephrasing_agent import run_rephrasing_test
from tests.test_scraper_agent import run_scraper_test

from tests.test_pdf_agent import run_pdf_agent_test

if __name__ == "__main__":
    # run_scraper_test()
    # run_indexing_test()
    # run_analysis_test()
    # run_rephrasing_test()
    run_pdf_agent_test()
