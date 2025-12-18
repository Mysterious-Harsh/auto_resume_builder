# auto_resume_builder/agents/rephrasing_agent.py

import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import SecretStr

from core.data_models import (
    JobRequirements,
    FilteredResumeContent,
)


def resume_rephrasing_agent(
    job_requirements: JobRequirements,
    top_relevant_bullets: FilteredResumeContent,
    model_to_use: dict,
) -> FilteredResumeContent | None:
    """
    Agent that rewrites the semantically relevant items for maximum impact,
    using LLM context to incorporate target keywords.

    Args:
        job_requirements: Structured job_requirements from the Analysis Agent.
        top_relevant_bullets: Raw bullet point/skill data retrieved from the Vector DB.

    Returns:
        A FilteredResumeContent object with optimized bullets, or None on failure.
    """

    print("\n--- Resume Filtering Agent: Rewriting and Finalizing Content ---")

    # # 1. Format the relevant items for the LLM prompt
    # items_to_rewrite = ""
    # for i, item in enumerate(top_relevant_bullets):
    #     # Pass the original text and its estimated relevance score to guide the LLM
    #     items_to_rewrite += (
    #         f"[{i+1}][Score: {item['relevance_score']:.2f}][Type:"
    #         f" {item['metadata']['type']},{item['metadata']['title']}]:"
    #         f" {item['text']}\n"
    #     )

    # 2. Combine requirements into a strong query string
    # req_str = (
    #     f"Target Role: {requirements.target_role}. Must-Haves:"
    #     f" {', '.join(requirements.must_have_skills)}. Keywords:"
    #     f" {', '.join(requirements.keywords_and_phrases)}"
    # )

    prompt = f"""
    You are a professional Resume Writer specializing in optimizing content for Applicant Tracking Systems (ATS).
    Your task is to rewrite the provided background items to maximize their relevance to the TARGET JOB.
    
    TARGET JOB REQUIREMENTS:
    ---
    {job_requirements.model_dump_json(indent=2)}
    ---
    BACKGROUND ITEMS:
    ---
    {top_relevant_bullets.model_dump_json(indent=2)}
    ---
    
    INSTRUCTIONS FOR REWRITING:
    1. **Format Constraint (Experience/Project):** If the item 'type' is 'Experience', 'Project', 'Education', or 'Certification', the rewritten text MUST be a concise, high-impact phrase, starting with a strong action verb and use quantifiable metrics. Do NOT use full sentences or elaborate descriptions.
    
    2. **Format Constraint (Skill Set):** If the item 'type' is 'Skill Set', the 'bullet_point' MUST ONLY contain the specific skill keywords/abbreviations from the original 'text' that are most relevant to the TARGET JOB. Do NOT add new words, prepositions, or descriptive sentences. **The output for Skill Set items should be a comma-separated list of keywords only.**
    
    3. **Keyword Integration:** For Experience/Project/Skill Set items, seamlessly integrate the most relevant skills, tools, technologies, and abbreviations (e.g., use 'NLP' instead of 'Natural Language Processing', 'PostgreSQL' instead of 'database queries').
    
    4. **Measurable Impact:** For Experience/Project items, emphasize measurable results and quantifiable achievements whenever possible.
    ---
    **CRITICAL HUMAN-WRITING STYLISTIC CONSTRAINTS (For AI Detector Evasion):**
    
    5. **Avoid Perfection:** The final output must read as if it were written by an experienced human, not an AI. Introduce a slight variance in sentence flow and avoid highly repetitive phrase structures across different bullet points.
    
    6. **Embrace Natural Phrasing:** Use strong, active verbs but vary the complexity. Occasionally use contractions (e.g., "didn't," "it's") or slightly unconventional phrasing where it sounds more natural than the most optimized, robotic alternative.
    
    7. **Focus on Narrative:** Ensure each bullet point tells a mini-story of *action, skill, and result*, rather than just being a keyword list strung together.

    8. **Limit Over-Optimization:** While keywords are important, do not overstuff them to the point where the text feels unnatural or forced. Prioritize readability and human-like flow.
    
    9. **Output Structure:** your are only allowed to alter the bullet point and please return the metadata as it is do not change anything in it and Return the final output as a JSON object matching the FilteredResumeContent schema.
    
    """

    try:
        LLM_NAME = model_to_use.get("llm_name")
        LLM_PROVIDER = model_to_use.get("llm_provider")
        print(f"Using model configuration: {LLM_NAME} from {LLM_PROVIDER}")

        if not LLM_NAME:
            raise ValueError("LLM_MODEL not found in model_to_use configuration")

        if LLM_PROVIDER == "google":
            print("Using Google Gemini for Rephrasing Agent")
            client = ChatGoogleGenerativeAI(
                model=LLM_NAME,  # e.g., "gemini-2.5-flash"
                api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(FilteredResumeContent)
            response = client.invoke(prompt)

        elif LLM_PROVIDER == "openrouter":
            print("Using OpenRouter for Rephrasing Agent")
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            client = ChatOpenAI(
                model=LLM_NAME,
                api_key=SecretStr(openrouter_api_key),
                base_url="https://openrouter.ai/api/v1",
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(FilteredResumeContent)
            response = client.invoke(prompt)
        elif LLM_PROVIDER == "ollama":
            print("Using Ollama for Rephrasing Agent")
            client = ChatOllama(
                model=LLM_NAME,
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(FilteredResumeContent)
            response = client.invoke(prompt)

        # filtered_content = FilteredResumeContent.model_validate_json(response.text)  # type: ignore
        print(f"Rewriting complete. Selected {len(response.bullet_points)} high-impact bullets.")  # type: ignore
        return response  # type: ignore

    except Exception as e:
        print(f"Error in Filtering Agent during LLM call: {e}")
        return None
