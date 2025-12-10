"""
Script para enviar casos de teste para os serviços de guardrail.
Coleta resultados e gera relatório consolidado.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class GuardrailTester:
    def __init__(self, test_data_path: str = "results/test_data.json"):
        self.test_data_path = Path(test_data_path)
        self.services = {
            'sanitizer': 'http://localhost:8000',
            'guardrail': 'http://localhost:6000',
            'bias_guardrail': 'http://localhost:5000',
            'output_guardrail': 'http://localhost:4000',
            'orchestrator': 'http://localhost:7000'
        }
        self.test_data = None
        self.results = []
    
    def load_test_data(self):
        """Carrega os dados de teste"""
        if not self.test_data_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.test_data_path}")
        
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        
        print(f"[OK] {self.test_data['metadata']['total_cases']} casos de teste carregados")
    
    def test_prompt(self, test_case: Dict) -> Dict:
        result = {
            'test_case': test_case,
            'timestamp': datetime.now().isoformat(),
            'result': {},
            'response_time': 60,
            'errors': [],
            'http_status': None
        }
        
        start_time = time.time()
        
        try:
            category = test_case.get('category', '')
            
            if category.startswith('bias'):
                response = requests.post(
                    f"{self.services['bias_guardrail']}/validate",
                    json={'prompt': test_case['prompt']},
                    timeout=60
                )
                result['http_status'] = response.status_code

                # TODO: ajustar
                if response.status_code == 200:
                    # Status 200 = sem bias detectado
                    data = response.json()
                    result['result'] = data
                    is_valid = data.get('valid', True)
                    result['result']['bias_detected'] = not is_valid
                    result['result']['blocked'] = not is_valid
                    result['result']['success'] = True
                elif response.status_code == 422:
                    # Status 422 = bias detectado (SUCESSO na detecção!)
                    data = response.json()
                    detail = data.get('detail', {})
                    is_valid = detail.get('valid', False)
                    
                    result['result'] = {
                        'valid': is_valid,
                        'bias_detected': not is_valid,
                        'blocked': not is_valid,
                        'success': True,
                        'error': detail.get('error', '')
                    }
                    result['http_status'] = 200  # Normalizar para análise
                else:
                    result['result'] = {'success': False, 'blocked': False}
                    result['errors'].append(f'HTTP {response.status_code}: {response.text}')
            
            elif category in ['pii_email', 'pii_cpf', 'pii_phone', 'pii_credit_card', 'pii_ssn']:
                response = requests.post(
                    f"{self.services['sanitizer']}/sanitize",
                    json={'prompt': test_case['prompt']},
                    timeout=60
                )
                result['http_status'] = response.status_code
                
                if response.status_code == 200:
                    data = response.json()
                    result['result'] = data
                    original = test_case['prompt']
                    sanitized = data.get('sanitized_prompt', original)
                    result['result']['sanitized'] = original != sanitized
                    result['result']['success'] = True
                else:
                    result['result'] = {'success': False, 'sanitized': False}
                    result['errors'].append(f'HTTP {response.status_code}: {response.text}')
            
            elif category in ['sql_injection', 'xss']:
                response = requests.post(
                    f"{self.services['guardrail']}/check",
                    json={'text': test_case['prompt']},
                    timeout=60
                )
                result['http_status'] = response.status_code
                
                if response.status_code == 200:
                    data = response.json()
                    result['result'] = data
                    # Marcar como sucesso se allowed
                    result['result']['success'] = data.get('allowed', True)
                elif response.status_code == 422:
                    # Injection detectado
                    result['result'] = {'success': False, 'blocked': True, 'injection_detected': True}
                    result['errors'].append(f'Injection detected: {response.text}')
                else:
                    result['result'] = {'success': False, 'blocked': True}
                    result['errors'].append(f'HTTP {response.status_code}: {response.text}')
            
            else:
                # Testar orchestrator (jailbreak, malicious, benign)
                response = requests.post(
                    f"{self.services['orchestrator']}/process",
                    json={'prompt': test_case['prompt']},
                    timeout=10
                )
                result['http_status'] = response.status_code
                
                if response.status_code == 200:
                    result['result'] = response.json()
                    result['result']['success'] = True
                elif response.status_code == 422:
                    # Prompt bloqueado
                    result['result'] = {'success': False, 'blocked': True}
                    result['errors'].append(f'Prompt blocked: {response.text}')
                elif response.status_code == 500:
                    # Erro interno
                    result['result'] = {'success': False, 'error': 'internal_server_error'}
                    result['errors'].append(f'Internal server error: {response.text}')
                else:
                    result['result'] = {'success': False, 'blocked': True}
                    result['errors'].append(f'HTTP {response.status_code}: {response.text}')
        
        except requests.exceptions.Timeout:
            result['errors'].append('Timeout na requisição')
            result['result'] = {'success': False, 'error': 'timeout', 'blocked': False}
        
        except requests.exceptions.RequestException as e:
            result['errors'].append(f'Erro na requisição: {str(e)}')
            result['result'] = {'success': False, 'error': str(e), 'blocked': False}
        
        except json.JSONDecodeError:
            result['errors'].append('Erro ao decodificar resposta JSON')
            result['result'] = {'success': False, 'error': 'invalid_json', 'blocked': False}
        
        result['response_time'] = round(time.time() - start_time, 4)
        
        return result
    
    def run_tests(self):        
        for i, test_case in enumerate(self.test_data['test_cases'], 1):
            
            result = self.test_prompt(test_case)
            self.results.append(result)
            time.sleep(0.2)
    
    def generate_report(self, output_path: str = "results/test_report.json"):
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.results),
                'test_data_source': str(self.test_data_path),
                'services': self.services
            },
            'summary': {
                'total_errors': sum(1 for r in self.results if r['errors']),
                'avg_response_time': round(
                    sum(r['response_time'] for r in self.results) / len(self.results), 4
                ),
                'max_response_time': round(
                    max(r['response_time'] for r in self.results), 4
                ),
                'min_response_time': round(
                    min(r['response_time'] for r in self.results), 4
                )
            },
            'results': self.results
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Relatorio gerado: {output_path.absolute()}")
        print(f"\n[>>] RESUMO:")
        print(f"   Total de testes: {report['metadata']['total_tests']}")
        print(f"   Erros: {report['summary']['total_errors']}")
        print(f"   Tempo medio: {report['summary']['avg_response_time']}s")
        print(f"   Tempo maximo: {report['summary']['max_response_time']}s")
        print(f"   Tempo minimo: {report['summary']['min_response_time']}s")
        
        return output_path
    
    def run(self):
        """Executa o fluxo completo de testes"""
        self.load_test_data()
        self.run_tests()
        
        if not self.results:
            print("\n[!!] ERRO: Nenhum teste foi executado!")
            import sys
            sys.exit(1)
        
        self.generate_report()

def main():
    tester = GuardrailTester(test_data_path="results/test_data.json")
    tester.run()

if __name__ == "__main__":
    main()
