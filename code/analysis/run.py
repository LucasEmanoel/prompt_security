import sys
from pathlib import Path

from request_services import GuardrailTester
from analyze_metrics import GuardrailMetricsAnalyzer


def check_file(filepath):
    return Path(filepath).exists()

def main():
    print("=" * 80)
    print("PIPELINE DE ANÁLISE DE GUARDRAILS")
    
    print("\n[ETAPA 1] Executando testes de guardrails...")
    try:
        tester = GuardrailTester()
        tester.run()
        print("[OK] Testes executados com sucesso!")
        
    except Exception as e:
        print(f"[!!] Erro ao executar testes: {str(e)}")
        sys.exit(1)
    
    print("\n[ETAPA 2] Analisando métricas...")
    try:
        analyzer = GuardrailMetricsAnalyzer()
        analyzer.run_complete_analysis()
        print("[OK] Análise de métricas concluída!")
        
    except Exception as e:
        print(f"[!!] Erro ao analisar métricas: {str(e)}")
        sys.exit(1)
    
    print("[OK] PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    main()
