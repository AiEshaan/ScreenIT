# backend/app/ai/embeddings.py
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("📦 Loading SentenceTransformer (all-MiniLM-L6-v2)...")
        # Load local model
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("✅ Model ready.")
    return _model

def calculate_similarity(candidate_text: str, jd_text: str) -> float:
    """
    Computes cosine similarity between candidate text and job description.
    """
    model = get_embedding_model()
    embeddings = model.encode([candidate_text, jd_text])
    import numpy as np
    
    vec1 = embeddings[0]
    vec2 = embeddings[1]
    
    # Calculate cosine similarity
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2)) * 100.0
