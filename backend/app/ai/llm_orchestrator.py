# backend/app/ai/llm_orchestrator.py
import os
import re
import json
import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from openai import OpenAI
from app.db.sqlite import get_routing_prefs
from app.core.config import SettingsManager

logger = logging.getLogger(__name__)

# Map provider IDs to model names used by OpenRouter
PROVIDER_MODELS = {
    "openai": "openai/gpt-oss-120b:free",
    "qwen": "qwen/qwen3-next-80b-a3b-instruct:free",
    "anthropic": "meta-llama/llama-3.3-70b-instruct:free", # Using llama-3.3 on OpenRouter as our Anthropic/conversational provider since it's free tier
    "gemini": "google/gemma-4-31b:free",
}

class AIOrchestrator:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"

    def _get_client(self, provider: str) -> Optional[OpenAI]:
        key = SettingsManager.get_provider_key(provider)
        if not key:
            # Fall back to general openrouter key if specific provider key is not set
            key = SettingsManager.get_provider_key("openrouter")
        if not key:
            return None
        try:
            return OpenAI(api_key=key, base_url=self.base_url)
        except Exception as exc:
            logger.warning(f"Could not create OpenAI client for {provider}: {exc}")
            return None

    def _call_model(
        self,
        provider: str,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Tuple[str, float]]:
        """
        Attempts to call a provider model. Returns (content, latency) or None.
        """
        client = self._get_client(provider)
        if not client:
            return None
            
        model = PROVIDER_MODELS.get(provider)
        if not model:
            return None

        start_time = time.time()
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
            latency = round(time.time() - start_time, 2)
            content = response.choices[0].message.content if response.choices else None
            if content:
                return content.strip(), latency
            return None
        except Exception as exc:
            logger.warning(f"⚠️ Provider {provider} ({model}) failed: {exc}")
            return None

    def call(
        self,
        task: str,
        prompt: str,
        system: str = "You are a helpful AI assistant.",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Routes the LLM call through the task cascade.
        Returns:
            {
                "content": str or None,
                "model_used": str,
                "latency": float
            }
        """
        # Fetch cascade from SQLite
        try:
            prefs = get_routing_prefs()
            cascade = prefs.get(task, prefs.get("default", ["openai", "qwen", "anthropic", "gemini", "offline"]))
        except Exception as exc:
            logger.warning(f"Failed to fetch routing preferences: {exc}")
            cascade = ["openai", "qwen", "anthropic", "gemini", "offline"]

        for provider in cascade:
            if provider == "offline":
                logger.info("Using offline rule engine fallback.")
                return {"content": None, "model_used": "Offline Rule Engine", "latency": 0.0}

            res = self._call_model(provider, system, prompt, max_tokens, temperature)
            if res:
                content, latency = res
                model_name = PROVIDER_MODELS.get(provider, provider)
                logger.info(f"✅ [{task}] answered by {provider} ({model_name}) in {latency}s")
                return {
                    "content": content,
                    "model_used": f"{provider.upper()} ({model_name.split('/')[-1]})",
                    "latency": latency
                }
                
        # All failed
        return {"content": None, "model_used": "Offline Rule Engine", "latency": 0.0}

    def call_json(
        self,
        task: str,
        prompt: str,
        system: str = "You are a helpful AI assistant. Always respond with valid JSON.",
        max_tokens: int = 1500,
        temperature: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Attempts JSON parsing on routed response content.
        """
        res = self.call(task, prompt, system, max_tokens, temperature)
        if not res["content"]:
            return res

        raw = res["content"]
        # Strip markdown fences
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean.strip())
        
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            clean = match.group(0)

        try:
            res["json_data"] = json.loads(clean)
        except json.JSONDecodeError as exc:
            logger.warning(f"⚠️ JSON parse failed for {res['model_used']}: {exc}. Content: {raw[:200]}")
            res["json_data"] = None
            
        return res
