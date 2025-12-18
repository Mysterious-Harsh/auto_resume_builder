# test_analysis_agent.py

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

try:
    from agents.analysis_agent import job_analysis_agent
    from core.data_models import JobRequirements
except ImportError as e:
    print(f"FATAL ERROR during import: {e}")
    print("Ensure you have set up the absolute imports in test_analysis_agent.py.")
    sys.exit(1)

# --- SAMPLE INPUT DATA ---
SAMPLE_JOB_DESCRIPTION = """
We are hiring a Senior Data Scientist in Toronto specializing in Natural Language Processing (NLP) 
and large-scale cloud deployments. Must have 5+ years of experience with Python, PyTorch, 
and deploying models on Azure ML. Responsibilities include mentoring junior staff, optimizing 
data processing pipelines (using Spark/Databricks), and presenting findings to executive stakeholders. 
Familiarity with financial data is a major plus.
"""


def run_analysis_test():
    """Tests the Job Analysis Agent's ability to extract structured requirements."""

    print("\n--- Running Job Analysis Agent Test ---")

    if not os.getenv("GEMINI_API_KEY"):
        print("Test Skipped: GEMINI_API_KEY not found.")
        return

    # Execute the agent
    requirements = job_analysis_agent(
        SAMPLE_JOB_DESCRIPTION,
        model_to_use={"llm_provider": "ollama", "llm_name": "qwen3:14b"},
    )

    if requirements and isinstance(requirements, JobRequirements):
        print("\n✅ SUCCESS: Analysis Agent returned structured data.")
        print(f"   Target Role: {requirements.target_role}")
        print(f"   Must-Have Skills: {', '.join(requirements.must_have_skills)}")
        print(
            "   Core Responsibilities (partial):"
            f" {requirements.core_responsibilities[0]}..."
        )

        # Further check to ensure the output is the correct Pydantic type
        assert (
            requirements.target_role == "Senior Data Scientist"
            or "Senior Data Scientist" in requirements.target_role
        )
    else:
        print(
            "\n❌ FAILURE: Analysis Agent failed to return a valid JobRequirements"
            " object."
        )


if __name__ == "__main__":
    run_analysis_test()
