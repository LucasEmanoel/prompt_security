import re

PATTERNS = [
    r"ignore (todas|as) instruções",
    r"revele seu prompt",
    r"jailbreak",
    r"bypass",
    r"você agora é",
]

def detect_prompt_injection(text: str) -> bool:
    for p in PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False
