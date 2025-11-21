from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Orchestrator API")

SANITIZER_URL = "http://sanitizer:8000/sanitize"
GUARDRAIL_URL = "http://guardrail:6000/check"

class PromptRequest(BaseModel):
    prompt: str

class ProcessResponse(BaseModel):
    original_prompt: str
    sanitized_prompt: str
    llm_response: str

@app.get("/")
def root():
    return {"message": "Orchestrator running", "status": "healthy"}

@app.post("/process", response_model=ProcessResponse)
async def process_prompt(req: PromptRequest):
    """
    Processa o prompt do usuário através do pipeline completo:
    1. Sanitizer: Limpa e normaliza o prompt
    2. GuardRail: Verifica prompt injection e palavras proibidas
    3. LLM: Processa o prompt aprovado
    4. Retorna: Resposta do LLM
    """
# Etapa 1: Limpeza e normalização do prompt
    try:
        async with httpx.AsyncClient() as client:
            sanitize_resp = await client.post(
                SANITIZER_URL, 
                json={"prompt": req.prompt},
                timeout=10.0
            )
            sanitize_data = sanitize_resp.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Timeout ao comunicar com o Sanitizer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Erro ao comunicar com o Sanitizer: {str(e)}"
        )
    
    clean_prompt = sanitize_data.get("clean_prompt", req.prompt)
    
    try:
        async with httpx.AsyncClient() as client:
            guardrail_resp = await client.post(
                GUARDRAIL_URL,
                json={"text": clean_prompt},
                timeout=10.0
            )
            guardrail_data = guardrail_resp.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Timeout ao comunicar com o GuardRail"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Erro ao comunicar com o GuardRail: {str(e)}"
        )
    
    if not guardrail_data.get("allowed", False):
        raise HTTPException(
            status_code=400, 
            detail=guardrail_data.get("reason", "Conteúdo bloqueado pelos guardrails")
        )
    
    safe_prompt = guardrail_data.get("safe_output", clean_prompt)
    
    # Etapa 3: Chamada ao LLM (simulado)
    llm_response = f"Resposta gerada pelo LLM para o prompt: '{safe_prompt}'. Esta é uma simulação acadêmica."
    
    # Retorna a resposta processada
    return ProcessResponse(
        original_prompt=req.prompt,
        sanitized_prompt=safe_prompt,
        llm_response=llm_response
    )
