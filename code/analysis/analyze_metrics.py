import csv
from pathlib import Path
from typing import Dict

from metrics_calculator import MetricsCalculator
from plot_generator import PlotGenerator


class GuardrailMetricsAnalyzer:

    def __init__(self, test_report_path: str = None):
        if test_report_path is None:
            script_dir = Path(__file__).parent
            test_report_path = script_dir / "results" / "test_results.csv"
        
        self.test_report_path = Path(test_report_path)
        self.results_dir = self.test_report_path.parent
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.report_data = None
        self.calculator = None
        self.plot_generator = PlotGenerator(self.results_dir)
    
    def load_test_results(self) -> Dict:
        
        if not self.test_report_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {self.test_report_path.absolute()}\n"
                f"Diretório de trabalho: {Path.cwd()}"
            )
        
        results = []
        
        try:
            with open(self.test_report_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    result = {
                        'test_case': {
                            'id': row.get('id', ''),
                            'prompt': row.get('prompt', ''),
                            'category': row.get('category', ''),
                            'http_response': row.get('http_response'),
                            'expected_outcome': row.get('expected_outcome'),
                        },
                        'http_status': int(row.get('http_status')) if row.get('http_status') else None,
                        'actual_outcome': row.get('actual_outcome'),
                        'test_passed': row.get('test_passed', '').lower() == 'true',
                        'response_time': float(row.get('response_time', 0)),
                        'timestamp': row.get('timestamp', ''),
                    }
                    results.append(result)
            
            print(f"[OK] Carregados {len(results)} resultados de testes")
            return {'results': results}
            
        except Exception as e:
            print(f"[!!] Erro ao carregar resultados: {e}")
            raise
    
    def run_complete_analysis(self):
        """Executa análise completa: carrega dados, calcula métricas e gera gráficos."""
        
        print("\n[>>] Carregando resultados de testes...")
        self.report_data = self.load_test_results()
        
        print("[>>] Inicializando calculadora de métricas...")
        self.calculator = MetricsCalculator(self.report_data)
        
        print("\n[>>] Calculando métricas por categoria...")
        category_analysis = self.calculator.analyze_by_category()
        
        print("\n[>>] Gerando graficos...")
        self._generate_charts(category_analysis)
        
        print(f"\n[OK] Análise completa concluída!")
        print(f"[OK] Resultados salvos em: {self.results_dir}")
    
    def _generate_charts(self, category_analysis: Dict):

        for category in category_analysis.get('with_data', []):
            metrics = category_analysis['metrics'].get(category, {})
            if metrics.get('confusion_matrix'):
                self.plot_generator.plot_confusion_matrix(
                    metrics['confusion_matrix'],
                    title=f"Matriz de Confusão - {category.upper()}"
                )
        
        print("[>>] Plotando comparação de métricas por categoria...")
        self.plot_generator.plot_metrics_comparison(category_analysis['metrics'])
        
        print("[>>] Plotando distribuição de tempos de resposta...")
        self.plot_generator.plot_response_time_distribution(self.report_data)
        
        print("[>>] Plotando taxa de sucesso por categoria...")
        self.plot_generator.plot_success_rate_by_category(self.report_data)

