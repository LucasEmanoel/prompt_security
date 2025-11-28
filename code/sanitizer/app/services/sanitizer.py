from .normalizer import normalize

def sanitize(prompt: str):
    """
    Apenas normaliza e limpa o texto.
    Não faz detecção de injection - isso é feito pelo GuardRail.
    """
    clean = normalize(prompt)
    return clean, "ok"
