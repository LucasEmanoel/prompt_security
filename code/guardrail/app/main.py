from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from typing import Optional

app = FastAPI(title="Input GuardRail API")

class GuardrailRequest(BaseModel):
    text: str

# Padrões de prompt injection (EXPANDIDOS)
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|anterior|earlier)\s+(instructions?|prompts?|commands?|instrucoes)",
    r"ignore\s+(your|the)\s+(instructions?|prompts?|commands?)",
    r"disregard\s+(all\s+)?(previous|anterior|earlier|your|the)",
    r"forget\s+(your|all|everything|all\s+previous)\s+(programming|instructions?|commands?|rules)",
    r"act\s+as\s+(if\s+)?(you|an)\s+(are\s+)?(unrestricted|unfiltered|uncensored)",
    r"you\s+are\s+now\s+(in\s+)?(developer|admin|god|root)\s+mode",
    r"bypass\s+(your|the|all)?\s*(filters?|restrictions?|safety|guidelines?)",
    r"override\s+(your|the|all)?\s*(safety|security|filters?|restrictions?)",
    r"new\s+instructions?:\s*ignore",
    r"system\s+prompt\s*(override|reset|change)",
    r"reveal\s+(your|the)\s+system\s+prompt",
    r"what\s+(are|were)\s+your\s+(original|initial)\s+instructions",
]

# Palavras proibidas (EXPANDIDAS)
FORBIDDEN_WORDS = [
    "hack", "hacking", "hacker", "crack", "cracking",
    "exploit", "exploiting", "vulnerability",
    "ddos", "dos attack",
    "malware", "virus", "trojan", "ransomware",
    "phish", "phishing", "spoof", "spoofing",
    "keylogger", "backdoor", "rootkit",
    "sql injection", "xss", "csrf",
    "brute force", "bruteforce",
    "password crack", "crack password",
    "steal data", "data breach",
    "illegal", "crime", "criminal activity",
    "bomb", "explosive", "weapon", "terrorism",
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
    for kw in FORBIDDEN_WORDS:
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
