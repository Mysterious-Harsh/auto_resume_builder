import os
import sys
import json
from dotenv import load_dotenv

# --- FIX: Ensure the package path is recognized for absolute imports ---
# If running with 'python main.py' from the 'auto_resume_builder' directory,
# you might still need to adjust the path or run with 'python -m auto_resume_builder.main'.
# For this script to work robustly, we assume you've configured your environment
# to recognize 'auto_resume_builder' as the package root.

# --- 1. Import Agents and Core Components (using absolute paths) ---
try:
    from agents.scraper_agent import scraper_agent
    from agents.analysis_agent import job_analysis_agent
    from agents.indexing_agent import (
        index_master_background,
        query_chroma_for_relevance,
    )
    from agents.organize_agent import organize_resume_content
    from agents.pdf_agent import generate_pdf_resume
    from agents.ats_score_agent import ats_score_agent

    # The PDF agent is needed here for final output
    # from auto_resume_builder.agents.pdf_agent import generate_pdf_resume

    from core.config import (
        MASTER_BACKGROUND_FILE,
        VECTOR_SEARCH_TOP_K,
    )
    from core.data_models import JobRequirements, FilteredResumeContent, ATSScoreOutput
except ImportError as e:
    print(f"FATAL ERROR: Could not import necessary modules. {e}")
    print(
        "Please ensure your Python path is correctly set and all imports in agents/ use"
        " the 'auto_resume_builder.' prefix."
    )
    sys.exit(1)


def load_master_background():
    """Loads and returns the user's master JSON background data."""
    try:
        with open(MASTER_BACKGROUND_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL: Master background file not found at {MASTER_BACKGROUND_FILE}")
        return None
    except json.JSONDecodeError:
        print("FATAL: Master background file is corrupted or invalid JSON.")
        return None


def run_resume_pipeline(
    job_url: str, model_to_use: dict, indexing_needed: bool = False
):
    """
    Orchestrates the multi-agent pipeline from job URL to final filtered content.
    """
    print("=====================================================")
    print("🤖 STARTING AUTO-RESUME BUILDER PIPELINE")
    print(f"TARGET URL: {job_url}")
    print("=====================================================")

    # ----------------------------------------------------
    # PHASE 0: SETUP AND DATA LOADING
    # ----------------------------------------------------

    # Load and index the master background data (Run once at start)
    master_data = load_master_background()
    if master_data is None:
        return
    if indexing_needed:
        print("\n--- PHASE 0: INDEXING MASTER BACKGROUND DATA ---")
        index_master_background(master_data)

    # Call the Indexing Agent to build/update the Vector DB
    # index_master_background(master_data)

    # ----------------------------------------------------
    # PHASE 1: SCRAPING AND ANALYSIS
    # ----------------------------------------------------

    # 1. Scrape the Job Description
    raw_job_description = scraper_agent(job_url)
    if not raw_job_description:
        print("PIPELINE ABORTED: Failed to reliably fetch the Job Description.")
        return

    # 2. Analyze the Job Description (LLM Call)
    job_requirements: JobRequirements = job_analysis_agent(raw_job_description, model_to_use=model_to_use)  # type: ignore
    if not job_requirements:
        print("PIPELINE ABORTED: Failed to extract structured Job Requirements.")
        return
    # print(job_requirements)
    # Print a quick summary of the analysis
    print("\n[PIPELINE] Analysis Complete. Extracted Must-Haves:")
    print(f"           - {', '.join(job_requirements.must_have_skills)}...")
    print(f"           - {', '.join(job_requirements.keywords_and_phrases)}...")

    # ----------------------------------------------------
    # PHASE 2: SEARCH AND FILTERING
    # ----------------------------------------------------

    # 3. Vector Database Search
    # Get all highly relevant items (above threshold, regardless of fixed top_k)
    top_relevant_bullets = query_chroma_for_relevance(
        requirements=job_requirements,
        top_k=VECTOR_SEARCH_TOP_K,  # High safety limit, filtering by score
    )

    if not top_relevant_bullets:
        print("PIPELINE ABORTED: No relevant content found in the Vector Database.")
        return
    bullet_points: FilteredResumeContent = FilteredResumeContent(
        bullet_points=top_relevant_bullets  # type: ignore
    )
    print(bullet_points)
    # 4. Content Rewriting and Filtering (LLM Call)
    from agents.rephrasing_agent import resume_rephrasing_agent

    final_content: FilteredResumeContent = resume_rephrasing_agent(
        job_requirements=job_requirements,
        top_relevant_bullets=bullet_points,
        model_to_use=model_to_use,
    )  # type: ignore
    if not final_content or not final_content.bullet_points:
        print(
            "PIPELINE ABORTED: Failed to rewrite content or no bullets were selected by"
            " the filter."
        )
        return
    print(final_content)

    print("\n[PIPELINE] Content Rewriting Completed.")

    print("\n[PIPELINE] Organizing Final Resume Content...")
    # Organize the final content into a structured format
    organized_background_data = organize_resume_content(
        master_background=master_data, filtered_content=final_content
    )
    print(organized_background_data)

    # 5. ATS Score Calculation
    ats_score = ats_score_agent(
        model_to_use=model_to_use,
        master_data=organized_background_data,
        requirements=job_requirements,
    )

    if ats_score:
        print("\n--- ATS SCORE REPORT ---")
        print(f"FINAL ATS MATCH SCORE: {ats_score.ats_score_percentage}%")
        print("Missing Critical Skills:")
        for skill in ats_score.missing_critical_skills:
            print(f"  - {skill}")
        print("Suggestions:")
        for suggestion in ats_score.suggestions_for_improvement:
            print(f"  - {suggestion}")
        print("------------------------")

    # ----------------------------------------------------
    # PHASE 3: FINAL OUTPUT (PDF Generation)
    # ----------------------------------------------------

    # 5. Generate Resume PDF (Requires pdf_agent.py to be implemented)
    print("\n--- PHASE 3: FINAL OUTPUT GENERATION ---")
    try:
        # Note: You need to implement the 'generate_pdf_resume' function in pdf_agent.py
        generate_pdf_resume(organized_background_data, job_requirements.target_role)
        print("Successfully generated tailored resume PDF (Placeholder).")
    except Exception as e:
        print(f"PDF GENERATION FAILED: {e}")

    print("\n=====================================================")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("=====================================================")


if __name__ == "__main__":
    # Load .env file for API Key
    load_dotenv()

    # --- DEFINE YOUR TARGET JOB POSTING HERE ---
    # Use a real URL for a full test
    TARGET_JOB_URL = (
        "https://ca.indeed.com/viewjob?jk=8e3b1811f907c538&from=shareddesktop_copy"
    )
    # Displaying LLM Lists for user selection
    LIST_OF_LLM_MODELS = [
        {"llm_provider": "google", "llm_name": ["gemini-2.5-flash"]},
        {
            "llm_provider": "openrouter",
            "llm_name": [
                "qwen/qwen3-235b-a22b:free",
                "moonshotai/kimi-k2:free",
                "allenai/olmo-3.1-32b-think:free",
                "tngtech/deepseek-r1t2-chimera:free",
                "mistralai/devstral-2512:free",
            ],
        },
        {
            "llm_provider": "ollama",
            "llm_name": [
                "deepseek-r1",
                "qwen3:8b",
                "qwen3:14b",
                "gemini-3-pro-preview",
                "gemini-3-flash-preview:cloud",
                "kimi-k2-thinking:cloud",
                "qwen3-next:80b-cloud",
            ],
        },
    ]
    print("Available LLM Models:")
    i = 1
    for model in LIST_OF_LLM_MODELS:
        print(f"{model['llm_provider'].upper()}:")
        for name in model["llm_name"]:
            print(f"  [{i}] {name}")
            i += 1
    llm_id = input(
        "\n Please select your desired LLM model and press Enter to continue..."
    )
    # For simplicity, we hardcode the model selection here
    if llm_id == "1":
        model_to_use = {"llm_provider": "google", "llm_name": "gemini-2.5-flash"}
    elif llm_id in ["2", "3", "4", "5", "6"]:

        model_to_use = {
            "llm_provider": "openrouter",
            "llm_name": LIST_OF_LLM_MODELS[1]["llm_name"][int(llm_id) - 2],
        }
    elif int(llm_id) >= 7:
        model_to_use = {
            "llm_provider": "ollama",
            "llm_name": LIST_OF_LLM_MODELS[2]["llm_name"][int(llm_id) - 7],
        }
    else:
        print("Invalid selection. Falling back to default model.")
        model_to_use = {"llm_provider": "google", "llm_name": "gemini-2.5-flash"}

    print(
        f"Selected model: {model_to_use['llm_name']} from"
        f" {model_to_use['llm_provider']}"
    )

    # Asking user if indexing is needed
    indexing_input = input(
        "\n Do you want to re-index the master background data? (y/n): "
    )
    indexing_needed = indexing_input.lower() == "y"
    # Execute the pipeline
    run_resume_pipeline(TARGET_JOB_URL, model_to_use, indexing_needed=indexing_needed)
