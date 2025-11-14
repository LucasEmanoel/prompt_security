from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class LLMResponse(BaseModel):
    text: str

# Palavras proibidas (exemplo acadêmico)
BANNED_KEYWORDS = ["bomba", "explosivo", "hackear", "ddos"]

def apply_guardrails(text: str):
    lowered = text.lower()
    for kw in BANNED_KEYWORDS:
        if kw in lowered:
            return {
                "allowed": False,
                "reason": f"Conteúdo bloqueado: palavra proibida detectada ('{kw}')",
                "safe_output": None
            }

    # Remoção simples de emails e CPFs
    cleaned = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL_REMOVIDO]", text)
    cleaned = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF_REMOVIDO]", cleaned)

    return {
        "allowed": True,
        "reason": "Conteúdo aprovado pelos guardrails",
        "safe_output": cleaned
    }

@app.post("/guardrail")
def guardrail(resp: LLMResponse):
    return apply_guardrails(resp.text)
