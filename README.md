# ScreenIt

![Dashboard](docs/screenshots/dashboard.png)

### AI Recruiter Copilot

Explainable AI Resume Screening Platform

⭐ Semantic Ranking  
⭐ Hybrid AI Routing  
⭐ Explainable Recommendations  
⭐ Recruiter Analytics  
⭐ Interview Guidance  

---

## What is ScreenIt?

### Problem Statement

Recruiters often receive hundreds of resumes for a single position.

Traditional ATS systems rely heavily on keyword matching, causing qualified candidates to be overlooked and making screening slow and inconsistent.

### Solution

ScreenIt solves this by combining semantic understanding, structured resume parsing, explainable ranking, and AI-generated recruiter insights to help hiring teams make faster and more confident hiring decisions.

```text
Recruiter
   ↓
Upload Job Description
   ↓
Upload Resumes
   ↓
Resume Parsing
   ↓
Semantic Ranking
   ↓
Recruiter Brief
   ↓
Shortlist
   ↓
Export
```

---

## Features

- **Semantic Ranking:** Contextual understanding of experience over rigid keyword checks.
- **Hybrid AI Routing:** Smart failover between Qwen3, GPT-OSS, and Llama 3.3.
- **Explainable Recommendations:** Transparent "Why Ranked" metrics and confidence scores.
- **Recruiter Analytics:** Rich hiring insights directly from the candidate pool.
- **Interview Guidance:** Custom interview questions generated based on candidates' specific skill gaps.

---

## Demo

*(Placeholder for 90-second Demo GIF showing the workflow)*
![Demo GIF](docs/demo.gif)

---

## Architecture

![Architecture](docs/architecture.png)

```text
React (Vite, Tailwind, Zustand)
   ↓
FastAPI (REST Endpoints)
   ↓
AI Engine (Orchestration)
   ↓
SentenceTransformer (Local Embeddings)
   ↓
OpenRouter (Multi-Model LLM)
   ↓
SQLite (Persistence)
```

---

## AI Pipeline

![Pipeline](docs/pipeline.png)

```text
Resume
   ↓
Parser
   ↓
Feature Extraction
   ↓
Embedding
   ↓
Similarity
   ↓
Ranking
   ↓
Recruiter Brief
   ↓
Interview Questions
   ↓
Reports
```

---

## Screenshots

### 1. Dashboard

![Dashboard](docs/screenshots/1-dashboard.png)

### 2. New Screening

![New Screening](docs/screenshots/2-new-screening.png)

### 3. Processing

![Processing](docs/screenshots/3-processing.png)

### 4. Candidate Review

![Candidate Review](docs/screenshots/4-candidate-review.png)

### 5. Comparison

![Comparison](docs/screenshots/5-comparison.png)

### 6. Analytics

![Analytics](docs/screenshots/6-analytics.png)

### 7. Settings

![Settings](docs/screenshots/7-settings.png)

---

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, TanStack Query.
- **Backend:** FastAPI, Python 3.13, Pydantic, SQLAlchemy.
- **AI/ML:** SentenceTransformers (`all-MiniLM-L6-v2`), PyMuPDF, OpenRouter API.
- **Database:** SQLite.

---

## Folder Structure

```text
ScreenIt/
├── apps/
│   └── web/                 # React Frontend
├── backend/
│   ├── app/
│   │   ├── ai/              # AI Pipeline Modules
│   │   ├── api/             # FastAPI Routes
│   │   ├── db/              # Database Configuration
│   │   ├── services/        # Orchestration Services
│   │   └── core/            # Config & Settings
│   └── main.py              # Application Entrypoint
├── shared/                  # Schemas & Prompts
├── docs/                    # Diagrams & Media
├── sample_data/             # Resumes & JDs for testing
├── start.bat                # Unified Launcher
├── LICENSE                  # MIT License
└── README.md                # Documentation
```

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/screenit.git
cd screenit
```

1. **Configure Environment**
Create `.env` in the root:

```env
OPENROUTER_API_KEY=your_api_key_here
MODEL_PRIMARY=openai/gpt-oss-120b:free
MODEL_FALLBACK=qwen/qwen3-next-80b-a3b-instruct:free
DATABASE_URL=sqlite:///backend/screenit.db
```

---

## Quick Start

Launch the entire stack using the root launcher:

```bash
./start.bat
```

- **Frontend:** `http://localhost:5173`
- **Backend APIs:** `http://localhost:8000/docs`

*(Note: If the backend is unreachable, the frontend falls back to a fully interactive Demo Mode).*

---

## API Endpoints

```http
POST /api/screen
GET /api/runs
GET /api/runs/{id}
POST /api/compare
GET /api/settings
```

---

## Model Routing Strategy

The system uses task-aware fallback routing to optimize for speed, quality, and reliability across different free-tier models via OpenRouter.

**Resume Parsing Strategy:**

```text
Qwen3 → GPT-OSS → Llama → Gemma → Offline Rules
```

**Recruiter Summary Strategy:**

```text
GPT-OSS → Qwen3 → Llama → Gemma → Offline Templates
```

---

## Explainability

Every recommendation includes:

- Semantic Match
- Skill Match
- Experience Match
- Education Match
- Why Ranked
- Recruiter Brief
- AI Confidence

This allows recruiters to **trust AI recommendations** rather than treating them as a black box.

---

## Engineering Decisions

| Decision            | Why                        |
| ------------------- | -------------------------- |
| **FastAPI**         | Lightweight REST framework |
| **SentenceTransformer** | Offline semantic matching  |
| **OpenRouter**      | Multi-model routing        |
| **SQLite**          | Simple deployment          |
| **React**           | Modern SPA                 |
| **Zustand**         | Lightweight global state   |
| **TanStack Query**  | Smart caching              |
| **Tailwind**        | Fast UI development        |

---

## Tradeoffs

- **SQLite instead of PostgreSQL:** Chosen for zero-setup portability. SQLAlchemy makes swapping to Postgres trivial for production.
- **Synchronous API vs Background Queue:** Currently blocks the HTTP request for simplicity in assessment environments. Production would implement Celery/Redis with WebSocket updates.
- **Local Embeddings:** SentenceTransformers runs locally to eliminate API latency and cost, at the expense of slight initial server boot overhead.
- **OpenRouter Multi-Model:** Used to prevent single-provider rate-limit bottlenecks and to match specific model modalities to tasks (Parsing vs Writing).

---

## Future Roadmap

- ATS Integrations (Greenhouse, Lever)
- Interview Scheduling
- Team Collaboration
- Recruiter Feedback Learning
- Candidate Chat
- Multi-language Support

---

## Contributors

Eshaan

---

## License

MIT License
