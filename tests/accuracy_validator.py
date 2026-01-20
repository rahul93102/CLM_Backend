"""
Phase 5 Testing & Optimization
Accuracy Validation, Performance Optimization, Error Handling
"""

import json
import time
import logging
from typing import Dict, List, Tuple, Optional
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class AccuracyValidator:
    """
    Validates accuracy of AI endpoints
    Tests metadata extraction, search relevance, classification precision
    """
    
    def __init__(self):
        self.test_results = []
    
    # ======== METADATA EXTRACTION VALIDATION ========
    
    def validate_metadata_extraction(self, 
                                    document_text: str,
                                    ground_truth: Dict,
                                    extracted_data: Dict) -> Dict:
        """
        Validate metadata extraction accuracy
        
        Args:
            document_text: Original contract text
            ground_truth: {
                'parties': [{'name': 'Party A', 'role': 'Licensor'}, ...],
                'effective_date': '2024-01-01',
                'contract_value': {'amount': 50000, 'currency': 'USD'}
            }
            extracted_data: What AI extracted
        
        Returns:
            {
                'accuracy': 0.85,
                'party_precision': 0.9,
                'date_accuracy': 1.0,
                'value_accuracy': 0.75,
                'details': {...}
            }
        """
        scores = {}
        
        # Validate parties
        party_score = self._validate_parties(
            ground_truth.get('parties', []),
            extracted_data.get('parties', [])
        )
        scores['party_precision'] = party_score
        
        # Validate dates
        date_score = self._validate_dates(
            ground_truth.get('effective_date'),
            ground_truth.get('termination_date'),
            extracted_data
        )
        scores['date_accuracy'] = date_score
        
        # Validate contract value
        value_score = self._validate_contract_value(
            ground_truth.get('contract_value'),
            extracted_data.get('contract_value')
        )
        scores['value_accuracy'] = value_score
        
        # Overall accuracy (weighted average)
        overall = (party_score * 0.4 + date_score * 0.3 + value_score * 0.3)
        scores['overall_accuracy'] = overall
        
        return {
            'accuracy': overall,
            'breakdown': scores,
            'passed': overall >= 0.90  # Target 90%+
        }
    
    def _validate_parties(self, ground_truth: List[Dict], extracted: List[Dict]) -> float:
        """Validate party name extraction"""
        if not ground_truth:
            return 1.0 if not extracted else 0.5
        
        if not extracted:
            return 0.0
        
        # Extract names
        truth_names = {p['name'].lower() for p in ground_truth}
        extracted_names = {p['name'].lower() for p in extracted}
        
        # Calculate precision and recall
        if not extracted_names:
            return 0.0
        
        matches = truth_names & extracted_names
        precision = len(matches) / len(extracted_names)
        recall = len(matches) / len(truth_names)
        
        # F1 score
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def _validate_dates(self, 
                       ground_effective: str,
                       ground_termination: str,
                       extracted: Dict) -> float:
        """Validate date extraction"""
        scores = []
        
        # Check effective date
        if ground_effective:
            extracted_effective = extracted.get('effective_date')
            if extracted_effective == ground_effective:
                scores.append(1.0)
            elif extracted_effective and self._dates_close(ground_effective, extracted_effective):
                scores.append(0.8)  # Close but not exact
            else:
                scores.append(0.0)
        
        # Check termination date
        if ground_termination:
            extracted_term = extracted.get('termination_date')
            if extracted_term == ground_termination:
                scores.append(1.0)
            elif extracted_term and self._dates_close(ground_termination, extracted_term):
                scores.append(0.8)
            else:
                scores.append(0.0)
        
        return sum(scores) / len(scores) if scores else 1.0
    
    def _dates_close(self, date1: str, date2: str, days_tolerance: int = 5) -> bool:
        """Check if dates are within tolerance"""
        try:
            d1 = datetime.strptime(date1, '%Y-%m-%d')
            d2 = datetime.strptime(date2, '%Y-%m-%d')
            return abs((d1 - d2).days) <= days_tolerance
        except:
            return False
    
    def _validate_contract_value(self, ground_truth: Optional[Dict], extracted: Optional[Dict]) -> float:
        """Validate contract value extraction"""
        if not ground_truth:
            return 1.0 if not extracted else 0.5
        
        if not extracted:
            return 0.0
        
        truth_amount = ground_truth.get('amount', 0)
        extracted_amount = extracted.get('amount', 0)
        
        if truth_amount == 0:
            return 0.0
        
        # Allow 10% variance
        tolerance = truth_amount * 0.10
        if abs(truth_amount - extracted_amount) <= tolerance:
            return 1.0
        elif abs(truth_amount - extracted_amount) <= tolerance * 2:
            return 0.5
        else:
            return 0.0
    
    # ======== CLASSIFICATION ACCURACY ========
    
    def validate_classification_accuracy(self,
                                       test_clauses: List[Tuple[str, str]],
                                       classification_results: List[Dict]) -> Dict:
        """
        Validate clause classification accuracy
        
        Args:
            test_clauses: [(clause_text, expected_label), ...]
            classification_results: [{'label': '...', 'confidence': 0.85}, ...]
        
        Returns:
            {
                'accuracy': 0.92,
                'precision': 0.95,
                'recall': 0.89,
                'avg_confidence': 0.87,
                'confusion_matrix': {...}
            }
        """
        if len(test_clauses) != len(classification_results):
            logger.error("Clause count mismatch for accuracy validation")
            return {'accuracy': 0.0, 'error': 'Mismatch'}
        
        correct = 0
        confidences = []
        label_stats = {}
        
        for (_, expected_label), result in zip(test_clauses, classification_results):
            predicted_label = result.get('label', '')
            confidence = result.get('confidence', 0)
            
            confidences.append(confidence)
            
            # Track stats per label
            if expected_label not in label_stats:
                label_stats[expected_label] = {'tp': 0, 'fp': 0, 'fn': 0}
            
            if predicted_label == expected_label:
                correct += 1
                label_stats[expected_label]['tp'] += 1
            else:
                label_stats[expected_label]['fn'] += 1
        
        accuracy = correct / len(test_clauses) if test_clauses else 0.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate precision/recall
        precision = self._calculate_precision(label_stats)
        recall = self._calculate_recall(label_stats)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'avg_confidence': avg_confidence,
            'total_tests': len(test_clauses),
            'passed': accuracy >= 0.85  # Target 85%+ accuracy
        }
    
    def _calculate_precision(self, label_stats: Dict) -> float:
        """Calculate precision across all labels"""
        precisions = []
        for stats in label_stats.values():
            total = stats['tp'] + stats['fp']
            if total > 0:
                precisions.append(stats['tp'] / total)
        return sum(precisions) / len(precisions) if precisions else 0.0
    
    def _calculate_recall(self, label_stats: Dict) -> float:
        """Calculate recall across all labels"""
        recalls = []
        for stats in label_stats.values():
            total = stats['tp'] + stats['fn']
            if total > 0:
                recalls.append(stats['tp'] / total)
        return sum(recalls) / len(recalls) if recalls else 0.0
    
    # ======== SEARCH RELEVANCE VALIDATION ========
    
    def validate_search_relevance(self,
                                 query: str,
                                 search_results: List[Dict],
                                 ground_truth_relevant: List[str]) -> Dict:
        """
        Validate search result relevance
        
        Args:
            query: Search query text
            search_results: [{'text': '...', 'similarity_score': 0.85}, ...]
            ground_truth_relevant: [doc_id, ...] of actually relevant results
        
        Returns:
            {
                'ndcg': 0.92,  # Normalized Discounted Cumulative Gain
                'map': 0.88,   # Mean Average Precision
                'mrr': 0.95,   # Mean Reciprocal Rank
                'recall@10': 0.85
            }
        """
        # Extract result IDs from search results
        retrieved_ids = [r.get('document_id') for r in search_results[:10]]
        
        # Calculate metrics
        precision_at_k = self._precision_at_k(retrieved_ids, ground_truth_relevant, k=10)
        recall_at_k = self._recall_at_k(retrieved_ids, ground_truth_relevant, k=10)
        ndcg = self._calculate_ndcg(retrieved_ids, ground_truth_relevant)
        mrr = self._calculate_mrr(retrieved_ids, ground_truth_relevant)
        
        return {
            'precision@10': precision_at_k,
            'recall@10': recall_at_k,
            'ndcg': ndcg,
            'mrr': mrr,
            'avg_relevance_score': self._average_relevance(search_results, ground_truth_relevant),
            'passed': ndcg >= 0.70  # Target NDCG >= 0.7
        }
    
    def _precision_at_k(self, retrieved: List, relevant: List, k: int) -> float:
        """Calculate precision@k"""
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        matches = sum(1 for r in retrieved_k if r in relevant_set)
        return matches / min(k, len(retrieved_k)) if retrieved_k else 0.0
    
    def _recall_at_k(self, retrieved: List, relevant: List, k: int) -> float:
        """Calculate recall@k"""
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        matches = sum(1 for r in retrieved_k if r in relevant_set)
        return matches / len(relevant_set) if relevant_set else 0.0
    
    def _calculate_ndcg(self, retrieved: List, relevant: List) -> float:
        """Calculate NDCG (Normalized Discounted Cumulative Gain)"""
        relevant_set = set(relevant)
        
        # DCG
        dcg = sum(
            (1 if r in relevant_set else 0) / np.log2(i + 2)
            for i, r in enumerate(retrieved[:10])
        )
        
        # IDCG (ideal DCG if all relevant results come first)
        idcg = sum(1 / np.log2(i + 2) for i in range(min(10, len(relevant))))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _calculate_mrr(self, retrieved: List, relevant: List) -> float:
        """Calculate MRR (Mean Reciprocal Rank)"""
        relevant_set = set(relevant)
        
        for i, r in enumerate(retrieved):
            if r in relevant_set:
                return 1 / (i + 1)
        return 0.0
    
    def _average_relevance(self, results: List[Dict], relevant: List) -> float:
        """Calculate average relevance score of results"""
        scores = [r.get('similarity_score', 0) for r in results if r.get('document_id') in relevant]
        return sum(scores) / len(scores) if scores else 0.0


class TestAccuracyValidation(TestCase):
    """Test accuracy validation"""
    
    def setUp(self):
        self.validator = AccuracyValidator()
    
    def test_validate_party_extraction(self):
        """Test party extraction validation"""
        ground_truth = {
            'parties': [
                {'name': 'Acme Corp', 'role': 'Licensor'},
                {'name': 'TechCorp', 'role': 'Licensee'}
            ]
        }
        
        extracted = {
            'parties': [
                {'name': 'Acme Corp', 'role': 'Licensor'},
                {'name': 'TechCorp', 'role': 'Licensee'}
            ]
        }
        
        result = self.validator.validate_metadata_extraction(
            'contract text',
            ground_truth,
            extracted
        )
        
        assert result['accuracy'] == 1.0  # Perfect match
        assert result['passed'] is True
    
    def test_validate_classification_accuracy(self):
        """Test classification accuracy"""
        test_clauses = [
            ('Confidentiality clause text', 'Confidentiality'),
            ('Payment terms clause', 'Payment Terms'),
            ('Termination conditions', 'Termination'),
        ]
        
        results = [
            {'label': 'Confidentiality', 'confidence': 0.92},
            {'label': 'Payment Terms', 'confidence': 0.88},
            {'label': 'Termination', 'confidence': 0.85},
        ]
        
        validation = self.validator.validate_classification_accuracy(test_clauses, results)
        
        assert validation['accuracy'] == 1.0
        assert validation['passed'] is True
    
    def test_validate_search_relevance(self):
        """Test search relevance validation"""
        results = [
            {'document_id': 'doc-1', 'similarity_score': 0.95},
            {'document_id': 'doc-2', 'similarity_score': 0.87},
            {'document_id': 'doc-3', 'similarity_score': 0.45},
        ]
        
        relevant = ['doc-1', 'doc-2']
        
        validation = self.validator.validate_search_relevance(
            'test query',
            results,
            relevant
        )
        
        assert 'ndcg' in validation
        assert validation['ndcg'] >= 0.7
