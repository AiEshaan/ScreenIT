"""
Resume Screening Agent
----------------------
AI-powered resume screening and candidate ranking system.

Pipeline:
    PDF/TXT Resume → Text Extraction → Feature Extraction
    → Semantic Similarity (SentenceTransformer) → Weighted Ranking
    → LLM Recruiter Summary → JSON + CSV + Markdown Output
"""

__version__ = "1.0.0"
__author__ = "Eshaan Mayekar"
