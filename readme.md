# 🤖 Auto-Resume Builder: Multi-Agent ATS Optimizer

An intelligent, multi-agent pipeline designed to automate the creation of highly tailored, ATS-optimized resumes. By scraping job descriptions, analyzing requirements, and performing semantic searches against a master background, this system generates a professional one-page resume that maximizes keyword match scores and mimics human writing styles.

Lightweight utility for generating, analyzing, and formatting resumes using a set of modular agents and a local Chroma vector store.

## 🌟 Key Features

-   Multi-Agent Orchestration: Uses specialized agents for scraping, job analysis, vector indexing, content filtering, and PDF generation.

-   Semantic Search (RAG): Utilizes ChromaDB to retrieve the most relevant experiences and skills from your master background using vector embeddings.

-   Dynamic PDF Generation: Automatically adjusts margins, font sizes (down to 9pt), and line spacing to ensure a perfect one-page fit following US/Canadian standards.

-   ATS Optimization & AI Evasion: Rewrites content to include high-density keywords and abbreviations while employing "Human-Written" stylistic constraints to bypass AI detectors.

-   Automated Scoring: Features an ATS Score Agent that provides a match percentage and actionable feedback before the final PDF is created.

## What this project does

-   Stores structured master background data in [data/master_background.json](data/master_background.json).
-   Indexes content and embeddings into a local Chroma DB ([data/chroma_data/chroma.sqlite3](data/chroma_data/chroma.sqlite3)).
-   Provides agents to scrape, index, rephrase, analyze, score for ATS, organize content, and generate PDFs.

## Core components

Agents (see source for details):

-   [`agents.scraper_agent`](agents/scraper_agent.py) — scrapes job/descriptions or web content.
-   [`agents.indexing_agent`](agents/indexing_agent.py) — builds/updates Chroma index from master data.
-   [`agents.analysis_agent`](agents/analysis_agent.py) — analyzes job text and resume bullets.
-   [`agents.rephrasing_agent`](agents/rephrasing_agent.py) — rewrites/rephrases bullets.
-   [`agents.ats_score_agent`](agents/ats_score_agent.py) — computes ATS fit/score.
-   [`agents.organize_agent`](agents/organize_agent.py) — organizes content for output.
-   [`agents.pdf_agent`](agents/pdf_agent.py) — renders final PDF (see [misc/PDF_Tests.ipynb](misc/PDF_Tests.ipynb) and tests in [tests/test_pdf_agent.py](tests/test_pdf_agent.py)).

Core utilities:

-   Configuration: [core/config.py](core/config.py)
-   Data models: see [`core.data_models.MetaData`](core/data_models.py) for metadata stored in vector DB.

## Setup & usage

1. Install (editable):

```sh
git clone https://github.com/your-username/auto_resume_builder.git
cd auto_resume_builder
pip install -r requirements.txt
```

2. Configuration:

-   Create a .env file in the root directory and add your API keys:
    `GEMINI_API_KEY=your_google_gemini_api_key_here`

3. Prepare Your Data

-   Edit or Add data/master_background.json with your full work history, education, and skills. Use the provided template in the file to ensure the agents can parse your history correctly.
-   Unique Keys: Notice the use of "education_1", "experience_1", and "project_1". These are unique identifiers used by the Indexing Agent to map vector search results back to the original source.

-   Lists for Descriptions: Always keep the description as a list of strings. This allows the Indexing Agent to create a separate vector embedding for every single bullet point, ensuring much higher precision during search, add detailed data.

-   The "Text" Field in Skills: In the skills object, keep the skills as a comma-separated string within a "text" key. This makes it easier for the Filtering Agent to identify and extract the relevant keywords into your new "filtered_list".

-   Data Persistence: When the pipeline runs, your agents should add new keys like filtered_bullets (for experiences/projects) and filtered_list (for skills) directly into this data structure in memory before passing it to the PDF Agent.

```json
{
	"name": "Harshkumar Patel",
	"phone_number": "+1(xxx)xxx-xxxx",
	"address": "address",
	"email": "emailaddress@outlook.com",
	"linkedin": "https://www.linkedin.com/in/HarshPatel31/",
	"github": "https://github.com/Mysterious-Harsh",
	"portfolio_website": "https://mysterious-harsh.github.io/MyPortfolio/index.html",
	"summary": "",
	"skills": {
		"programming_languages": "Python, R, Java, HTML, CSS, SQL",
		"scripting_languages": "Shell, Bash, Zsh, Batch, JavaScript",
		"web_development": "HTML, CSS, JavaScript, Java, Python, PHP, Django, Flask, Jinja2",
		"Cloud & Big Data": "Azure, AWS , Apache Spark, Docker, MLflow",
		"Data Visualization Tools": "Tableau, Power BI, Excel"
	},
	"educations": {
		"education_1": {
			"degree": "Postgraduate Diploma",
			"university": "Lambton College, Lambton College, Toronto, ON",
			"field_of_study": "Artificial Intelligence & Machine Learning",
			"start_date": "Jan 2022",
			"end_date": "Sept 2023"
		},
		"education_2": {
			"degree": "Bachelors of Engineering",
			"university": "Gujarat Technological University, India ",
			"field_of_study": "Computer Engineering ",
			"start_date": "Aug 2016",
			"end_date": "Aug 2020"
		}
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
				"Leading data analysis and model optimization initiatives for AI training datasets across multiple applications.",
				"Responsible for improving model performance through advanced data processing and validation techniques.",
				"Improved model training efficiency by 20% through strategic hyperparameter optimization and algorithm selection.",
				"Analyzed and optimized large-scale datasets (>1M records) for multiple AI applications, ensuring data quality and consistency.",
				"Developed automated data validation and anomaly detection systems, reducing manual review time by 35%.",
				"Collaborated with cross-functional teams to implement data-driven improvements in annotation workflows.",
				"Presented insights through advanced visualizations, contributing to strategic decision-making processes"
			]
		},
		"experience_2": {
			"position": "Automated Speech Research Scientist Intern",
			"company": "Microsoft (Nuance)",
			"location": "Montreal, QC",
			"type": "Internship",
			"start_date": "Mar 2023",
			"end_date": "Aug 2023",
			"description": [
				"Spearheaded the implementation of Speech Completion for Microsoft Teams Meetings and PowerPoint Presentations.",
				"Integrated cutting-edge AI technologies to enhance real-time speech recognition capabilities.",
				"Elevated real-time speech recognition accuracy by 80% through advanced neural network architectures.",
				"Integrated GPT-4 API for intelligent outcome prediction, enhancing user experience in Gradio UI.",
				"Designed and implemented CI/CD pipeline using GitHub Actions, reducing deployment failures by 40%.",
				"Shortened release cycle from 2 days to 1 day through automated testing and deployment processes.",
				"Awarded Regional Winner at Microsoft Global Hackathon 2023 for real-time speech summarization system."
			]
		}
	},
	"projects": {
		"project_1": {
			"name": "Roadside Anomaly Detection ",
			"description": [
				"Implemented Web-Based Deep Learning project using Flask & Jinja2 for Backend with Admin as well User Portal Login that detects anomalies on roads & generates Tickets by reading number plat with OCR.",
				"Trained YOLOv3 Model using vehicle dataset on Google Colab with GPU capacities & integrated it into the website.",
				"Used OpenCV threshold, edge detection & contour to fetch number plate and perform OCR using Tesseract-OCR."
			],
			"technologies": "Python, Flask, CNN, OpenCV, YOLOv3, Tesseract-OCR"
		},
		"project_2": {
			"name": "Real-Time Speech Emotion Recognition",
			"description": [
				"Engineered a deep-learning pipeline using LSTM neural networks with the RElU Activation function and Softmax Activation function for output layer to classify seven emotions (Calm, Happy, Angry, Sad, Fearful, and Disgust) from voice signals.",
				"Extracted audio features such as MFCCs, Chroma, and Mel using Librosa library for effective model training.",
				"Developed a real-time application using Python's sounddevice and soundfile libraries to capture live audio input and predict emotions on-the-fly.",
				"Collected and performed exploratory data analysis on 8,480 audio files from the RAVDESS and TESS datasets, extracting features such as Root Mean Squared Energy, Mel-Spectrograms and MFCCs for robust modelling.",
				"Designed and trained the model to reach 99.06% training accuracy (loss: 0.035) and 96.84% validation accuracy (loss: 0.1184)."
			],
			"technologies": "Python, LSTM, Matplotlib, Keras, TensorFlow, Librosa"
		}
	},
	"certifications": {
		"certification_1": {
			"name": "Unsupervised Learning, Recommenders, Reinforcement Learning",
			"issuer": "Coursera",
			"date": "Nov 2022"
		}
	}
}
```
