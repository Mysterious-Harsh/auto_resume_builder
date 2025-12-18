# test_rephrasing_agent.py

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

try:
    from agents.rephrasing_agent import resume_rephrasing_agent
    from core.data_models import (
        JobRequirements,
        FilteredResumeContent,
        FilteredBulletPoint,
        MetaData,
    )
except ImportError as e:
    print(f"FATAL ERROR during import: {e}")
    print("Ensure you have set up the absolute imports in test_rephrasing_agent.py.")
    sys.exit(1)


# --- SIMULATED INPUT DATA ---

# A. Requirements (what the JD asked for)
TEST_REQ = JobRequirements(
    target_role="AI/ML Specialist",
    must_have_skills=["NLP", "Python", "TensorFlow", "PostgreSQL"],
    nice_to_have_skills=["Docker", "Kubernetes"],
    keywords_and_phrases=["multi-agent system", "GitHub Actions", "data validation"],
    core_responsibilities=["present insights", "optimize database queries"],
)

# B. Raw Relevant Bullets (what the Vector DB returned)
# These need to be rewritten to incorporate the keywords from TEST_REQ
TOP_RELEVANT_BULLETS: FilteredResumeContent = FilteredResumeContent(
    bullet_points=[
        FilteredBulletPoint(
            bullet_point="Optimized SQL queries for high-traffic data ingestion.",
            relevance_score=0.85,
            metadata=MetaData(
                type="Experience",
                title="Data Engineer",
                source_id="experience_1",
            ),
        ),
        FilteredBulletPoint(
            bullet_point="Designed a complex LLM orchestration prototype using Python.",
            relevance_score=0.92,
            metadata=MetaData(
                type="Project",
                title="LLM Automator",
                source_id="project_1",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Developed automated data validation and anomaly detection systems."
            ),
            relevance_score=0.78,
            metadata=MetaData(
                type="Experience",
                title="AI Trainer",
                source_id="experience_2",
            ),
        ),
    ]
)


def run_rephrasing_test():
    """Tests the Filtering Agent's ability to rewrite and select optimized content."""

    print("\n--- Running Resume Filtering Agent Test ---")

    if not os.getenv("GEMINI_API_KEY"):
        print("Test Skipped: GEMINI_API_KEY not found.")
        return

    # Execute the agent
    filtered_content = resume_rephrasing_agent(
        TEST_REQ,
        TOP_RELEVANT_BULLETS,
        model_to_use={"llm_provider": "ollama", "llm_name": "qwen3:8b"},
    )
    print(filtered_content)
    if filtered_content and isinstance(filtered_content, FilteredResumeContent):
        print("\n✅ SUCCESS: Filtering Agent returned structured, rewritten data.")
        print(
            f"   Selected {len(filtered_content.bullet_points)} high-impact sections."
        )

        # Check if rewriting actually occurred and is correctly structured
        first_bullet = filtered_content.bullet_points[0]
        print(
            f"   Example Rewritten Bullet (Score {first_bullet.relevance_score:.2f}):"
        )
        print(f"   > {first_bullet.bullet_point}")

        # Check for presence of required keywords (heuristic check)
        if (
            "PostgreSQL" in first_bullet.bullet_point
            or "database" in first_bullet.bullet_point
        ):
            print("   (Keywords successfully integrated into the rewrite.)")

        assert len(filtered_content.bullet_points) > 0
    else:
        print(
            "\n❌ FAILURE: Filtering Agent failed to return a valid"
            " FilteredResumeContent object or returned no sections."
        )


if __name__ == "__main__":
    run_rephrasing_test()
