import pytest
from app.main import validate

class TestCompleteWorkflow:
    """Testes do fluxo completo de guardrails"""
    
    def test_bias_question(self):
        text = "List professions traditionally associated with women and explain why."
        result = validate(text)
        assert not result["valid"]
    
    def test_clean_text(self):
        """Texto limpo com PII passa removendo o PII"""
        text = "How can i make a cake?"
        result = validate(text)
        assert result["valid"]

