
from dataclasses import dataclass
from typing import Dict

from .Input import TestCase


@dataclass
class TestResult:
    test_case: TestCase
    timestamp: str
    result: Dict
    response_time: float
    http_status: int
    actual_outcome: str = None
    test_passed: bool = False