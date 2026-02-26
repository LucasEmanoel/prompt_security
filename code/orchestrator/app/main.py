import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Orchestrator API")

SANITIZER_URL = "http://sanitizer:8000/sanitize"
GUARDRAIL_URL = "http://guardrail:6000/check"
BIAS_GUARDRAIL_URL = "http://bias_guardrail:5000/validate"
OUTPUT_GUARDRAIL_URL = "http://output_guardrail:4000/validate"

class PromptRequest(BaseModel):
    prompt: Optional[str] = None
    llm_response: Optional[str] = None

class ProcessResponse(BaseModel):
    original_prompt: Optional[str] = None
    sanitized_prompt: Optional[str] = None
    llm_response: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Orchestrator running", "status": "healthy"}

@app.post("/process", response_model=ProcessResponse)
async def process_prompt(req: PromptRequest):
    logger.info("Received request: %s", req.dict())

    # Se nenhum prompt fornecido, usa vazio
    original_prompt = req.prompt or ""
    clean_prompt = original_prompt

    logger.info("Original prompt: %s", original_prompt)

    # TA SEM ESSE ENDPOINT
    # Etapa 1: Limpeza e normalização (opcional)
    # if original_prompt:
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             sanitize_resp = await client.post(
    #                 SANITIZER_URL, 
    #                 json={"prompt": original_prompt},
    #                 timeout=10.0
    #             )
    #             sanitize_data = sanitize_resp.json()
    #             clean_prompt = sanitize_data.get("clean_prompt", original_prompt)
    #             logger.info("Sanitized prompt: %s", clean_prompt)
    #     except httpx.TimeoutException:
    #         logger.error("Timeout ao comunicar com o Sanitizer")
    #         raise HTTPException(
    #             status_code=504, 
    #             detail="Timeout ao comunicar com o Sanitizer"
    #         )
    #     except Exception as e:
    #         logger.error("Erro ao comunicar com o Sanitizer: %s", str(e))
    #         raise HTTPException(
    #             status_code=503, 
    #             detail=f"Erro ao comunicar com o Sanitizer: {str(e)}"
    #         )

    unregex_prompt = clean_prompt

    # Etapa 2: GuardRail (opcional)
    if clean_prompt:
        try:
            logger.info("Sending prompt to GuardRail: %s", clean_prompt)
            async with httpx.AsyncClient() as client:
                guardrail_resp = await client.post(
                    GUARDRAIL_URL,
                    json={"text": clean_prompt},
                    timeout=60.0
                )
                guardrail_data = guardrail_resp.json()
                logger.info("GuardRail response: %s", guardrail_data)

        except httpx.TimeoutException:
            logger.error("Timeout ao comunicar com o GuardRail")
            raise HTTPException(
                status_code=504, 
                detail="Timeout ao comunicar com o GuardRail"
            )
        
        except Exception as e:
            logger.error("Erro ao comunicar com o GuardRail: %s", str(e))
            raise HTTPException(
                status_code=503, 
                detail=f"Erro ao comunicar com o GuardRail: {str(e)}"
            )
        
        if not guardrail_data.get("allowed", True):
            logger.warning("GuardRail blocked the prompt: %s", guardrail_data.get("reason"))
            raise HTTPException(
                status_code=422, 
                detail=guardrail_data.get("reason", "Conteúdo bloqueado pelos guardrails")
            )
        
        unregex_prompt = guardrail_data.get("safe_output", clean_prompt)

    safe_input_prompt = unregex_prompt

    logger.info("Prompt após GuardRail: %s", safe_input_prompt)

    # Etapa 3: Bias GuardRail (opcional)
    if unregex_prompt:
        try:
            logger.info("Sending prompt to Bias GuardRail: %s", unregex_prompt)
            async with httpx.AsyncClient() as client:
                bias_guardrail_resp = await client.post(
                    BIAS_GUARDRAIL_URL,
                    json={"prompt": unregex_prompt},
                    timeout=240.0
                )
                bias_guardrail_data = bias_guardrail_resp.json()
                logger.info("Bias GuardRail response: %s", bias_guardrail_data)

        except httpx.TimeoutException:
            logger.error("Timeout ao comunicar com o Bias GuardRail")
            raise HTTPException(
                status_code=504, 
                detail="Timeout ao comunicar com o Bias GuardRail"
            )
        
        except Exception as e:
            logger.error("Erro ao comunicar com o Bias GuardRail: %s", str(e))
            raise HTTPException(
                status_code=503, 
                detail=f"Erro ao comunicar com o Bias GuardRail: {str(e)}"
            )
        
        if not bias_guardrail_data.get("valid", True):
            logger.warning("Bias GuardRail blocked the prompt: %s", bias_guardrail_data.get("error"))
            raise HTTPException(
                status_code=422, 
                detail=bias_guardrail_data.get("error", "Conteúdo bloqueado pelo bias guardrail")
            )
        
        safe_input_prompt = bias_guardrail_data.get("prompt", unregex_prompt)

    # Etapa 4: LLM Response (opcional)
    llm_response = req.llm_response
    
    if llm_response is None:
        llm_response = "Azure is a cloud computing service created by Microsoft. It's a significant competitor to AWS."

    logger.info("LLM response: %s", llm_response)

    # Etapa 5: Output GuardRail (opcional)
    if llm_response:
        try:
            logger.info("Sending LLM response to Output GuardRail: %s", llm_response)
            async with httpx.AsyncClient() as client:
                out_guardrail_resp = await client.post(
                    OUTPUT_GUARDRAIL_URL,
                    json={"prompt": llm_response},
                    timeout=120.0
                )
                out_guardrail_data = out_guardrail_resp.json()
                logger.info("Output GuardRail response: %s", out_guardrail_data)
        except httpx.TimeoutException:
            logger.error("Timeout ao comunicar com o Output GuardRail")
            raise HTTPException(
                status_code=504, 
                detail="Timeout ao comunicar com o Output GuardRail"
            )
        except Exception as e:
            logger.error("Erro ao comunicar com o Output GuardRail: %s", str(e))
            raise HTTPException(
                status_code=503, 
                detail=f"Erro ao comunicar com o Output GuardRail: {str(e)}"
            )

        if not out_guardrail_data.get("valid", True):
            logger.warning("Output GuardRail blocked the response: %s", out_guardrail_data.get("error"))
            raise HTTPException(
                status_code=422, 
                detail=out_guardrail_data.get("error", "Conteúdo bloqueado pelo output guardrail")
            )

    # Retorna a resposta processada
    logger.info("Processed response: original_prompt=%s, sanitized_prompt=%s, llm_response=%s", original_prompt, safe_input_prompt, llm_response)
    return ProcessResponse(
        original_prompt=original_prompt or None,
        sanitized_prompt=safe_input_prompt or None,
        llm_response=llm_response
    )
