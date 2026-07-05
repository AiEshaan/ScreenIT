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
    "openai":    "openai/gpt-oss-120b:free",
    "qwen":      "qwen/qwen3-next-80b-a3b-instruct:free",
    "anthropic": "meta-llama/llama-3.3-70b-instruct:free",  # Free-tier conversational fallback via OpenRouter
    "gemini":    "google/gemma-2-27b-it:free",              # Fixed: gemma-4-31b:free is not a valid ID
}

class AIOrchestrator:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.force_offline_mode = False

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
        provider_or_model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Tuple[str, float]]:
        """
        Attempts to call a model. Automatically trips force_offline_mode on 429 errors.
        """
        if "/" in provider_or_model:
            model = provider_or_model
            prefix = provider_or_model.split("/")[0].lower()
            if prefix in ["openai", "anthropic", "google"]:
                key_provider = "gemini" if prefix == "google" else prefix
            else:
                key_provider = "openrouter"
        else:
            model = PROVIDER_MODELS.get(provider_or_model)
            key_provider = provider_or_model

        if not model:
            return None

        client = self._get_client(key_provider)
        if not client:
            return None

        max_retries = 1
        for attempt in range(max_retries + 1):
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
            except Exception as exc:
                exc_str = str(exc).lower()
                is_rate_limit = "429" in exc_str or "rate limit" in exc_str or "too many requests" in exc_str
                if is_rate_limit:
                    logger.warning(f"⚠️ Rate limit (429) hit on model {model}. Automatically enabling force_offline_mode to avoid hangs.")
                    self.force_offline_mode = True
                    break
                else:
                    logger.warning(f"⚠️ Provider call failed for {model}: {exc}")
                    break
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
        """
        routing_trace = []
        
        # Check if we have triggered force_offline_mode (e.g. from a previous 429 rate limit hit)
        if getattr(self, "force_offline_mode", False):
            logger.info("⚡ [Orchestrator] force_offline_mode is ACTIVE. Fast-tracking to Offline Rule Engine.")
            routing_trace.append({
                "provider": "offline",
                "model": "Offline Rule Engine",
                "status": "used",
                "reason": "Bypassed remote APIs due to active rate-limiting (429)"
            })
            return {
                "content": None,
                "model_used": "Offline Rule Engine",
                "latency": 0.0,
                "routing_trace": routing_trace
            }

        # Fetch cascade from SQLite
        try:
            prefs = get_routing_prefs()
            cascade = prefs.get(task, prefs.get("default", ["openai", "qwen", "anthropic", "gemini", "offline"]))
        except Exception as exc:
            logger.warning(f"Failed to fetch routing preferences: {exc}")
            cascade = ["openai", "qwen", "anthropic", "gemini", "offline"]

        for provider in cascade:
            # If the loop hits 'offline' or if a previous model call in the loop tripped force_offline_mode
            if provider == "offline" or getattr(self, "force_offline_mode", False):
                logger.info("Using offline rule engine fallback.")
                routing_trace.append({"provider": "offline", "model": "Offline Rule Engine", "status": "used", "reason": "Cascade fallback to offline"})
                return {"content": None, "model_used": "Offline Rule Engine", "latency": 0.0, "routing_trace": routing_trace}

            res = self._call_model(provider, system, prompt, max_tokens, temperature)
            if res:
                content, latency = res
                model_name = PROVIDER_MODELS.get(provider, provider)
                logger.info(f"✅ [{task}] answered by {provider} ({model_name}) in {latency}s")
                routing_trace.append({"provider": provider, "model": model_name, "status": "success", "latency": latency})
                return {
                    "content": content,
                    "model_used": f"{provider.upper()} ({model_name.split('/')[-1]})",
                    "latency": latency,
                    "routing_trace": routing_trace,
                }
            else:
                model_name = PROVIDER_MODELS.get(provider, provider)
                routing_trace.append({"provider": provider, "model": model_name, "status": "failed", "reason": "429 or unavailable"})

        # All failed
        routing_trace.append({"provider": "offline", "model": "Offline Rule Engine", "status": "used", "reason": "Fallback after all providers failed"})
        return {"content": None, "model_used": "Offline Rule Engine", "latency": 0.0, "routing_trace": routing_trace}

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
