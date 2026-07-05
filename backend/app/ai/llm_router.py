# backend/app/llm_router.py
#
# Task-aware LLM Router for ScreenIt
# ----------------------------------
# Each task uses the best available model for that task type.
# If a model fails, it automatically falls back down the chain.
# If all models fail, the caller falls back to the local rule engine.
#
# Priority ladder (by task):
#   PARSING     → Qwen3 Next 80B  → GPT-OSS 120B → Llama 3.3 70B → Gemma 4
#   SUMMARY     → GPT-OSS 120B   → Qwen3 Next   → Llama 3.3 70B → Gemma 4
#   QUESTIONS   → Llama 3.3 70B  → GPT-OSS 120B → Qwen3 Next    → Gemma 4
#   DEFAULT     → GPT-OSS 120B   → Qwen3 Next   → Llama 3.3 70B → Gemma 4

import os
import re
import json
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMTask(str, Enum):
    """
    Identifies the task type so the router can pick the optimal model.
    - PARSING   : Structured extraction from resume text (Qwen excels)
    - SUMMARY   : Recruiter briefs, Why Ranked, Confidence reasoning (GPT-OSS)
    - QUESTIONS : Interview question generation (Llama, conversational quality)
    - DEFAULT   : Any other task (GPT-OSS as primary)
    """
    PARSING   = "parsing"
    SUMMARY   = "summary"
    QUESTIONS = "questions"
    DEFAULT   = "default"


# ── Model registry ──────────────────────────────────────────────────────────
# Listed from strongest/most capable to lightweight fallback.
# All are :free tier on OpenRouter — one API key covers all of them.

_GPT_OSS    = "openai/gpt-oss-120b:free"          # Best overall reasoning + JSON
_QWEN3      = "qwen/qwen3-next-80b-a3b-instruct:free"  # Best for structured extraction
_LLAMA      = "meta-llama/llama-3.3-70b-instruct:free" # Best conversational NLP
_GEMMA4_31  = "google/gemma-4-31b:free"            # Solid lightweight backup
_GEMMA4_27  = "google/gemma-3-27b-it:free"         # Final fallback before offline

# ── Task → model priority mapping ───────────────────────────────────────────
TASK_MODELS: Dict[LLMTask, List[str]] = {
    LLMTask.PARSING: [
        _QWEN3,       # Best: structured JSON extraction from long text
        _GPT_OSS,     # Fallback 1
        _LLAMA,       # Fallback 2
        _GEMMA4_31,   # Fallback 3
        _GEMMA4_27,   # Fallback 4
    ],
    LLMTask.SUMMARY: [
        _GPT_OSS,     # Best: nuanced reasoning, recruiter-quality prose
        _QWEN3,       # Fallback 1
        _LLAMA,       # Fallback 2
        _GEMMA4_31,   # Fallback 3
        _GEMMA4_27,   # Fallback 4
    ],
    LLMTask.QUESTIONS: [
        _LLAMA,       # Best: conversational, natural interview questions
        _GPT_OSS,     # Fallback 1
        _QWEN3,       # Fallback 2
        _GEMMA4_31,   # Fallback 3
        _GEMMA4_27,   # Fallback 4
    ],
    LLMTask.DEFAULT: [
        _GPT_OSS,
        _QWEN3,
        _LLAMA,
        _GEMMA4_31,
        _GEMMA4_27,
    ],
}


class LLMRouter:
    """
    Wraps OpenRouter with task-aware model selection and automatic failover.

    Usage:
        router = LLMRouter()

        # Recruiter summary — will try GPT-OSS 120B first
        text = router.call(task=LLMTask.SUMMARY, prompt="...", system="...")

        # Structured JSON extraction — will try Qwen3 first
        data = router.call_json(task=LLMTask.PARSING, prompt="...", system="...")

    If OPENROUTER_API_KEY is not set OR all models fail, call() returns None
    and call_json() returns None so the caller can use its local fallback.
    """

    def __init__(self):
        self.api_key  = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.base_url = "https://openrouter.ai/api/v1"
        self._client: Optional[OpenAI] = None

    # ── Internal ─────────────────────────────────────────────────────────────

    def _get_client(self) -> Optional[OpenAI]:
        if not self.api_key:
            return None
        if self._client is None:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except Exception as exc:
                logger.warning(f"Could not create OpenAI client: {exc}")
                return None
        return self._client

    def _call_model(
        self,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[str]:
        """
        Single model attempt. Returns content string or None on failure.
        """
        client = self._get_client()
        if not client:
            return None
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content if response.choices else None
            return content.strip() if content else None
        except Exception as exc:
            logger.warning(f"⚠️  {model} failed: {exc}")
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    def call(
        self,
        prompt: str,
        system: str = "You are a helpful AI assistant.",
        task: LLMTask = LLMTask.DEFAULT,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> Optional[str]:
        """
        Call the best available model for the given task type.
        Returns the response text, or None if all models fail / no API key.
        """
        models = TASK_MODELS.get(task, TASK_MODELS[LLMTask.DEFAULT])
        for model in models:
            result = self._call_model(model, system, prompt, max_tokens, temperature)
            if result:
                logger.info(f"✅  [{task.value}] answered by {model.split('/')[1]}")
                return result
        logger.warning(f"🔴  All models failed for task={task.value}. Using offline fallback.")
        return None

    def call_json(
        self,
        prompt: str,
        system: str = "You are a helpful AI assistant. Always respond with valid JSON.",
        task: LLMTask = LLMTask.DEFAULT,
        max_tokens: int = 1500,
        temperature: float = 0.05,
    ) -> Optional[Dict[str, Any]]:
        """
        Call the best available model and parse the response as JSON.
        Uses a tighter temperature for deterministic structured output.
        Returns a parsed dict, or None if parsing fails or all models fail.
        """
        raw = self.call(
            prompt=prompt,
            system=system,
            task=task,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if not raw:
            return None

        # Strip markdown code fences that some models add (```json ... ```)
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean.strip())

        # Try to extract JSON object if there's surrounding prose
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            clean = match.group(0)

        try:
            return json.loads(clean)
        except json.JSONDecodeError as exc:
            logger.warning(f"⚠️  JSON parse failed: {exc}. Raw: {raw[:200]}")
            return None

    # ── Convenience shortcuts (used by engine.py) ─────────────────────────────

    def recruiter_brief(self, prompt: str) -> Optional[str]:
        """Generate a recruiter-quality prose summary — GPT-OSS 120B first."""
        return self.call(
            prompt=prompt,
            system=(
                "You are an expert technical recruiter. "
                "Write concise, direct recruiter briefs. "
                "No bullet spam. Use short paragraphs. Max 4 sentences."
            ),
            task=LLMTask.SUMMARY,
            max_tokens=400,
            temperature=0.2,
        )

    def interview_questions(self, prompt: str) -> Optional[str]:
        """Generate targeted interview questions — Llama 3.3 70B first."""
        return self.call(
            prompt=prompt,
            system=(
                "You are a senior hiring manager. "
                "Generate 3–5 specific, behavioural interview questions. "
                "Focus on skill gaps and role requirements. "
                "Return as a JSON array of strings."
            ),
            task=LLMTask.QUESTIONS,
            max_tokens=600,
            temperature=0.3,
        )

    def extract_skills(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Extract structured skills data from resume text — Qwen3 first."""
        return self.call_json(
            prompt=prompt,
            system=(
                "You are a resume parsing AI. "
                "Extract structured data from the resume. "
                "Always return valid JSON with keys: "
                "skills (list), experience_years (int), education (string), "
                "summary (string, 1 sentence)."
            ),
            task=LLMTask.PARSING,
            max_tokens=800,
            temperature=0.05,
        )
