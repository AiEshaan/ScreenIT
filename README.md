# ScreenIT

---

### 🏆 Rooman Technologies – 24-Hour AI Agent Challenge
* **Category:** Category 1 – People & HR
* **Selected Agent:** Resume Screening Agent
* **Project Name:** ScreenIT – AI Resume Screening Platform

---

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![OpenRouter](https://img.shields.io/badge/OpenRouter-Hybrid_AI-6C47FF?logo=openai&logoColor=white)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-all--MiniLM--L6--v2-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

![Dashboard](docs/screenshots/dashboard.png)

### AI Resume Intelligence Platform

Explainable AI-Powered Resume Screening Agent

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

ScreenIT is an AI-powered **Resume Screening Agent** (Category 1 – People & HR) that automatically parses resumes, extracts structured candidate information, performs semantic matching against job descriptions using SentenceTransformers, ranks candidates with an explainable scoring engine, and generates recruiter-ready AI summaries through a hybrid LLM routing system with automatic fallback and offline resilience.

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
Parser (PDF/DOCX/TXT → Regex + LLM enhance)
   ↓
Context Builder (Structured JSON facts)
   ↓
Embeddings (SentenceTransformer, cached)
   ↓
Ranking Engine (Semantic 50% + Skills 25% + Exp 15% + Edu 10%)
   ↓
AI Orchestrator (OpenRouter cascade → Offline fallback)
   ↓
Recruiter Brief + Interview Questions
   ↓
React Dashboard (Analytics, History, Comparison, Export)
```

## 🏗️ Architecture Diagram

```mermaid
graph TD
    A[Recruiter] --> B[Upload JD + Resumes]
    B --> C[Resume Parser\nPDF / DOCX / TXT]
    C --> D[Context Builder\nStructured JSON]
    D --> E[Embedding Engine\nSentenceTransformer + Cache]
    E --> F[Ranking Engine\nSemantic + Skills + Exp + Edu]
    F --> G[AI Orchestrator]
    G --> H{OpenRouter Cascade}
    H -->|Primary| I[GPT-OSS 120B]
    H -->|Fallback 1| J[Qwen3 80B]
    H -->|Fallback 2| K[Llama 3.3 70B]
    H -->|Fallback 3| L[Gemma 2 27B]
    H -->|Offline| M[Rule Engine]
    I & J & K & L & M --> N[Recruiter Brief\n+ Interview Questions]
    N --> O[React Dashboard\nAnalytics · History · Export]
```

---

## Screenshots & Platform Tour

| 🖥️ Dashboard Page | 📂 Start New Screening |
| :---: | :---: |
| ![Dashboard](docs/screenshots/dashboard.png) | ![New Screening](docs/screenshots/new-screening.png) |
| **⚡ Resume Parsing Progress** | **⚙️ AI Provider & Routing Settings** |
| ![Resume Parsing](docs/screenshots/resume-parsing.png) | ![Setting](docs/screenshots/setting.png) |
| **🗒️ Campaign History Log** | **🔍 Scored Candidate Assessment** |
| ![History Log](docs/screenshots/history-log.png) | ![Resume Agent Output](docs/screenshots/resume-agent-output.png) |

---

## 🎯 Live AI Screening Results

Real output produced by ScreenIT — candidates ranked with explainable scores, AI recruiter briefs, and skill gap analysis.

| Result View 1 | Result View 2 | Result View 3 |
| :---: | :---: | :---: |
| ![Result 1](docs/results/results-1.png) | ![Result 2](docs/results/results-2.png) | ![Result 3](docs/results/results-3.png) |

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
git clone https://github.com/AiEshaan/ScreenIT.git
cd ScreenIT
```

2. **Configure Environment**
Create `.env` in the root:

```env
OPENROUTER_API_KEY=your_api_key_here
```
*(All provider keys and routing default configurations are managed dynamically through the platform Settings UI and stored locally).*

---

## Quick Start

Launch the entire stack using the root launcher:

```bash
./start.bat
```

- **Frontend:** `http://localhost:5173`
- **Backend APIs:** `http://localhost:8000/docs`

The platform will run in production mode connecting directly to the FastAPI server and your local SQLite database.

---

## API Endpoints

```http
POST   /api/screen                  # Create campaign and parse resumes
GET    /api/runs                    # Get all campaigns
GET    /api/runs/{id}               # Get detailed campaign report
DELETE /api/runs/{id}               # Delete campaign run and candidates (cascade)
DELETE /api/candidates/{id}         # Delete candidate profile
PATCH  /api/candidates/{id}         # Update candidate metadata or brief
GET    /api/analytics               # Get dynamic database analytics
GET    /api/settings/models         # Fetch active OpenRouter models (free vs paid)
GET    /api/settings/keys           # Get provider keys configuration status
POST   /api/settings/keys           # Save custom provider API key to .env
GET    /api/settings/routing        # Retrieve task cascade orders
POST   /api/settings/routing        # Update task routing priorities
POST   /api/settings/test-key       # Validate provider API credentials
GET    /api/settings/health         # Get database & embedding statuses
```

---

## Model Routing Strategy & Resiliency

The system uses a **Cascading AI Orchestrator** to route tasks to priority models via OpenRouter:

- **Grouped Model Configurations**: Choose dynamically between free-tier models and paid models (GPT-4o Mini, Claude 3 Haiku, Gemini 2.5 Flash) directly in the UI.
- **429 Rate Limit Recovery**: Implements an automatic exponential backoff retry loop (sleeps 2s/4s) when hitting OpenRouter free tier rate limits before failing over to the next priority.
- **Offline Rule Engine**: If all configured cascade models fail, it falls back to a deterministic offline parser and scoring system to complete the task successfully.

---

## Explainability

Every recommendation includes:

- Semantic Similarity Match (Local vector match)
- Skill Match (Direct keyword intersection)
- Experience Match (Required years vs candidate years)
- Education Match (Degree hierarchy validation)
- Why Ranked (AI justification)
- Recruiter Brief (Executive summary)
- AI Confidence & Model telemetry metadata (Model used + Latency)

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

**Infrastructure & Deployment**
- 🐳 Docker Compose — one-command setup for backend + frontend + DB
- ☁️ Cloud Deployment — Frontend on Vercel, Backend on Railway/Fly.io
- 🗄️ PostgreSQL — swap SQLite for production-grade database
- ⚡ Redis + Celery — background job queue with real-time WebSocket updates
- 🔐 JWT Authentication — recruiter login and multi-user support
- 📦 S3-compatible resume storage (AWS S3 / Cloudflare R2)

**AI & Intelligence**
- 🧠 Fine-tuned embedding model trained on recruitment domain data
- 🔄 Continuous learning from recruiter accept/reject feedback
- 📊 Advanced analytics with cohort analysis and hiring funnel metrics
- 🤖 Interview scheduling agent integration

**Product Features**
- 🌐 ATS Integrations — Greenhouse, Lever, Workday
- 💬 Candidate Chat — AI-powered candidate Q&A interface
- 🌍 Multi-language resume support
- 📋 Collaborative team screening with recruiter notes
- 🔔 Email/Slack notification pipeline for shortlist alerts

**Engineering**
- ✅ Automated test suite — pytest + Playwright E2E
- 🚀 GitHub Actions CI/CD pipeline
- 📈 Prometheus + Grafana observability stack

---

## Contributors

Eshaan

---

## License

MIT License
