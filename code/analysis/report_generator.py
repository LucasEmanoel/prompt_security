"""
Módulo para geração de relatórios e interpretação de resultados.
Responsável por criar tabelas, interpretações textuais e análises.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict


class ReportGenerator:
    """Gera relatórios, tabelas e interpretações de resultados."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def generate_summary_table(self, overall_metrics: Dict, category_metrics: Dict) -> pd.DataFrame:
        """
        Gera tabela resumo das métricas.
        
        Args:
            overall_metrics: Métricas gerais
            category_metrics: Métricas por categoria
        
        Returns:
            DataFrame com resumo das métricas
        """
        data = []
        
        # Adicionar métricas gerais
        data.append({
            'Categoria': 'GERAL',
            'Precisão': f"{overall_metrics['precision']:.2%}",
            'Recall': f"{overall_metrics['recall']:.2%}",
            'F1-Score': f"{overall_metrics['f1_score']:.2%}",
            'Acurácia': f"{overall_metrics['accuracy']:.2%}",
            'FPR': f"{overall_metrics['fpr']:.2%}",
            'FNR': f"{overall_metrics['fnr']:.2%}"
        })
        
        # Adicionar métricas por categoria
        for category, metrics in sorted(category_metrics.items()):
            cm = metrics.get('confusion_matrix', {})
            total = cm.get('total', 0)
            
            if total == 0:
                data.append({
                    'Categoria': f"{category} *",
                    'Precisão': "N/A",
                    'Recall': "N/A",
                    'F1-Score': "N/A",
                    'Acurácia': "N/A",
                    'FPR': "N/A",
                    'FNR': "N/A"
                })
            else:
                data.append({
                    'Categoria': category,
                    'Precisão': f"{metrics['precision']:.2%}",
                    'Recall': f"{metrics['recall']:.2%}",
                    'F1-Score': f"{metrics['f1_score']:.2%}",
                    'Acurácia': f"{metrics['accuracy']:.2%}",
                    'FPR': f"{metrics['fpr']:.2%}",
                    'FNR': f"{metrics['fnr']:.2%}"
                })
        
        return pd.DataFrame(data)
    
    def save_summary_table(self, summary_table: pd.DataFrame):
        """
        Salva tabela resumo em CSV.
        
        Args:
            summary_table: DataFrame com resumo das métricas
        """
        csv_path = self.output_dir / "metrics_summary.csv"
        summary_table.to_csv(csv_path, index=False)
        print(f"[>>] Tabela salva: {csv_path}")
        return csv_path
    
    def interpret_results(self, overall_metrics: Dict, category_metrics: Dict) -> str:
        """
        Gera interpretação textual dos resultados.
        
        Args:
            overall_metrics: Métricas gerais
            category_metrics: Métricas por categoria
        
        Returns:
            String com interpretação completa
        """
        lines = []
        
        lines.extend(self._interpret_general(overall_metrics))
        lines.extend(self._interpret_tradeoffs(overall_metrics))
        lines.extend(self._interpret_by_category(category_metrics))
        lines.extend(self._interpret_performance(overall_metrics))
        lines.extend(self._interpret_recommendations(overall_metrics, category_metrics))
        
        return "\n".join(lines)
    
    def save_interpretation(self, interpretation: str):
        """
        Salva interpretação em arquivo.
        
        Args:
            interpretation: Texto da interpretação
        """
        interpretation_path = self.output_dir / "analysis_interpretation.txt"
        with open(interpretation_path, 'w', encoding='utf-8') as f:
            f.write(interpretation)
        print(f"[>>] Interpretacao salva: {interpretation_path}")
        return interpretation_path
    
    def save_detailed_metrics(self, overall_metrics: Dict, category_metrics: Dict, 
                             summary_table: pd.DataFrame):
        """
        Salva métricas detalhadas em JSON.
        
        Args:
            overall_metrics: Métricas gerais
            category_metrics: Métricas por categoria
            summary_table: DataFrame com resumo
        """
        from datetime import datetime
        
        metrics_output = {
            'timestamp': datetime.now().isoformat(),
            'overall_metrics': overall_metrics,
            'category_metrics': category_metrics,
            'summary_table': summary_table.to_dict('records')
        }
        
        metrics_path = self.output_dir / "detailed_metrics.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_output, f, indent=2, ensure_ascii=False)
        print(f"[>>] Metricas detalhadas salvas: {metrics_path}")
        return metrics_path
    
    @staticmethod
    def _interpret_general(overall_metrics: Dict) -> list:
        """Interpreta análise geral do sistema."""
        lines = []
        lines.append("=" * 80)
        lines.append("INTERPRETAÇÃO DOS RESULTADOS - ANÁLISE DE GUARDRAILS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("1. ANÁLISE GERAL DO SISTEMA")
        lines.append("-" * 80)
        
        accuracy = overall_metrics['accuracy']
        precision = overall_metrics['precision']
        recall = overall_metrics['recall']
        
        lines.append(f"Acurácia Geral: {accuracy:.2%}")
        if accuracy >= 0.9:
            lines.append("✅ EXCELENTE: O sistema demonstra alta eficácia geral.")
        elif accuracy >= 0.7:
            lines.append("⚠️  BOM: O sistema funciona bem, mas há espaço para melhorias.")
        else:
            lines.append("❌ NECESSITA MELHORIAS: A eficácia do sistema está abaixo do ideal.")
        
        lines.append("")
        lines.append(f"Precisão: {precision:.2%}")
        if precision >= 0.9:
            lines.append("✅ Poucos falsos positivos - usuários legítimos raramente são bloqueados.")
        elif precision >= 0.7:
            lines.append("⚠️  Alguns falsos positivos - usuários legítimos ocasionalmente bloqueados.")
        else:
            lines.append("❌ Muitos falsos positivos - experiência do usuário pode ser prejudicada.")
        
        lines.append("")
        lines.append(f"Recall (Sensibilidade): {recall:.2%}")
        if recall >= 0.9:
            lines.append("✅ Excelente detecção de ameaças - poucas ameaças passam despercebidas.")
        elif recall >= 0.7:
            lines.append("⚠️  Boa detecção, mas algumas ameaças podem passar.")
        else:
            lines.append("❌ CRÍTICO: Muitas ameaças não estão sendo detectadas.")
        
        lines.append("")
        lines.append(f"F1-Score: {overall_metrics['f1_score']:.2%}")
        lines.append(f"(Equilíbrio entre Precisão e Recall)")
        
        return lines
    
    @staticmethod
    def _interpret_tradeoffs(overall_metrics: Dict) -> list:
        """Interpreta trade-offs do sistema."""
        lines = []
        lines.append("")
        lines.append("2. ANÁLISE DE TRADE-OFFS")
        lines.append("-" * 80)
        
        fpr = overall_metrics['fpr']
        fnr = overall_metrics['fnr']
        
        lines.append(f"Taxa de Falsos Positivos (FPR): {fpr:.2%}")
        lines.append(f"Taxa de Falsos Negativos (FNR): {fnr:.2%}")
        lines.append("")
        
        if fpr < 0.1 and fnr < 0.1:
            lines.append("✅ ÓTIMO: Bom equilíbrio entre segurança e usabilidade.")
        elif fpr > fnr:
            lines.append("⚠️  Sistema está mais RESTRITIVO (bloqueia demais).")
            lines.append("   Impacto: Pode frustrar usuários legítimos.")
            lines.append("   Recomendação: Considerar relaxar algumas regras.")
        else:
            lines.append("⚠️  Sistema está mais PERMISSIVO (deixa passar demais).")
            lines.append("   Impacto: Ameaças podem não ser detectadas.")
            lines.append("   Recomendação: Fortalecer regras de detecção.")
        
        return lines
    
    @staticmethod
    def _interpret_by_category(category_metrics: Dict) -> list:
        """Interpreta performance por categoria."""
        lines = []
        lines.append("")
        lines.append("3. ANÁLISE POR CATEGORIA")
        lines.append("-" * 80)
        
        weak_categories = []
        strong_categories = []
        
        for category, metrics in category_metrics.items():
            if metrics['f1_score'] < 0.7:
                weak_categories.append((category, metrics))
            elif metrics['f1_score'] >= 0.9:
                strong_categories.append((category, metrics))
        
        if strong_categories:
            lines.append("✅ CATEGORIAS COM BOA PERFORMANCE:")
            for cat, metrics in strong_categories:
                lines.append(f"   • {cat}: F1={metrics['f1_score']:.2%}, Acc={metrics['accuracy']:.2%}")
        
        lines.append("")
        
        if weak_categories:
            lines.append("❌ CATEGORIAS QUE NECESSITAM ATENÇÃO:")
            for cat, metrics in weak_categories:
                lines.append(f"   • {cat}: F1={metrics['f1_score']:.2%}, Acc={metrics['accuracy']:.2%}")
                
                if metrics['precision'] < metrics['recall']:
                    lines.append(f"     → Problema: Muitos falsos positivos")
                else:
                    lines.append(f"     → Problema: Muitos falsos negativos (ameaças não detectadas)")
        
        return lines
    
    @staticmethod
    def _interpret_performance(overall_metrics: Dict) -> list:
        """Interpreta performance do sistema."""
        lines = []
        lines.append("")
        lines.append("4. ANÁLISE DE PERFORMANCE")
        lines.append("-" * 80)
        
        avg_time = overall_metrics.get('avg_response_time', 0)
        max_time = overall_metrics.get('max_response_time', 0)
        
        lines.append(f"Tempo Médio de Resposta: {avg_time:.3f}s")
        lines.append(f"Tempo Máximo de Resposta: {max_time:.3f}s")
        lines.append("")
        
        if avg_time < 0.5:
            lines.append("✅ Excelente latência - não impacta experiência do usuário.")
        elif avg_time < 1.0:
            lines.append("⚠️  Latência aceitável, mas pode ser otimizada.")
        else:
            lines.append("❌ Latência alta - pode impactar negativamente a experiência.")
        
        return lines
    
    @staticmethod
    def _interpret_recommendations(overall_metrics: Dict, category_metrics: Dict) -> list:
        """Gera recomendações."""
        lines = []
        lines.append("")
        lines.append("5. RECOMENDAÇÕES")
        lines.append("-" * 80)
        
        recall = overall_metrics['recall']
        precision = overall_metrics['precision']
        avg_time = overall_metrics.get('avg_response_time', 0)
        
        weak_categories = [c for c, m in category_metrics.items() if m['f1_score'] < 0.7]
        
        recommendations = []
        
        if recall < 0.8:
            recommendations.append("• URGENTE: Melhorar detecção de ameaças (baixo recall)")
            recommendations.append("  - Adicionar mais padrões de detecção")
            recommendations.append("  - Revisar regras que podem estar muito permissivas")
        
        if precision < 0.8:
            recommendations.append("• Reduzir falsos positivos")
            recommendations.append("  - Refinar padrões para evitar bloqueios excessivos")
            recommendations.append("  - Implementar whitelist para casos conhecidos")
        
        if weak_categories:
            recommendations.append(f"• Focar melhorias nas categorias: {', '.join(weak_categories)}")
        
        if avg_time > 0.5:
            recommendations.append("• Otimizar performance do sistema")
            recommendations.append("  - Considerar cache de resultados")
            recommendations.append("  - Paralelizar checagens independentes")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando dentro dos parâmetros esperados!")
            recommendations.append("• Manter monitoramento contínuo")
            recommendations.append("• Atualizar base de ameaças regularmente")
        
        lines.extend(recommendations)
        lines.append("")
        lines.append("=" * 80)
        
        return lines
