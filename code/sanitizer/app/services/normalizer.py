import unicodedata
import re

def normalize(text: str):
    text = re.sub(r'[\u200B-\u200F\u202A-\u202E]', '', text)
    text = unicodedata.normalize("NFKC", text)
    return text[:3000]
