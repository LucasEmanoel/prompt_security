import subprocess
import sys
from pathlib import Path

def run_step(command, step_name):
    result = subprocess.run(command, shell=True)
    
    if result.returncode == 0:
        print(f"\n[OK] {step_name} concluido!\n")
        return True
    else:
        print(f"\n[!!] {step_name} falhou!\n")
        return False

def check_file(filepath):
    return Path(filepath).exists()

def main():

    if not Path("generate_test_data.py").exists():
        print("[!!] ERRO: Execute este script da pasta 'analysis'")
        sys.exit(1)
    
    
    if not run_step(f"{sys.executable} generate_test_data.py", "Geracao de dados"):
        sys.exit(1)

    if run_step(f"{sys.executable} request_services.py", "Execucao de testes"):
        if check_file("results/test_report.json"):
            print("\n[OK] Testes executados com sucesso!")
        else:
            print("\n[!!] ERRO: Relatorio nao foi gerado.")
            print("   Provavelmente os servicos nao estavam disponiveis.")
            print("   Inicie os servicos e execute novamente o Passo 3.")
            sys.exit(1)
    else:
        print("\n[!!] Erro ao executar testes.")
        sys.exit(1)
    
    if not run_step(f"{sys.executable} analyze_metrics.py", "Analise de metricas"):
        print("\n[!!] Erro ao analisar metricas.")
        sys.exit(1)

if __name__ == "__main__":
    main()
