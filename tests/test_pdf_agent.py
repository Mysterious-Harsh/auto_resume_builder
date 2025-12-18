# test_pdf_agent.py

import os
import sys
import json
import tempfile
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- FIX: Set the Python Path to recognize 'auto_resume_builder' as the package root ---
# # Note: This is a robust way to handle imports for test files run outside the package.
# project_root = os.path.dirname(os.path.abspath(__file__))
# # Check if auto_resume_builder is directly in the root
# if os.path.exists(os.path.join(project_root, "auto_resume_builder")):
#     sys.path.append(os.path.join(project_root))
# --------------------------------------------------------------------------------------

# Load environment variables (needed if PDF_OUTPUT_DIR is defined here)
load_dotenv()

try:
    # Use absolute imports for the agent and models
    from agents.pdf_agent import generate_pdf_resume
    from agents.organize_agent import organize_resume_content
    from agents.ats_score_agent import ats_score_agent
    from core.data_models import (
        FilteredResumeContent,
        FilteredBulletPoint,
        MetaData,
        JobRequirements,
        ATSScoreOutput,
    )
    from core.config import MASTER_BACKGROUND_FILE

    # Define the output directory to a temporary location for testing
    TEST_PDF_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "test_resume_output")

except ImportError as e:
    print(f"FATAL ERROR during import: {e}")
    print(
        "Ensure you have set up the absolute imports correctly and all dependencies"
        " (fpdf2, pydantic) are installed."
    )
    sys.exit(1)


# --- 1. SIMULATED INPUT DATA ---

# A. Master Background Data (A subset of master_background.json)
with open(MASTER_BACKGROUND_FILE, "r") as f:
    MASTER_DATA = json.load(f)

# B. Filtered Content (Output from Filtering Agent)
FILTERED_CONTENT = FilteredResumeContent(
    sections=[
        FilteredBulletPoint(
            bullet_point="Python, SQL",
            relevance_score=0.8294684886932373,
            metadata=MetaData(
                source_id="programming_languages",
                type="skills",
                title="programming_languages",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "TensorFlow, Pandas, PyTorch, SciPy, Scikit-Learn, Keras, XGBoost,"
                " NLTK, Flask, Django"
            ),
            relevance_score=0.8213152885437012,
            metadata=MetaData(
                source_id="python_libraries", type="skills", title="python_libraries"
            ),
        ),
        FilteredBulletPoint(
            bullet_point="Azure, AWS, Apache Spark, Docker, MLflow",
            relevance_score=0.8198609352111816,
            metadata=MetaData(
                source_id="Cloud & Big Data", type="skills", title="Cloud & Big Data"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Led data analysis and model optimization initiatives for AI training"
                " datasets, enhancing performance across diverse applications."
            ),
            relevance_score=0.8178659677505493,
            metadata=MetaData(
                source_id="experience_1", type="experiences", title="AI Trainer"
            ),
        ),
        FilteredBulletPoint(
            bullet_point="JavaScript, Python, Django, Flask",
            relevance_score=0.8134992122650146,
            metadata=MetaData(
                source_id="web_development", type="skills", title="web_development"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Participated in Agile software development, contributing to code"
                " reviews and optimization efforts."
            ),
            relevance_score=0.8122393488883972,
            metadata=MetaData(
                source_id="experience_4",
                type="experiences",
                title="Deep Learning Scientist",
            ),
        ),
        FilteredBulletPoint(
            bullet_point="Data Visualization, Problem-Solving, Critical Thinking",
            relevance_score=0.8067041039466858,
            metadata=MetaData(
                source_id="Professional Skills",
                type="skills",
                title="Professional Skills",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Improved machine learning model performance utilizing advanced data"
                " processing and validation techniques."
            ),
            relevance_score=0.7944411635398865,
            metadata=MetaData(
                source_id="experience_1", type="experiences", title="AI Trainer"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Natural Language Processing (NLP), Data Visualization, Model"
                " Development"
            ),
            relevance_score=0.7934510707855225,
            metadata=MetaData(
                source_id="deep learning", type="skills", title="deep learning"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Trained and deployed deep learning models for various computer vision"
                " applications, contributing to software features."
            ),
            relevance_score=0.7913139462471008,
            metadata=MetaData(
                source_id="experience_4",
                type="experiences",
                title="Deep Learning Scientist",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Analyzed and optimized large-scale datasets (>1M records) for AI"
                " applications, ensuring data quality and consistency for improved"
                " model performance."
            ),
            relevance_score=0.7835239768028259,
            metadata=MetaData(
                source_id="experience_1", type="experiences", title="AI Trainer"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Developed robust backend systems leveraging Python, Flask, and Django"
                " for production deployment of ML applications."
            ),
            relevance_score=0.7805604934692383,
            metadata=MetaData(
                source_id="experience_4",
                type="experiences",
                title="Deep Learning Scientist",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "SOLID Principles, Programming Design Patterns, Agile, Test-Driven"
                " Development"
            ),
            relevance_score=0.7734562754631042,
            metadata=MetaData(
                source_id="Methodologies", type="skills", title="Methodologies"
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Developed comprehensive reporting systems and automated data"
                " processing pipelines, streamlining data analysis workflows."
            ),
            relevance_score=0.7721039056777954,
            metadata=MetaData(
                source_id="experience_3",
                type="experiences",
                title="Data/Business Analyst",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Led data analysis initiatives, significantly improving operational"
                " efficiency and contributing to business growth through optimization"
                " strategies."
            ),
            relevance_score=0.768844485282898,
            metadata=MetaData(
                source_id="experience_3",
                type="experiences",
                title="Data/Business Analyst",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Enhanced machine learning model accuracy and developed automated"
                " monitoring systems to ensure robust real-time operations."
            ),
            relevance_score=0.7621472477912903,
            metadata=MetaData(
                source_id="experience_4",
                type="experiences",
                title="Deep Learning Scientist",
            ),
        ),
        FilteredBulletPoint(
            bullet_point=(
                "Collaborated with cross-functional teams, implementing data-driven"
                " improvements in annotation workflows and supporting product"
                " development."
            ),
            relevance_score=0.7600703835487366,
            metadata=MetaData(
                source_id="experience_1", type="experiences", title="AI Trainer"
            ),
        ),
    ]
)

TEST_REQ = JobRequirements(
    target_role="AI/ML Specialist",
    must_have_skills=["NLP", "Python", "TensorFlow", "PostgreSQL"],
    nice_to_have_skills=["Docker", "Kubernetes"],
    keywords_and_phrases=["multi-agent system", "GitHub Actions", "data validation"],
    core_responsibilities=["present insights", "optimize database queries"],
)

TARGET_ROLE = "Senior AI/ML Developer (Test)"


def run_pdf_agent_test():
    """Tests the PDF Agent's ability to execute and create a file."""

    print("\n--- Running PDF Agent Test ---")

    organized_content = organize_resume_content(
        master_background=MASTER_DATA, filtered_content=FILTERED_CONTENT
    )
    print("Organized Content:", json.dumps(organized_content, indent=4))

    # sys.exit(0)  # TEMP EXIT TO TEST ORGANIZE FUNCTION
    # 5. ATS Score Calculation
    # --- Execute the Agent ---
    output_path = generate_pdf_resume(
        data={
            "name": "Harshkumar Patel",
            "phone_number": "+1(437)421-3950",
            "address": "Saint John, New Brunswick",
            "email": "theharsh1@outlook.com",
            "linkedin": "https://www.linkedin.com/in/HarshPatel31/",
            "github": "https://github.com/Mysterious-Harsh",
            "portfolio_website": (
                "https://mysterious-harsh.github.io/MyPortfolio/index.html"
            ),
            "summary": "",
            "skills": {
                "Cloud & Big Data": ["Azure, AWS, Apache Spark, Docker, MLflow"],
                "python_libraries": [
                    "TensorFlow, PyTorch, Scikit-learn, XGBoost, Keras, NLTK, Flask,"
                    " Django"
                ],
                "deep learning": [
                    "NLP, Image Processing, Audio Processing, Model Development"
                ],
                "machine_learning": [
                    "Supervised Learning, Unsupervised Learning, Predictive Modeling"
                ],
                "Data Visualization Tools": ["Tableau, Power BI"],
                "programming_languages": ["Python, SQL"],
            },
            "educations": {
                "education_1": {
                    "degree": "Postgraduate Diploma",
                    "university": "Lambton College, Lambton College, Toronto, ON",
                    "field_of_study": "Artificial Intelligence & Machine Learning",
                    "start_date": "Jan 2022",
                    "end_date": "Sept 2023",
                },
                "education_2": {
                    "degree": "Bachelors of Engineering",
                    "university": "Gujarat Technological University, India ",
                    "field_of_study": "Computer Engineering ",
                    "start_date": "Aug 2016",
                    "end_date": "Aug 2020",
                },
            },
            "experiences": {
                "experience_1": {
                    "position": "AI Trainer",
                    "company": "DataAnnotation.tech",
                    "location": "Remote",
                    "type": "Freelance",
                    "start_date": "Jan 2024",
                    "end_date": "Present",
                    "description": [
                        (
                            "Optimized large-scale datasets (>1M records) for AI"
                            " applications, ensuring data quality and consistency for"
                            " robust AI model training."
                        ),
                        (
                            "Led data analysis and model optimization initiatives for"
                            " AI training datasets across multiple applications,"
                            " enhancing data preparation and model performance."
                        ),
                        (
                            "Improved AI model performance through advanced data"
                            " processing and validation techniques, crucial for"
                            " end-to-end AI lifecycle management and MLOps."
                        ),
                    ],
                },
                "experience_2": {
                    "position": "Automated Speech Research Scientist Intern",
                    "company": "Microsoft (Nuance)",
                    "location": "Montreal, QC",
                    "type": "Internship",
                    "start_date": "Mar 2023",
                    "end_date": "Aug 2023",
                    "description": [
                        (
                            "Integrated GPT-4 API to develop generative AI solutions"
                            " for intelligent outcome prediction, significantly"
                            " enhancing user experience in Gradio UI."
                        ),
                        (
                            "Integrated cutting-edge AI technologies to enhance"
                            " real-time speech recognition capabilities, contributing"
                            " to robust AI solutions."
                        ),
                        (
                            "Secured Regional Winner at Microsoft Global Hackathon 2023"
                            " for developing a real-time speech summarization system,"
                            " showcasing innovation in generative AI solutions."
                        ),
                        (
                            "Spearheaded implementation of an AI-driven speech"
                            " completion system for Microsoft Teams Meetings and"
                            " PowerPoint Presentations, enhancing automation and user"
                            " productivity."
                        ),
                    ],
                },
                "experience_4": {
                    "position": "Deep Learning Scientist",
                    "company": "SoftVan",
                    "location": "Ahmedabad, India",
                    "type": "Fulltime-Internship",
                    "start_date": "May 2019",
                    "end_date": "Apr 2020",
                    "description": [
                        (
                            "Trained and rigorously evaluated CNN models for pattern"
                            " detection, achieving 98% accuracy and improving machine"
                            " learning solution efficacy."
                        ),
                        (
                            "Developed robust backend systems using Flask and Django"
                            " for production-grade AI solution deployment and MLOps"
                            " pipelines."
                        ),
                    ],
                },
            },
            "projects": {
                "project_1": {
                    "name": "Roadside Anomaly Detection ",
                    "description": [
                        (
                            "Implemented a web-based Deep Learning project using Flask"
                            " for automated roadside anomaly detection and ticket"
                            " generation via OCR, showcasing production-grade AI"
                            " deployment."
                        ),
                        (
                            "Trained and deployed a YOLOv3 model using GPU capacities"
                            " for vehicle detection, integrating it into a web"
                            " application for real-time AI solutions."
                        ),
                    ],
                    "technologies": "Python, Flask, CNN, OpenCV, YOLOv3, Tesseract-OCR",
                },
                "project_2": {
                    "name": "Real-Time Speech Emotion Recognition",
                    "description": [
                        (
                            "Designed and trained an AI model, achieving 99.06%"
                            " training accuracy and 96.84% validation accuracy for"
                            " robust real-time speech emotion recognition."
                        ),
                        (
                            "Engineered audio features (MFCCs, Chroma, Mel) using"
                            " Librosa for effective model training, optimizing data"
                            " preparation for AI solutions."
                        ),
                    ],
                    "technologies": (
                        "Python, LSTM, Matplotlib, Keras, TensorFlow, Librosa"
                    ),
                },
            },
            "certifications": {
                "certification_1": {
                    "name": (
                        "Unsupervised Learning, Recommenders, Reinforcement Learning"
                    ),
                    "issuer": "Coursera",
                    "date": "Nov 2022",
                }
            },
        },
        target_role=TARGET_ROLE,
    )

    # # --- Validation Checks ---
    # print("\n--- Validation ---")

    # if output_path is None:
    #     print("❌ FAILURE: PDF Agent returned None (Execution Failure).")
    #     return

    # # 1. Check if the file exists
    # if os.path.exists(output_path):
    #     print(f"✅ SUCCESS: PDF file created at: {output_path}")
    # else:
    #     print(f"❌ FAILURE: PDF file not found at expected path: {output_path}")
    #     return

    # # 2. Check file size (ensure it's not an empty file)
    # file_size = os.path.getsize(output_path)
    # if file_size > 1000:  # A reasonable minimum size for a non-empty PDF
    #     print(f"✅ SUCCESS: File size is {file_size} bytes (Non-empty).")
    # else:
    #     print(
    #         f"❌ FAILURE: File size is too small ({file_size} bytes). PDF may be empty."
    #     )

    # # 3. Check for correct filename convention
    # expected_filename_part = (
    #     "Harshkumar_Patel_Senior_AI_ML_Developer_Test_Tailored_Resume.pdf"
    # )
    # if expected_filename_part in output_path:
    #     print(f"✅ SUCCESS: Filename matches expected convention.")
    # else:
    #     print(
    #         f"❌ FAILURE: Filename '{os.path.basename(output_path)}' does not match"
    #         " expected convention."
    #     )


if __name__ == "__main__":
    run_pdf_agent_test()
    print(
        "\nNOTE: Generated PDF is saved in your system's temporary directory for"
        " inspection."
    )
