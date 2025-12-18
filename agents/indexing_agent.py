import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Core Intelligence (LLM) and Models
from google import genai
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
import chromadb

# Import Configuration and Data Models from the core directory
try:
    from ..core.config import (
        GOOGLE_EMBEDDING_MODEL,
        OLLAMA_EMBEDDING_MODEL,
        CHROMA_COLLECTION_NAME,
        CHROMA_DB_PATH,
        MIN_RELEVANCE_THRESHOLD,
    )
    from ..core.data_models import JobRequirements
except ImportError:
    from core.config import (
        GOOGLE_EMBEDDING_MODEL,
        OLLAMA_EMBEDDING_MODEL,
        CHROMA_COLLECTION_NAME,
        CHROMA_DB_PATH,
        MIN_RELEVANCE_THRESHOLD,
    )
    from core.data_models import JobRequirements

load_dotenv()


# --- GLOBAL INITIALIZATION ---
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
except Exception as e:
    print(
        "ERROR: Failed to initialize Gemini or Chroma client. Check API key and"
        f" directory path. Error: {e}"
    )

# Global reference for the Chroma collection
resume_collection = None


def prepare_data_for_indexing(json_data: dict) -> List[Dict]:
    """
    Flattens the structured JSON background into a list of documents
    with metadata suitable for embedding in ChromaDB.
    """
    data_points = []

    # --- 1. Process Experiences ---
    for exp_key, exp_data in json_data.get("experiences", {}).items():
        position = exp_data.get("position", "Untitled Position")
        company = exp_data.get("company", "Unknown Company")
        for i, bullet in enumerate(exp_data.get("description", [])):
            data_points.append({
                "id": f"{exp_key}_{i}",
                "document": bullet,  # The text to be embedded
                "metadata": {
                    "type": "experiences",
                    "source_id": exp_key,
                    "title": position,
                },
            })
    # --- 2. Process Projects (NEW SECTION) ---
    for proj_key, proj_data in json_data.get("projects", {}).items():
        name = proj_data.get("name", "Untitled Project")
        # Embed each description bullet point for granular search
        for i, bullet in enumerate(proj_data.get("description", [])):
            data_points.append({
                "id": f"{proj_key}_{i}",
                "document": bullet,
                "metadata": {
                    "type": "projects",
                    "source_id": proj_key,
                    "title": name,
                },
            })

    # --- 2. Process Skills ---
    for skill_category, skills_string in json_data.get("skills", {}).items():
        if skills_string:
            # Treat each skill category as one embeddable document
            data_points.append({
                "id": f"{skill_category}",
                "document": skills_string,
                "metadata": {
                    "type": "skills",
                    "source_id": skill_category,
                    "title": skill_category,
                },
            })

    # # --- 3. Process Education ---
    # for edu_key, edu_data in json_data.get("educations", {}).items():
    #     doc = (
    #         f"{edu_data.get('degree')} in {edu_data.get('field_of_study')} from"
    #         f" {edu_data.get('university')} ({edu_data.get('start_date')} to"
    #         f" {edu_data.get('end_date')})"
    #     )
    #     data_points.append({
    #         "id": f"{edu_key}",
    #         "document": doc,
    #         "metadata": {"type": "Education", "title": edu_data.get("degree")},
    #     })
    # --- 5. Process Certifications (NEW SECTION) ---
    for cert_key, cert_data in json_data.get("certifications", {}).items():
        name = cert_data.get("name", "Untitled Certification")
        data_points.append({
            "id": f"{cert_key}",
            "document": name,
            "metadata": {
                "type": "certifications",
                "source_id": cert_key,
                "title": name,
            },
        })

    return data_points


def index_master_background(json_data: dict, client: str = "ollama"):
    """
    Creates the ChromaDB collection, indexes the user's background data,
    and handles the embedding using the Gemini API.
    """
    global resume_collection
    if not client:
        return

    prepared_data = prepare_data_for_indexing(json_data)
    print(prepared_data)

    print(
        f"\n[INDEXING AGENT] Preparing {len(prepared_data)} documents for embedding..."
    )

    ids = [item["id"] for item in prepared_data]
    documents = [item["document"] for item in prepared_data]
    metadatas = [item["metadata"] for item in prepared_data]

    try:
        # 1. Ensure the collection is fresh if needed (optional)
        try:
            chroma_client.delete_collection(name=CHROMA_COLLECTION_NAME)
        except:
            pass  # Ignore if collection doesn't exist
        if client == "ollama":

            doc_embedding_func = OllamaEmbeddingFunction(
                url="http://localhost:11434",  # Default Ollama URL
                model_name=OLLAMA_EMBEDDING_MODEL,
            )
        elif client == "gemini":
            doc_embedding_func = GoogleGenerativeAiEmbeddingFunction(
                api_key=os.getenv("GEMINI_API_KEY"), model_name=GOOGLE_EMBEDDING_MODEL
            )
        # 2. Create the collection, specifying the embedding function
        resume_collection = chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
            embedding_function=doc_embedding_func,  # type: ignore
        )

        # 3. Add the documents to the collection (Chroma handles the embedding call)
        resume_collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(
            f"Indexing complete! Total documents indexed: {resume_collection.count()}"
        )

    except Exception as e:
        print(f"Error during Chroma indexing: {e}")


def query_chroma_for_relevance(
    requirements: JobRequirements, top_k: int = 20, client: str = "ollama"
) -> List[Dict]:
    """
    Performs semantic search against the ChromaDB collection using JD requirements.

    Returns a list of dictionaries containing the relevant documents and metadata.
    """
    global resume_collection
    # Ensure the collection exists before querying
    if resume_collection is None:
        # Try to reconnect to the persistent collection if it was already created
        try:
            if client == "ollama":

                doc_embedding_func = OllamaEmbeddingFunction(
                    url="http://localhost:11434",  # Default Ollama URL
                    model_name=OLLAMA_EMBEDDING_MODEL,
                )
            elif client == "gemini":
                doc_embedding_func = GoogleGenerativeAiEmbeddingFunction(
                    api_key=os.getenv("GEMINI_API_KEY"),
                    model_name=GOOGLE_EMBEDDING_MODEL,
                )
            resume_collection = chroma_client.get_collection(
                name=CHROMA_COLLECTION_NAME,
                embedding_function=doc_embedding_func,  # type: ignore
            )
        except Exception:
            print("Error: Resume collection is not initialized or does not exist.")
            return []

    print(f"\n[VECTOR DB AGENT] Searching for top {top_k} relevant items...")

    # Create a concise query string from the JobRequirements object
    # This query string will be embedded and used to search the vector space.
    req_str = (
        requirements.target_role
        + " "
        + " ".join(requirements.must_have_skills)
        + " "
        + " ".join(requirements.keywords_and_phrases)
    )

    try:
        # Perform the query
        results = resume_collection.query(
            query_texts=[req_str],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        relevant_items = []
        for doc, meta, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]  # type: ignore
        ):
            # Convert cosine distance (0=perfect match, 2=opposite) to a relevance score (1.0=perfect match)
            relevance_score = max(0.5, 1.0 - distance)
            if relevance_score > MIN_RELEVANCE_THRESHOLD:
                relevant_items.append({
                    "bullet_point": doc,  # The original bullet point/skill text
                    "relevance_score": relevance_score,
                    "metadata": meta,
                })

        print(f"Vector search retrieved {len(relevant_items)} items.")
        return relevant_items

    except Exception as e:
        print(f"Error during Chroma query: {e}")
        return []
