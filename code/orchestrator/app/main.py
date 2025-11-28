from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Orchestrator API")

SANITIZER_URL = "http://sanitizer:8000/sanitize"
GUARDRAIL_URL = "http://guardrail:6000/check"
BIAS_GUARDRAIL_URL = "http://bias_guardrail:5000/validate"
OUTPUT_GUARDRAIL_URL = "http://output_guardrail:4000/validate"

class PromptRequest(BaseModel):
    prompt: str
    llm_response: str

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
    
    unregex_prompt = guardrail_data.get("safe_output", clean_prompt)

    try:
        async with httpx.AsyncClient() as client:
            bias_guardrail_resp = await client.post(
                BIAS_GUARDRAIL_URL,
                json={"prompt": unregex_prompt},
                timeout=10.0
            )
            bias_guardrail_data = bias_guardrail_resp.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Timeout ao comunicar com o Bias GuardRail"
        )

    if not bias_guardrail_data.get("valid", False):
        raise HTTPException(
            status_code=400, 
            detail=bias_guardrail_data.get("error", "Conteúdo bloqueado pelo bias guardrail")
        )
    
    safe_input_prompt = bias_guardrail_data.get("prompt", clean_prompt)

    # Resposta padrão fake de LLM
    llm_response = "Azure is a cloud computing service created by Microsoft. It's a significant competitor to AWS."

    # Caso um valor customizado seja passado como parâmetro altera (para testes do output guardrail)
    if req.llm_response:
        llm_response = req.llm_response

    try:
        async with httpx.AsyncClient() as client:
            #faz chamada para serviço de output guardrail
            out_guardrail_resp = await client.post(
                OUTPUT_GUARDRAIL_URL,
                json={"prompt": llm_response},
                timeout=10.0
            )
            out_guardrail_data = out_guardrail_resp.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Timeout ao comunicar com o Output GuardRail"
        )

    #caso o output guardrail lançe erro, barra a resposta
    if not out_guardrail_data.get("valid", False):
        raise HTTPException(
            status_code=400, 
            detail=out_guardrail_data.get("error", "Conteúdo bloqueado pelo output guardrail")
        )
    
    # Retorna a resposta processada
    return ProcessResponse(
        original_prompt=req.prompt,
        sanitized_prompt=safe_input_prompt,
        llm_response=llm_response
    )
