"""
Orquestrador principal da análise de métricas de guardrails.
Coordena a execução de cálculos, visualizações e relatórios.
"""

import json
from pathlib import Path
from typing import Dict

from metrics_calculator import MetricsCalculator
from plot_generator import PlotGenerator
#from report_generator import ReportGenerator


class GuardrailMetricsAnalyzer:
    """Orquestrador principal que coordena análise completa de guardrails."""
    
    def __init__(self, test_report_path: str = "results/test_report.json"):
        self.test_report_path = Path(test_report_path)
        self.report_data = None
        self.metrics_calculator = None
        self.plot_generator = None
        #self.report_generator = None
    
    def load_report(self) -> Dict:
        """Carrega relatório de testes."""
        if not self.test_report_path.exists():
            raise FileNotFoundError(f"Relatório não encontrado: {self.test_report_path}")
        
        with open(self.test_report_path, 'r', encoding='utf-8') as f:
            self.report_data = json.load(f)
        
        print(f"[OK] Relatorio carregado: {len(self.report_data.get('results', []))} testes")
        return self.report_data
    
    def _initialize_components(self):
        """Inicializa componentes auxiliares."""
        self.metrics_calculator = MetricsCalculator(self.report_data)
        self.plot_generator = PlotGenerator(self.test_report_path.parent)
        #self.report_generator = ReportGenerator(self.test_report_path.parent)

    def run_complete_analysis(self):
        """Executa análise completa dos guardrails."""
        print("\n[>>] INICIANDO ANALISE COMPLETA DOS GUARDRAILS\n")
        
        # 1. Carregar dados
        self.load_report()
        
        # 2. Inicializar componentes
        self._initialize_components()
        
        # 3. Calcular métricas
        print("\n[>>] Calculando metricas...")
        overall_metrics = self.analyze_overall()
        category_metrics = self.analyze_by_category()
        
        # 4. Gerar visualizações
        print("\n[>>] Gerando visualizacoes...")
        self.plot_generator.plot_confusion_matrix(
            overall_metrics['confusion_matrix'],
            "Matriz de Confusão Geral"
        )
        self.plot_generator.plot_metrics_comparison(
            {k: v for k, v in category_metrics.items()}
        )
        self.plot_generator.plot_response_time_distribution(self.report_data)
        self.plot_generator.plot_success_rate_by_category(self.report_data)
        
        # 5. Gerar tabela resumo
        print("\n[>>] Gerando tabela resumo...")
        summary_table = self.generate_summary_table(overall_metrics, category_metrics)
        
        # Salvar tabela em CSV
        #self.report_generator.save_summary_table(summary_table)
        
        # Imprimir tabela no console
        print("\n" + "="*80)
        print("TABELA RESUMO DAS METRICAS")
        print("="*80)
        print(summary_table.to_string(index=False))
        
        # 6. Gerar interpretação
        #print("\n[>>] Gerando interpretacao dos resultados...")
        #interpretation = self.interpret_results(overall_metrics, category_metrics)
        
        # Salvar interpretação
        #self.report_generator.save_interpretation(interpretation)
        
        # Imprimir interpretação
        #print("\n" + interpretation)
        
        # 7. Salvar métricas detalhadas
        #self.report_generator.save_detailed_metrics(overall_metrics, category_metrics, summary_table)
        
        print("\n[OK] ANALISE COMPLETA FINALIZADA!\n")


def main():
    analyzer = GuardrailMetricsAnalyzer(
        test_report_path="results/test_report.json"
    )
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
