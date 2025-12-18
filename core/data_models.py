# --- auto_resume_builder/core/data_models.py ---

from pydantic import BaseModel, Field
from typing import List, Dict

# --- Agent 1 & 2 Output (Job Analysis & Vector Query Input) ---


class JobRequirements(BaseModel):
    """Structured requirements extracted by the Analysis Agent from the Job Description."""

    target_role: str = Field(description="The exact job title to tailor the resume to.")
    must_have_skills: List[str] = Field(
        description="Critical, non-negotiable technical or soft skills."
    )
    nice_to_have_skills: List[str] = Field(
        description="Critical, non-negotiable technical or soft skills."
    )
    keywords_and_phrases: List[str] = Field(
        description=(
            "General relevant keywords, industry terms, or desired responsibilities."
        )
    )
    core_responsibilities: List[str] = Field(
        description="Key tasks the candidate will perform."
    )


class MetaData(BaseModel):
    """Metadata for a single bullet point stored in the vector database."""

    source_id: str = Field(
        description=(
            "Original Unchanged unique source ID of the master background (e.g.,"
            " 'experience_1, python_libraries, certification_1')."
        )
    )
    type: str = Field(
        description=(
            "The Unchanged source category: 'Experience', 'Project', 'Skill Set', or"
            " 'Education'."
        )
    )
    title: str = Field(
        description=(
            "The original Unchanged source title (e.g., 'AI Trainer' or 'Data"
            " Engineer')."
        )
    )


# --- Agent 3 & 4 Input/Output (Filtering & Generation) ---


class FilteredBulletPoint(BaseModel):
    """A single bullet point, rewritten and scored by the Filtering Agent."""

    bullet_point: str = Field(
        description=(
            "The rewritten, highly optimized bullet point, incorporating job"
            " description keywords."
        )
    )
    relevance_score: float = Field(
        description="The final relevance score (must be >= 0.5)."
    )
    metadata: MetaData = Field(
        description="The original metadata from the vector database."
    )


class FilteredResumeContent(BaseModel):
    """The final, filtered and rewritten content ready for PDF generation."""

    bullet_points: List[FilteredBulletPoint]


# --- Structured Output Model ---
class ATSScoreOutput(BaseModel):
    """Structured output for the ATS Score Agent."""

    ats_score_percentage: int = Field(
        ..., description="The final ATS match score as a percentage (0-100)."
    )
    missing_critical_skills: List[str] = Field(
        ...,
        description=(
            "List of 3-5 critical skills from the job requirements that were NOT"
            " adequately covered in the final resume bullets."
        ),
    )
    suggestions_for_improvement: List[str] = Field(
        ...,
        description=(
            "2-3 specific, actionable suggestions to increase the score (e.g., 'Add a"
            " bullet about Python in experience_1')."
        ),
    )
