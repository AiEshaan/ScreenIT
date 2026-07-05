from app.ai.llm_orchestrator import AIOrchestrator

def test_offline_fallback():
    orchestrator = AIOrchestrator()
    orchestrator.force_offline_mode = True
    
    result = orchestrator.call(
        task="summary",
        prompt="Describe candidate John Doe",
        system="System prompt"
    )
    
    assert result["model_used"] == "Offline Rule Engine"
    assert result["content"] is None
    assert result["latency"] == 0.0
    assert len(result["routing_trace"]) > 0
    assert "rate-limiting" in result["routing_trace"][0]["reason"].lower()
