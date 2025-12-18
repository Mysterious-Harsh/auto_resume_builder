# auto_resume_builder/agents/ats_score_agent.py

import os
import sys
import json
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import SecretStr

# --- Import Pydantic for Structured Output ---
try:
    from core.data_models import JobRequirements, ATSScoreOutput
except ImportError:
    print("FATAL ERROR: Could not import core LLM or data modules in ATS Score Agent.")
    sys.exit(1)


def ats_score_agent(
    model_to_use: Dict[str, Any],
    master_data: Dict[str, Any],
    requirements: JobRequirements,
) -> Optional[ATSScoreOutput]:
    """
    Simulates an ATS ranking to generate a match score and actionable feedback.

    Args:
        master_data: The master background dictionary containing the FINAL optimized content
                     in 'experiences' (filtered_bullets) and 'skills' (filtered_list).
        requirements: The structured job requirements extracted by the Analysis Agent.
    """
    print("\n--- ATS Score Agent: Calculating Match Score ---")

    # 1. Prepare Content for LLM

    # Extract the final, optimized content (must reflect the merged structure)
    optimized_bullets = []

    # Extract optimized experience bullets
    for exp_data in master_data.get("experiences", {}).values():
        optimized_bullets.extend(exp_data.get("description", []))

    # Extract optimized project bullets
    for proj_data in master_data.get("projects", {}).values():
        optimized_bullets.extend(proj_data.get("description", []))

    # Extract optimized skills list (concatenated)
    skill_lists = []
    for skill_data in master_data.get("skills", {}).values():
        skill_lists.append(" ".join(skill_data))
    # Concatenate all content into a single resume text block for evaluation
    optimized_resume_content = (
        " ".join(optimized_bullets) + " " + " | SKILLS: " + " ".join(skill_lists)
    )
    print("Optimized Resume Content for ATS Evaluation:", optimized_resume_content)

    if not optimized_resume_content.strip():
        print("❌ ATS Score Agent failed: No optimized content found to evaluate.")
        return None

    # 2. Prepare Requirements String
    req_str = f"MUST HAVES: {', '.join(requirements.must_have_skills)}. "
    req_str += f"KEYWORDS: {', '.join(requirements.keywords_and_phrases)}."
    req_str += (
        f" core RESPONSIBILITIES: {', '.join(requirements.core_responsibilities)}."
    )

    # 3. Construct the LLM Prompt
    prompt = f"""
        You are a simulated Applicant Tracking System (ATS) score calculator.
        Your task is to compare the OPTIMIZED RESUME CONTENT against the TARGET JOB REQUIREMENTS and provide a match score and detailed feedback.
        
        TARGET JOB REQUIREMENTS (Focus on these terms):
        ---
        {req_str}
        ---
        
        OPTIMIZED RESUME CONTENT (Concise text from the tailored resume):
        ---
        {optimized_resume_content}
        ---
        
        INSTRUCTIONS:
        1. **Calculate Score:** Assign an ATS match score from 0 to 100%. Base the score strictly on keyword presence, technical term usage, and alignment with the 'MUST HAVES'.
        2. **Identify Gaps:** List 3-5 critical skills from the REQUIREMENTS that are clearly missing from the RESUME CONTENT.
        3. **Suggest Fixes:** Provide 2-3 specific, actionable suggestions on how the candidate could adjust their existing resume content to cover the gaps and increase the score.
        
        OUTPUT FORMAT:
        You MUST return a single JSON object that strictly adheres to the provided schema.
        """

    # 4. Call LLM Client
    try:

        LLM_NAME = model_to_use.get("llm_name")
        LLM_PROVIDER = model_to_use.get("llm_provider")
        print(f"Using model configuration: {LLM_NAME} from {LLM_PROVIDER}")

        if not LLM_NAME:
            raise ValueError("LLM_MODEL not found in model_to_use configuration")

        if LLM_PROVIDER == "google":
            print("Using Google Gemini for ATS Score Agent")
            client = ChatGoogleGenerativeAI(
                model=LLM_NAME,  # e.g., "gemini-2.5-flash"
                api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(ATSScoreOutput)
            response = client.invoke(prompt)

        elif LLM_PROVIDER == "openrouter":
            print("Using OpenRouter for ATS Score Agent")
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            client = ChatOpenAI(
                model=LLM_NAME,
                api_key=SecretStr(openrouter_api_key),
                base_url="https://openrouter.ai/api/v1",
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(ATSScoreOutput)
            response = client.invoke(prompt)
        elif LLM_PROVIDER == "ollama":
            print("Using Ollama for ATS Score Agent")
            client = ChatOllama(
                model=LLM_NAME,
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(ATSScoreOutput)
            response = client.invoke(prompt)

            print(f"✅ ATS Score Calculated: {response.ats_score_percentage}%")  # type: ignore
            return response  # type: ignore
    except Exception as e:
        print(f"❌ Error calling LLM for ATS score: {e}")
        return None

    return None
