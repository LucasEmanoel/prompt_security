from .normalizer import normalize
from .injection_detector import detect_prompt_injection

def sanitize(prompt: str):
    clean = normalize(prompt)

    if detect_prompt_injection(clean):
        return None, "blocked"

    return clean, "ok"
