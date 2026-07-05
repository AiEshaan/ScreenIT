"""
resume_screening/skills_database.py
-------------------------------------
Curated skills database for deterministic, reproducible skill extraction.
Uses case-insensitive word-boundary matching — no API key required.

Advantages over LLM-only extraction:
  - Deterministic: same input always yields same skills
  - Fast: no network call, runs in microseconds
  - Reproducible: easy to audit and extend
"""

from __future__ import annotations
import re
from typing import List

# ── Skill Categories ─────────────────────────────────────────────────────────

PROGRAMMING_LANGUAGES: List[str] = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C",
    "Go", "Golang", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "Scala",
    "R", "MATLAB", "Shell", "Bash", "PowerShell", "SQL", "PL/SQL", "T-SQL",
    "Dart", "Haskell", "Lua", "Perl", "Groovy", "Julia",
]

ML_AI: List[str] = [
    # Concepts
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
    "Computer Vision", "Reinforcement Learning", "Transfer Learning",
    "Supervised Learning", "Unsupervised Learning", "Semi-supervised Learning",
    "Feature Engineering", "Model Training", "Model Deployment", "Model Evaluation",
    "A/B Testing", "Data Analysis", "Data Science", "Data Engineering",
    "Recommendation Systems", "Anomaly Detection", "Time Series",
    "Prompt Engineering", "Fine-tuning", "RLHF", "RAG",
    # Frameworks / Libraries
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "XGBoost",
    "LightGBM", "CatBoost", "Pandas", "NumPy", "SciPy",
    "Matplotlib", "Seaborn", "Plotly", "Jupyter", "Colab",
    # LLM / GenAI
    "LangChain", "LangGraph", "OpenAI", "Anthropic", "Claude", "GPT",
    "BERT", "Transformers", "Hugging Face", "LLM", "Embeddings",
    "SentenceTransformer", "FAISS", "Pinecone", "Weaviate", "Chroma",
    "Vector Database", "Retrieval Augmented Generation",
    # MLOps
    "MLflow", "DVC", "Weights & Biases", "Kubeflow", "Airflow",
]

WEB_FRAMEWORKS: List[str] = [
    "FastAPI", "Django", "Flask", "Node.js", "Express", "React", "Next.js",
    "Vue.js", "Angular", "Svelte", "GraphQL", "REST API", "gRPC",
    "Spring Boot", "Laravel", "Ruby on Rails", "ASP.NET", "Streamlit",
    "Gradio", "Celery",
]

DATABASES: List[str] = [
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "Snowflake", "BigQuery", "Redshift",
    "Oracle", "SQL Server", "Neo4j", "InfluxDB", "Supabase", "Firebase",
]

CLOUD_DEVOPS: List[str] = [
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "Terraform", "Ansible", "Jenkins", "GitHub Actions", "CI/CD",
    "Linux", "Unix", "Nginx", "Apache", "Helm", "ArgoCD",
    "Serverless", "Lambda", "EC2", "S3", "Cloud Functions", "Vercel",
    "Heroku", "Railway", "DigitalOcean",
]

TOOLS: List[str] = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
    "VS Code", "PyCharm", "IntelliJ", "Postman", "Swagger",
    "Excel", "Tableau", "Power BI", "Looker",
    "Spark", "Hadoop", "Databricks", "Kafka",
    "Playwright", "Selenium", "Pytest", "Jest", "Unit Testing",
    "Figma", "Notion",
]

SOFT_SKILLS: List[str] = [
    "Communication", "Problem Solving", "Leadership", "Project Management",
    "Agile", "Scrum", "Kanban", "Cross-functional", "Collaboration",
]

ALL_SKILLS: List[str] = (
    PROGRAMMING_LANGUAGES + ML_AI + WEB_FRAMEWORKS
    + DATABASES + CLOUD_DEVOPS + TOOLS + SOFT_SKILLS
)

# Build case-insensitive canonical lookup
_SKILL_MAP: dict[str, str] = {s.lower(): s for s in ALL_SKILLS}

# Aliases — common abbreviations mapped to canonical names
ALIASES: dict[str, str] = {
    "sklearn": "scikit-learn",
    "nlp": "Natural Language Processing",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "k8s": "Kubernetes",
    "tf": "TensorFlow",
    "hf": "Hugging Face",
    "llms": "LLM",
    "gcp": "Google Cloud",
    "ci/cd": "CI/CD",
    "rest": "REST API",
    "pytorch": "PyTorch",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "spacy": "NLP",
    "langchain": "LangChain",
    "openai api": "OpenAI",
    "rag": "RAG",
    "faiss": "FAISS",
    "react.js": "React",
    "reactjs": "React",
    "nodejs": "Node.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "golang": "Go",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "elastic": "Elasticsearch",
    "huggingface": "Hugging Face",
    "sentence transformer": "SentenceTransformer",
    "sentence-transformer": "SentenceTransformer",
    "github action": "GitHub Actions",
    "xgb": "XGBoost",
    "lgbm": "LightGBM",
}


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from resume text using case-insensitive word-boundary matching.

    Returns a sorted, deduplicated list of canonical skill names.
    No API key or model required — fully deterministic.
    """
    found: set[str] = set()
    text_lower = text.lower()

    # Check canonical skills
    for skill_lower, canonical in _SKILL_MAP.items():
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, text_lower):
            found.add(canonical)

    # Check aliases
    for alias, canonical in ALIASES.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text_lower):
            found.add(canonical)

    return sorted(found)


def normalize_skill(skill: str) -> str:
    """Return the canonical form of a skill name."""
    sl = skill.lower().strip()
    return _SKILL_MAP.get(sl) or ALIASES.get(sl) or skill


def get_skill_category(skill: str) -> str:
    """Return the category of a skill."""
    s = normalize_skill(skill)
    if s in PROGRAMMING_LANGUAGES:
        return "Programming Language"
    if s in ML_AI:
        return "ML / AI"
    if s in WEB_FRAMEWORKS:
        return "Web Framework"
    if s in DATABASES:
        return "Database"
    if s in CLOUD_DEVOPS:
        return "Cloud / DevOps"
    if s in TOOLS:
        return "Tool"
    return "Other"
