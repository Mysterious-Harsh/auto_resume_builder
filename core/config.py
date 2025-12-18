# --- auto_resume_builder/core/config.py ---
import os

# --- LLM and Embedding Configuration ---
# High-quality embedding model for semantic search
GOOGLE_EMBEDDING_MODEL = "models/text-embedding-004"
OLLAMA_EMBEDDING_MODEL = "qwen3-embedding:8b"  # Ollama embedding model


# --- ChromaDB Configuration ---
# Name of the collection (table) in the vector database
CHROMA_COLLECTION_NAME = "resume_master_data"
# Local directory where ChromaDB will store its persistent files
CHROMA_DB_PATH = os.path.join(os.getcwd(), "data", "chroma_data")

# --- Project Paths ---
# Path to the master JSON file
MASTER_BACKGROUND_FILE = os.path.join(os.getcwd(), "data", "master_background.json")
# Path for generated PDF outputs
OUTPUTS_DIR = os.path.join(os.getcwd(), "outputs")

# --- Application Constants ---
# Minimum relevance score threshold for content selection
MIN_RELEVANCE_THRESHOLD = 0.50
# Number of top results to fetch from the Vector DB for LLM refinement
VECTOR_SEARCH_TOP_K = 20
# Default timeout for web scraping operations (in seconds)
DEFAULT_SCRAPER_TIMEOUT = 15
# Create output directories if they don't exist
os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
