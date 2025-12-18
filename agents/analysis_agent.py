# auto_resume_builder/agents/analysis_agent.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import SecretStr
from core.data_models import JobRequirements


def job_analysis_agent(
    job_description: str,
    model_to_use: dict,
) -> JobRequirements | None:
    """
    Agent that analyzes a Job Description (JD) and extracts structured requirements
    for the filtering and indexing agents.

    Args:
        job_description: The raw text of the job posting.

    Returns:
        A JobRequirements object or None if the operation fails.
    """

    print("\n--- Job Analysis Agent: Extracting Structured Requirements ---")

    prompt = f"""
    JOB DESCRIPTION:
    ---
    {job_description}
    ---
    You are an expert Job Analyst and ATS Optimizer. Your task is to dissect the provided Job Description (JD) and extract the critical, high-value keywords and requirements needed for a resume, regardless of the industry.
    
    INSTRUCTIONS:
    1. **target_role:** Identify the specific, professional job title that the candidate will use on their resume (e.g., 'Senior Sales Manager', 'Registered Nurse', 'Marketing Specialist', 'Senior Data Scientist', 'Full Stack Developer').
    2. **must_have_skills:** Extract 5 to 10 absolute, non-negotiable **skills, industry-specific tools, or required certifications** mentioned in the JD. These must be **single words or short abbreviations** (e.g., Python, CRM, PMP, QuickBooks, HIPAA, SEO, InDesign).
    3. **nice_to_have_skills:** (e.g., additional skills that are beneficial but not mandatory).
    4.**keywords_and_phrases:** Extract 10 to 15 key processes, methodologies, and concepts that define the core work. These should be short, industry-specific phrases (e.g., Lead Generation, Agile Methodology, Patient Triage, Supply Chain Optimization, Content Strategy).
    5. **core_responsibilities:** Condense the main duties into 4 to 6 brief, descriptive sentences. Each sentence must focus on a specific, high-level task or outcome. **Do NOT include generic, non-actionable phrases** like "collaborate with teams" or "strong communication skills." Focus on specific actions, processes, and deliverables.

    
    OUTPUT FORMAT:
    
    You MUST return the results as a single JSON object that strictly adheres to the provided JSON Schema. Do NOT include any introductory text, apologies, or explanations outside the JSON block.
    """

    try:
        LLM_NAME = model_to_use.get("llm_name")
        LLM_PROVIDER = model_to_use.get("llm_provider")
        print(f"Using model configuration: {LLM_NAME} from {LLM_PROVIDER}")

        if not LLM_NAME:
            raise ValueError("LLM_MODEL not found in model_to_use configuration")

        if LLM_PROVIDER == "google":
            print("Using Google Gemini for Job Analysis Agent")
            client = ChatGoogleGenerativeAI(
                model=LLM_NAME,  # e.g., "gemini-2.5-flash"
                api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(JobRequirements)
            response = client.invoke(prompt)

        elif LLM_PROVIDER == "openrouter":
            print("Using OpenRouter for Job Analysis Agent")
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            client = ChatOpenAI(
                model=LLM_NAME,
                api_key=SecretStr(openrouter_api_key),
                base_url="https://openrouter.ai/api/v1",
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(JobRequirements)
            response = client.invoke(prompt)
        elif LLM_PROVIDER == "ollama":
            print("Using Ollama for Job Analysis Agent")
            client = ChatOllama(
                model=LLM_NAME,
                temperature=0.2,  # Optional: use a low temperature for more reliable structured output
            ).with_structured_output(JobRequirements)
            response = client.invoke(prompt)

        # The response.text will be a JSON string conforming to the JobRequirements schema
        # extracted_data = JobRequirements.model_validate_json(response)  # type: ignore

        print(f"Extraction successful for role: {response.target_role}")  # type: ignore
        return response  # type: ignore

    except Exception as e:
        print(f"Error in Job Analysis Agent during LLM call: {e}")
        return None
