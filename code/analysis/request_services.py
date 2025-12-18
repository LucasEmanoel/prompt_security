import json
import sys
import csv
import requests
import time
from pathlib import Path
from datetime import datetime

from contracts.Input import TestCase
from contracts.Output import TestResult

def garantir_dir():
    script_dir = Path(__file__).parent
    data_path = script_dir / "data"
    results_path = script_dir / "results"
    
    data_path.mkdir(parents=True, exist_ok=True)
    results_path.mkdir(parents=True, exist_ok=True)
    
    return data_path, results_path

class GuardrailTester:
    def __init__(self):
        self.data_dir, self.results_dir = garantir_dir()

        self.services = {
            "sanitizer": "http://localhost:8000",
            "guardrail": "http://localhost:6000",
            "bias_guardrail": "http://localhost:5000",
            "output_guardrail": "http://localhost:4000",
            "orchestrator": "http://localhost:7000",
        }
        self.test_cases = []
        self.results = []

    def load_test_data(self):
        csv_files = {
            "benign_prompts.csv",
            "jailbreak_attempts.csv",
            "malicious_prompts.csv",
            "pii_prompts.csv",
            "biased_prompts.csv",
        }

        for csv_file in csv_files:
            filepath = self.data_dir / csv_file
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        count = 0
                        for row in reader:
                            test_case = TestCase(
                                id=row.get("id", ""),
                                prompt=row.get("prompt", ""),
                                category=row.get("category", ""),
                                http_response=row.get("http_response"),
                                expected_outcome=row.get("expected_outcome"),
                            )
                            self.test_cases.append(test_case)
                            count += 1
                    print(f"[OK] Carregados {count} testes de {csv_file}")
                except Exception as e:
                    print(f"[!!] Erro ao carregar {csv_file}: {e}")

        print(f"\n[OK] Total de {len(self.test_cases)} casos de teste carregados")

    def test_prompt(self, test_case: TestCase) -> TestResult:
        start_time = time.time()
        http_status = None
        result_data = {}
        actual_outcome = None
        test_passed = False

        try:
            if test_case.category == "pii":
                print(
                    f"\n[>>] Testando PII: {test_case.id}, Category: {test_case.category}"
                )
                response = requests.post(
                    f"{self.services['sanitizer']}/sanitize",
                    json={"prompt": test_case.prompt},
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    actual_output = data.get("clean_prompt", test_case.prompt)
                    test_passed = actual_output == test_case.expected_outcome
                    result_data = {
                        "success": test_passed,
                        "sanitized": test_case.prompt != actual_output,
                        **data,
                    }
                    actual_outcome = actual_output
                else:
                    result_data = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                    }
                    actual_outcome = None

                http_status = response.status_code

            else:
                expected_http = int(
                    test_case.http_response
                    or (200 if test_case.category == "benign" else 422)
                )
                print(
                    f"\n[>>] Testando Orchestrator: {test_case.id}, Category: {test_case.category}"
                )
                response = requests.post(
                    f"{self.services['orchestrator']}/process",
                    json={"prompt": test_case.prompt},
                    timeout=10,
                )

                http_status = response.status_code
                test_passed = http_status == expected_http
                actual_outcome = str(http_status)

                if http_status == 200:
                    result_data = response.json()
                    result_data["success"] = True
                elif http_status == 422:
                    result_data = {"success": False, "blocked": True}
                elif http_status == 500:
                    result_data = {"success": False, "error": "internal_server_error"}
                else:
                    result_data = {"success": False}

        except requests.exceptions.Timeout:
            http_status = None
            result_data = {"success": False, "error": "timeout"}
            actual_outcome = "timeout"
        except requests.exceptions.RequestException as e:
            http_status = None
            result_data = {"success": False, "error": str(e)}
            actual_outcome = str(e)
        except json.JSONDecodeError:
            http_status = None
            result_data = {"success": False, "error": "invalid_json"}
            actual_outcome = "invalid_json"
        except Exception as e:
            http_status = None
            result_data = {"success": False, "error": str(e)}
            actual_outcome = str(e)

        print(
            f"\n[>>] Resultado do teste {test_case.id}: Passed={test_passed}, HTTP Status={http_status}, Response Time={round(time.time() - start_time, 4)}s"
        )

        return TestResult(
            test_case=test_case,
            timestamp=datetime.now().isoformat(),
            result=result_data,
            response_time=round(time.time() - start_time, 4),
            http_status=http_status,
            actual_outcome=actual_outcome,
            test_passed=test_passed,
        )

    def run_tests(self):
        print("\n[>>] Iniciando execução de testes...")

        for i, test_case in enumerate(self.test_cases, 1):
            result = self.test_prompt(test_case)
            self.results.append(result)
            time.sleep(0.2)

            if i % 10 == 0:
                print(f"[>>] {i}/{len(self.test_cases)} testes executados...")

        print(f"[>>] {len(self.test_cases)} testes completados!")

    def generate_csv(self, output_path: str = None):
        if output_path is None:
            script_dir = Path(__file__).parent
            output_path = script_dir / "results" / "test_results.csv"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "id",
                "category",
                "prompt",
                "http_response",
                "expected_outcome",
                "http_status",
                "actual_outcome",
                "test_passed",
                "response_time",
                "timestamp",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                writer.writerow(
                    {
                        "id": result.test_case.id,
                        "category": result.test_case.category,
                        "prompt": result.test_case.prompt,
                        "http_response": result.test_case.http_response,
                        "expected_outcome": result.test_case.expected_outcome,
                        "http_status": result.http_status,
                        "actual_outcome": result.actual_outcome,
                        "test_passed": result.test_passed,
                        "response_time": result.response_time,
                        "timestamp": result.timestamp,
                    }
                )

        return output_path

    def run(self):
        self.load_test_data()

        if not self.test_cases:
            print(f"\n[!!] ERRO CRÍTICO: Nenhum teste foi carregado!")
            print(f"[!!] Abortando execução.")
            sys.exit(1)

        self.run_tests()

        if not self.results:
            print(f"\n[!!] ERRO: Nenhum teste foi executado!")
            sys.exit(1)

        csv_path = self.generate_csv()
        print(f"[OK] Relatório CSV gerado em: {csv_path.absolute()}")

