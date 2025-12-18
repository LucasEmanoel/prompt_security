
from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    prompt: str
    category: str
    http_response: str = None
    expected_outcome: str = None