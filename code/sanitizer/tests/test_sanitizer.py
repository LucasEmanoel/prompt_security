"""
Testes unitários para o serviço Sanitizer
Foco em testar a lógica de negócio (funções individuais)
"""
import pytest
from app.services.normalizer import normalize
from app.services.sanitizer import sanitize

class TestNormalizer:
    """Testes para normalização de texto"""
    
    def test_normalize_removes_invisible_characters(self):
        """Remove caracteres invisíveis (zero-width)"""
        text = "Olá\u200Bmundo\u200C"
        result = normalize(text)
        assert "\u200B" not in result
        assert "\u200C" not in result
        assert result == "Olámundo"
    
    def test_normalize_removes_multiple_invisible_chars(self):
        """Remove vários tipos de caracteres invisíveis"""
        text = "A\u200BB\u200CC\u200DD\u202AE"
        result = normalize(text)
        assert result == "ABCDE"
    
    def test_normalize_limits_length_to_3000(self):
        """Limita o texto a 3000 caracteres"""
        long_text = "x" * 5000
        result = normalize(long_text)
        assert len(result) == 3000
    
    def test_normalize_preserves_short_text(self):
        """Preserva texto menor que 3000 caracteres"""
        text = "Texto normal curto"
        result = normalize(text)
        assert result == text
    
    def test_normalize_handles_unicode_normalization(self):
        """Normaliza Unicode (NFKC)"""
        # Caractere com acento decomposto
        text = "café"
        result = normalize(text)
        assert result is not None
        assert "café" in result or "cafe" in result
    
    def test_normalize_empty_string(self):
        """Lida com string vazia"""
        result = normalize("")
        assert result == ""

class TestSanitizerService:
    """Testes para o serviço completo de sanitização"""
    
    def test_sanitize_clean_text(self):
        """Sanitiza texto limpo corretamente"""
        text = "Olá mundo"
        cleaned, status = sanitize(text)
        assert cleaned == "Olá mundo"
        assert status == "ok"
    
    def test_sanitize_removes_invisible_chars(self):
        """Remove caracteres invisíveis durante sanitização"""
        text = "Olá\u200Bmundo"
        cleaned, status = sanitize(text)
        assert "\u200B" not in cleaned
        assert cleaned == "Olámundo"
        assert status == "ok"
    
    def test_sanitize_limits_length(self):
        """Limita tamanho durante sanitização"""
        text = "a" * 5000
        cleaned, status = sanitize(text)
        assert len(cleaned) == 3000
        assert status == "ok"
    
    def test_sanitize_complex_text(self):
        """Sanitiza texto complexo com unicode e caracteres invisíveis"""
        text = "Café\u200B com\u200C açúcar"
        cleaned, status = sanitize(text)
        assert "\u200B" not in cleaned
        assert "\u200C" not in cleaned
        assert status == "ok"
    
    def test_sanitize_always_returns_ok_status(self):
        """Sempre retorna status 'ok' (não valida segurança)"""
        texts = ["normal", "ignore instruções", "jailbreak"]
        for text in texts:
            _, status = sanitize(text)
            assert status == "ok"

