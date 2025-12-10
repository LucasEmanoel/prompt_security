"""
Módulo para cálculo de métricas de performance e matrizes de confusão.
Responsável por toda lógica de cálculo matemático das métricas.
"""

from typing import Dict, List
import numpy as np


class MetricsCalculator:
    """Calcula métricas de performance baseadas em resultados de teste."""
    
    def __init__(self, report_data: Dict):
        self.report_data = report_data
    
    def calculate_confusion_matrix(self, category: str = None) -> Dict:
        """
        Calcula matriz de confusão (TP, FP, TN, FN).
        
        Args:
            category: Categoria específica para filtrar (None = todas)
        
        Returns:
            Dict com TP, FP, TN, FN e total
        """
        tp = fp = tn = fn = 0
        
        results = self.report_data.get('results', [])
        
        for result in results:
            test_case = result.get('test_case', {})
            actual_result = result.get('result', {})
            http_status = result.get('http_status')
            has_errors = len(result.get('errors', [])) > 0
            
            # Filtrar por categoria se especificado
            if category and test_case.get('category') != category:
                continue
            
            expected = test_case.get('expected_outcome')
            test_category = test_case.get('category')
            
            # Determinar se foi bloqueado/detectado
            is_blocked = self._is_blocked(actual_result, http_status)
            
            # Ignorar casos com erro de servidor (500) para não distorcer métricas
            if http_status == 500 or (has_errors and 'internal_server_error' in str(result.get('errors'))):
                continue
            
            # Classificar resultado
            if test_category == 'benign':
                # Prompts benignos devem passar (negativo)
                if not is_blocked:
                    tn += 1  # Passou corretamente
                else:
                    fp += 1  # Bloqueado incorretamente
            else:
                # Ameaças devem ser bloqueadas (positivo)
                if is_blocked:
                    tp += 1  # Bloqueado corretamente
                else:
                    fn += 1  # Passou incorretamente
        
        return {
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn,
            'total': tp + fp + tn + fn
        }
    
    def calculate_metrics(self, confusion_matrix: Dict) -> Dict:
        """
        Calcula métricas de performance a partir da matriz de confusão.
        
        Args:
            confusion_matrix: Dict com TP, FP, TN, FN
        
        Returns:
            Dict com precision, recall, f1_score, accuracy, specificity, fpr, fnr
        """
        tp = confusion_matrix['tp']
        fp = confusion_matrix['fp']
        tn = confusion_matrix['tn']
        fn = confusion_matrix['fn']
        
        # Evitar divisão por zero
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # False Positive Rate e False Negative Rate
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        return {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'accuracy': round(accuracy, 4),
            'specificity': round(specificity, 4),
            'fpr': round(fpr, 4),
            'fnr': round(fnr, 4),
            'confusion_matrix': confusion_matrix
        }
    
    def calculate_response_time_stats(self) -> Dict:
        """
        Calcula estatísticas de tempo de resposta.
        
        Returns:
            Dict com avg, max, min response time
        """
        results = self.report_data.get('results', [])
        response_times = [r.get('response_time', 0) for r in results]
        
        return {
            'avg_response_time': round(np.mean(response_times), 4) if response_times else 0,
            'max_response_time': round(np.max(response_times), 4) if response_times else 0,
            'min_response_time': round(np.min(response_times), 4) if response_times else 0
        }
    
    def analyze_by_category(self) -> Dict:
        """
        Analisa métricas por categoria de teste.
        
        Returns:
            Dict com métricas para cada categoria
        """
        categories = self._get_all_categories()
        
        category_metrics = {}
        categories_with_data = []
        categories_without_data = []
        
        for category in sorted(categories):
            cm = self.calculate_confusion_matrix(category)
            metrics = self.calculate_metrics(cm)
            category_metrics[category] = metrics
            
            if cm.get('total', 0) > 0:
                categories_with_data.append(category)
            else:
                categories_without_data.append(category)
        
        return {
            'metrics': category_metrics,
            'with_data': categories_with_data,
            'without_data': categories_without_data
        }
    
    def analyze_overall(self) -> Dict:
        """
        Análise geral de todos os testes.
        
        Returns:
            Dict com métricas gerais e tempo de resposta
        """
        cm = self.calculate_confusion_matrix()
        overall_metrics = self.calculate_metrics(cm)
        
        # Adicionar informações de tempo
        time_stats = self.calculate_response_time_stats()
        overall_metrics.update(time_stats)
        
        return overall_metrics
    
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
    
    def _get_all_categories(self) -> set:
        """Extrai todas as categorias dos resultados."""
        categories = set()
        for result in self.report_data.get('results', []):
            cat = result.get('test_case', {}).get('category')
            if cat:
                categories.add(cat)
        return categories
