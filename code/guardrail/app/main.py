from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class GuardrailRequest(BaseModel):
    text: str

# Palavras proibidas (exemplo acadêmico)
BANNED_KEYWORDS = ["bomb", "explosive", "hack", "ddos", "malware", "virus"]

# Padrões de prompt injection
INJECTION_PATTERNS = [
    r"ignore.*(instruções|instructions|instrucoes|prompts?)",
    r"revele.*(seu|o|your)?\s*(prompt|sistema|system)",
    r"reveal.*?(?:your|the)?\s*(?:prompt|system)",
    r"jailbreak",
    r"bypass",
    r"você agora (é|sera|vai ser)",
    r"you are now",
    r"disregard.*(previous|anterior|all)",
    r"forget (all|everything|todas?)",
    r"desconsidere.*(anterior|anteriores|tudo)",
]

def detect_injection(text: str) -> tuple[bool, str]:
    """Detecta padrões de prompt injection."""
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return True, f"Prompt injection detectado: padrão '{pattern}'"
    return False, ""

def detect_banned_keywords(text: str) -> tuple[bool, str]:
    """Detecta palavras proibidas."""
    lowered = text.lower()
    for kw in BANNED_KEYWORDS:
        if kw in lowered:
            return True, f"Palavra proibida detectada: '{kw}'"
    return False, ""

def apply_guardrails(text: str):
    """
    Aplica guardrails ao texto:
    1. Detecta prompt injection
    2. Detecta palavras proibidas
    3. Remove dados sensíveis (emails, CPFs)
    """
    

    is_injection, injection_reason = detect_injection(text)
    if is_injection:
        return {
            "allowed": False,
            "reason": f"Conteúdo bloqueado: {injection_reason}",
            "safe_output": None
        }
    
    has_banned, banned_reason = detect_banned_keywords(text)
    if has_banned:
        return {
            "allowed": False,
            "reason": f"Conteúdo bloqueado: {banned_reason}",
            "safe_output": None
        }

    cleaned = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL_REMOVED]", text)
    cleaned = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF_REMOVED]", cleaned)

    return {
        "allowed": True,
        "reason": "Conteúdo aprovado pelos guardrails",
        "safe_output": cleaned
    }

@app.get("/")
def root():
    return {"message": "GuardRail running", "status": "healthy"}

@app.post("/check")
def check_guardrail(req: GuardrailRequest):
    """
    Verifica se o texto passa pelos guardrails:
    - Detecta prompt injection
    - Detecta palavras proibidas
    - Remove dados sensíveis
    """
    return apply_guardrails(req.text)
