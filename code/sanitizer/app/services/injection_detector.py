import re

PATTERNS = [
    r"ignore.*(todas|as).*instru[cç]([oõ]|ões|oes)",
    r"revele.*(seu|o).*(prompt|sistema)",
    r"jailbreak",
    r"bypass",
    r"voc[eê].*(agora|now).*[eé]",
]

def detect_prompt_injection(text: str) -> bool:
    for p in PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False
