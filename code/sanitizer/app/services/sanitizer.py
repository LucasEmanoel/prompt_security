from .normalizer import normalize

def sanitize(prompt: str):
    """
    Apenas normaliza e limpa o texto.
    """
    clean = normalize(prompt)
    return clean, "ok"
