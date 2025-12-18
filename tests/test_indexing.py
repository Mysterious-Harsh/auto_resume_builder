# test_indexing.py

import os
import json
from dotenv import load_dotenv

# We need to explicitly set the Python path so we can import modules
# from the 'auto_resume_builder' package structure correctly.
# import sys

# project_root = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(project_root, "auto_resume_builder"))

# Import the specific functions needed for testing
from agents.indexing_agent import (
    index_master_background,
    query_chroma_for_relevance,
)
from core.config import MASTER_BACKGROUND_FILE, CHROMA_COLLECTION_NAME, CHROMA_DB_PATH
from core.data_models import JobRequirements


# --- SETUP ---
def setup_test_environment():
    """Sets up the test environment by loading necessary configurations."""

    # 1. Load environment variables from .env
    load_dotenv()
    print("os.getenv('GEMINI_API_KEY'):", os.getenv("GEMINI_API_KEY"))
    if not os.getenv("GEMINI_API_KEY"):
        raise EnvironmentError(
            "GEMINI_API_KEY not found. Please set it in your .env file."
        )


# 2. Load the master JSON data
try:
    with open(MASTER_BACKGROUND_FILE, "r") as f:
        master_data = json.load(f)
except FileNotFoundError:
    print(
        f"Error: Master background file not found at {MASTER_BACKGROUND_FILE}. Please"
        " create it."
    )
    master_data = None

# 3. Create a test JobRequirements object for querying
TEST_JOB_REQ = JobRequirements(
    target_role="AI/ML Specialist",
    must_have_skills=["NLP", "Python", "TensorFlow"],
    nice_to_have_skills=["Docker", "Kubernetes"],
    keywords_and_phrases=[
        "multi-agent system",
        "GitHub Actions",
        "data validation",
        "speech recognition",
    ],
    core_responsibilities=["present insights", "optimize database queries"],
)


def run_indexing_test():
    """Runs the indexing and a basic query test."""
    if master_data is None:
        return

    print("--- STARTING INDEXING TEST ---")
    # if os.path.exists(CHROMA_DB_PATH):
    #     print(
    #         f"ChromaDB path '{CHROMA_DB_PATH}' already exists. Skipping indexing test."
    #     )
    # else:
    # --- A. Test Indexing ---
    print("\n[TEST STEP A: INDEXING]")

    # index_master_background(master_data, client="ollama")

    # To verify, you could check the persistence directory
    # The ChromaDB files should now exist in ./auto_resume_builder/data/chroma_data

    # --- B. Test Querying (Semantic Search) ---
    print("\n[TEST STEP B: QUERYING]")

    # Call the query function from the indexing agent
    relevant_results = query_chroma_for_relevance(
        TEST_JOB_REQ, top_k=100, client="ollama"
    )

    if relevant_results:
        print("\nSUCCESS: Query returned relevant documents. Top 5 results:")
        for i, item in enumerate(relevant_results):
            print(
                f"  {i+1}. [Score: {item['relevance_score']:.2f}]"
                f" ({item['metadata']['source_id']}:{item['metadata']['type']}:"
                f" {item['metadata']['title']}) - {item['bullet_point'][:80]}..."
            )
    else:
        print("\nFAILURE: Query returned no results or an error occurred.")


if __name__ == "__main__":
    setup_test_environment()
    run_indexing_test()
