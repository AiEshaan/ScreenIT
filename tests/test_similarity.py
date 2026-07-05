from app.ai.embeddings import calculate_similarity

def test_similarity_score_range():
    score = calculate_similarity(
        "Python FastAPI Docker",
        "Python FastAPI"
    )
    assert 0.0 <= score <= 100.0
