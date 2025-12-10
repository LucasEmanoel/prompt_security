"""
Módulo para geração de gráficos e visualizações.
Responsável por toda a renderização visual de dados.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
from collections import defaultdict


class PlotGenerator:
    """Gera gráficos e visualizações dos resultados."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self._setup_style()
    
    @staticmethod
    def _setup_style():
        """Configura estilo dos gráficos."""
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def plot_confusion_matrix(self, confusion_matrix: Dict, title: str = "Matriz de Confusão"):
        """
        Plota matriz de confusão como heatmap.
        
        Args:
            confusion_matrix: Dict com TP, FP, TN, FN
            title: Título do gráfico
        """
        total = confusion_matrix.get('total', 0)
        if total == 0:
            print(f"[!!] Sem dados para plotar matriz de confusão: {title}")
            return
        
        cm_array = np.array([
            [confusion_matrix['tp'], confusion_matrix['fn']],
            [confusion_matrix['fp'], confusion_matrix['tn']]
        ])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm_array, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Predicted Threat', 'Predicted Safe'],
                    yticklabels=['Actual Threat', 'Actual Safe'])
        plt.title(title)
        plt.ylabel('Valor Real')
        plt.xlabel('Valor Predito')
        plt.tight_layout()
        
        output_path = self.output_dir / f"confusion_matrix_{title.replace(' ', '_').lower()}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"[>>] Grafico salvo: {output_path}")
        plt.close()
    
    def plot_metrics_comparison(self, category_metrics: Dict):
        """
        Plota comparação de métricas entre categorias.
        
        Args:
            category_metrics: Dict com métricas por categoria
        """
        if not category_metrics:
            print("[!!] Nenhuma categoria para comparação")
            return
        
        categories = list(category_metrics.keys())
        metrics_names = ['precision', 'recall', 'f1_score', 'accuracy']
        
        data = []
        for metric in metrics_names:
            values = [category_metrics[cat][metric] for cat in categories]
            data.append(values)
        
        x = np.arange(len(categories))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        for i, (metric, values) in enumerate(zip(metrics_names, data)):
            offset = width * (i - 1.5)
            bars = ax.bar(x + offset, values, width, label=metric.replace('_', ' ').title())
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=7)
        
        ax.set_xlabel('Categoria')
        ax.set_ylabel('Score')
        ax.set_title('Comparação de Métricas por Categoria')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / "metrics_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"[>>] Grafico salvo: {output_path}")
        plt.close()
    
    def plot_response_time_distribution(self, report_data: Dict):
        """
        Plota distribuição de tempos de resposta.
        
        Args:
            report_data: Dados completos do relatório
        """
        results = report_data.get('results', [])
        response_times = [r.get('response_time', 0) for r in results]
        categories = [r.get('test_case', {}).get('category', 'unknown') for r in results]
        
        df = pd.DataFrame({
            'response_time': response_times,
            'category': categories
        })
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histograma geral
        ax1.hist(response_times, bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Tempo de Resposta (s)')
        ax1.set_ylabel('Frequência')
        ax1.set_title('Distribuição de Tempos de Resposta')
        ax1.axvline(np.mean(response_times), color='red', linestyle='--', 
                   label=f'Média: {np.mean(response_times):.3f}s')
        ax1.legend()
        
        # Box plot por categoria
        df.boxplot(column='response_time', by='category', ax=ax2)
        ax2.set_xlabel('Categoria')
        ax2.set_ylabel('Tempo de Resposta (s)')
        ax2.set_title('Tempo de Resposta por Categoria')
        plt.sca(ax2)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = self.output_dir / "response_time_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"[>>] Grafico salvo: {output_path}")
        plt.close()
    
    def plot_success_rate_by_category(self, report_data: Dict):
        """
        Plota taxa de sucesso por categoria.
        
        Args:
            report_data: Dados completos do relatório
        """
        results = report_data.get('results', [])
        
        category_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for result in results:
            category = result.get('test_case', {}).get('category', 'unknown')
            expected = result.get('test_case', {}).get('expected_outcome')
            actual = result.get('result', {})
            http_status = result.get('http_status')
            
            is_blocked = self._is_blocked(actual, http_status)
            
            # Considerar sucesso se comportou como esperado
            is_success = (
                (expected in ['block', 'detect'] and is_blocked) or
                (expected == 'pass' and not is_blocked) or
                (expected == 'sanitize' and (actual.get('sanitized', False) or http_status == 200))
            )
            
            category_success[category]['total'] += 1
            if is_success:
                category_success[category]['success'] += 1
        
        if not category_success:
            print("[!!] Nenhuma categoria com dados para plotar taxa de sucesso")
            return
        
        categories = sorted(category_success.keys())
        success_rates = []
        
        for cat in categories:
            total = category_success[cat]['total']
            success = category_success[cat]['success']
            rate = (success / total * 100) if total > 0 else 0
            success_rates.append(rate)
        
        plt.figure(figsize=(16, 6))
        bars = plt.bar(categories, success_rates, color='skyblue', edgecolor='black')
        
        # Colorir barras baseado na taxa de sucesso
        for bar, rate in zip(bars, success_rates):
            if rate >= 90:
                bar.set_color('green')
            elif rate >= 70:
                bar.set_color('orange')
            elif rate > 0:
                bar.set_color('red')
            else:
                bar.set_color('lightgray')
        
        plt.xlabel('Categoria')
        plt.ylabel('Taxa de Sucesso (%)')
        plt.title('Taxa de Sucesso por Categoria')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 110)
        
        # Adicionar valores nas barras
        for i, (cat, rate) in enumerate(zip(categories, success_rates)):
            if rate > 0:
                plt.text(i, rate + 2, f'{rate:.1f}%', ha='center', va='bottom', fontsize=8)
            else:
                plt.text(i, 5, '0.0%', ha='center', va='bottom', fontsize=8, color='red')
        
        plt.axhline(y=90, color='green', linestyle='--', alpha=0.5, label='90% (Excelente)')
        plt.axhline(y=70, color='orange', linestyle='--', alpha=0.5, label='70% (Aceitável)')
        plt.legend()
        
        plt.tight_layout()
        output_path = self.output_dir / "success_rate_by_category.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"[>>] Grafico salvo: {output_path}")
        plt.close()
    
    @staticmethod
    def _is_blocked(actual_result: Dict, http_status: int) -> bool:
        """Determina se uma resposta foi bloqueada/detectada."""
        return (
            http_status in [422, 403] or
            not actual_result.get('success', True) or
            actual_result.get('blocked', False) or
            actual_result.get('bias_detected', False) or
            actual_result.get('injection_detected', False) or
            (http_status == 200 and not actual_result.get('valid', True))
        )
