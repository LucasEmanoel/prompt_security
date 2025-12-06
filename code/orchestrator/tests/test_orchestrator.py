"""
Testes unitários para o serviço Orchestrator
Testes simples focados em validação de lógica
Nota: O Orchestrator é principalmente orquestração de APIs,
então testes completos requerem os serviços rodando ou mocks complexos.
Aqui incluímos testes básicos de validação.
"""
import pytest


class TestDataModels:
    """Testes para validação de modelos de dados"""
    
    def test_prompt_request_model(self):
        """Valida estrutura de PromptRequest"""
        from app.main import PromptRequest
        
        # Deve aceitar um prompt válido
        request = PromptRequest(prompt="Olá mundo")
        assert request.prompt == "Olá mundo"
    
    def test_process_response_model(self):
        """Valida estrutura de ProcessResponse"""
        from app.main import ProcessResponse
        
        # Deve aceitar os três campos obrigatórios
        response = ProcessResponse(
            original_prompt="original",
            sanitized_prompt="sanitizado",
            llm_response="resposta LLM"
        )
        assert response.original_prompt == "original"
        assert response.sanitized_prompt == "sanitizado"
        assert response.llm_response == "resposta LLM"


class TestConfiguration:
    """Testes para configurações do serviço"""
    
    def test_service_urls_configured(self):
        """Verifica se as URLs dos serviços estão configuradas"""
        from app.main import SANITIZER_URL, GUARDRAIL_URL
        
        assert SANITIZER_URL is not None
        assert GUARDRAIL_URL is not None
        assert "sanitizer" in SANITIZER_URL.lower()
        assert "guardrail" in GUARDRAIL_URL.lower()
    
    def test_sanitizer_url_has_correct_endpoint(self):
        """Verifica endpoint do sanitizer"""
        from app.main import SANITIZER_URL
        
        assert "/sanitize" in SANITIZER_URL
    
    def test_guardrail_url_has_correct_endpoint(self):
        """Verifica endpoint do guardrail"""
        from app.main import GUARDRAIL_URL
        
        assert "/check" in GUARDRAIL_URL


class TestServiceLogic:
    """Testes de lógica básica do serviço"""
    
    def test_service_has_process_endpoint(self):
        """Verifica que o endpoint /process existe"""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert "/process" in routes
    
    def test_service_has_root_endpoint(self):
        """Verifica que o endpoint raiz existe"""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert "/" in routes
    
    def test_app_has_correct_title(self):
        """Verifica o título da aplicação"""
        from app.main import app
        
        assert app.title == "Orchestrator API"


class TestWorkflowLogic:
    """Testes conceituais do fluxo de trabalho"""
    
    def test_workflow_steps_definition(self):
        """Documenta as etapas esperadas do workflow"""
        # Este teste serve como documentação do fluxo esperado
        expected_steps = [
            "1. Receber prompt do usuário",
            "2. Enviar para Sanitizer (limpeza)",
            "3. Enviar para GuardRail (validação)",
            "4. Se aprovado: processar com LLM",
            "5. Retornar resposta"
        ]
        
        # Verifica que temos as URLs configuradas para as etapas
        from app.main import SANITIZER_URL, GUARDRAIL_URL
        
        assert SANITIZER_URL is not None  # Etapa 2
        assert GUARDRAIL_URL is not None  # Etapa 3
        # Etapas 1, 4 e 5 estão no endpoint /process
    
    def test_required_dependencies_importable(self):
        """Verifica que as dependências necessárias estão disponíveis"""
        # FastAPI
        import fastapi
        assert fastapi is not None
        
        # HTTPx para requisições assíncronas
        import httpx
        assert httpx is not None
        
        # Pydantic para validação
        import pydantic
        assert pydantic is not None


class TestErrorHandling:
    """Testes relacionados a tratamento de erros"""
    
    def test_http_exception_available(self):
        """Verifica que HTTPException está disponível para erros"""
        from fastapi import HTTPException
        
        # Deve conseguir criar uma exceção de timeout
        exc = HTTPException(status_code=504, detail="Timeout")
        assert exc.status_code == 504
        assert "Timeout" in exc.detail
    
    def test_service_unavailable_exception(self):
        """Verifica exceção para serviço indisponível"""
        from fastapi import HTTPException
        
        exc = HTTPException(status_code=503, detail="Serviço indisponível")
        assert exc.status_code == 503
    
    def test_bad_request_exception(self):
        """Verifica exceção para requisição inválida"""
        from fastapi import HTTPException
        
        exc = HTTPException(status_code=400, detail="Conteúdo bloqueado")
        assert exc.status_code == 400

