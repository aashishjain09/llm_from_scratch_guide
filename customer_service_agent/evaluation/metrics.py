"""
Evaluation metrics for customer service system
"""

import json
from typing import Dict, List
from dataclasses import dataclass
import statistics


@dataclass
class Metrics:
    """Container for evaluation metrics"""
    total_requests: int
    successful_responses: int
    escalated_requests: int
    avg_response_time_ms: float
    cost_per_ticket: float
    quality_score: float
    escalation_rate: float
    avg_confidence: float
    
    def to_dict(self):
        return {
            'total_requests': self.total_requests,
            'successful_responses': self.successful_responses,
            'escalated_requests': self.escalated_requests,
            'avg_response_time_ms': round(self.avg_response_time_ms, 2),
            'cost_per_ticket': round(self.cost_per_ticket, 2),
            'quality_score': round(self.quality_score, 3),
            'escalation_rate': round(self.escalation_rate, 3),
            'avg_confidence': round(self.avg_confidence, 3)
        }


class MetricsCalculator:
    """Calculates performance metrics from execution logs"""
    
    def __init__(self, cost_config: Dict = None):
        """
        Initialize metrics calculator.
        
        Args:
            cost_config: Cost configuration with pricing model
        """
        self.cost_config = cost_config or {
            'specialist_response_cost': 0.15,
            'qa_validation_cost': 0.05,
            'escalation_cost': 2.50,
            'human_support_cost_per_ticket': 10.0
        }
    
    def calculate(self, execution_logs: List[Dict]) -> Metrics:
        """
        Calculate metrics from execution logs.
        
        Args:
            execution_logs: List of execution records from system
            
        Returns:
            Metrics object with aggregated statistics
        """
        if not execution_logs:
            return self._empty_metrics()
        
        # Organize logs by request
        requests_data = self._organize_by_request(execution_logs)
        
        total_requests = len(requests_data)
        successful_responses = 0
        escalated_requests = 0
        response_times = []
        costs = []
        quality_scores = []
        confidences = []
        
        for request_id, request_logs in requests_data.items():
            # Check if request was escalated
            escalated = any(log.get('result', {}).get('requires_escalation', False) 
                          for log in request_logs)
            
            if escalated:
                escalated_requests += 1
            else:
                successful_responses += 1
            
            # Collect timing data
            times = [log.get('result', {}).get('processing_time_ms', 0) 
                    for log in request_logs]
            response_times.extend(times)
            
            # Collect quality data
            quality = [log.get('result', {}).get('confidence', 0.5) 
                      for log in request_logs if 'confidence' in log.get('result', {})]
            quality_scores.extend(quality)
            
            # Collect confidence data
            confidences.extend([log.get('result', {}).get('confidence', 0.5) 
                              for log in request_logs if 'confidence' in log.get('result', {})])
            
            # Calculate cost for this request
            cost = self._calculate_request_cost(request_logs, escalated)
            costs.append(cost)
        
        # Aggregate metrics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        avg_cost = statistics.mean(costs) if costs else 0
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0.5
        avg_confidence = statistics.mean(confidences) if confidences else 0.5
        escalation_rate = escalated_requests / total_requests if total_requests > 0 else 0
        
        return Metrics(
            total_requests=total_requests,
            successful_responses=successful_responses,
            escalated_requests=escalated_requests,
            avg_response_time_ms=avg_response_time,
            cost_per_ticket=avg_cost,
            quality_score=avg_quality,
            escalation_rate=escalation_rate,
            avg_confidence=avg_confidence
        )
    
    def _organize_by_request(self, logs: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize execution logs by request ID"""
        organized = {}
        for log in logs:
            request_id = log.get('request_id', 'unknown')
            if request_id not in organized:
                organized[request_id] = []
            organized[request_id].append(log)
        return organized
    
    def _calculate_request_cost(self, request_logs: List[Dict], escalated: bool) -> float:
        """Calculate cost for processing a single request"""
        cost = 0.0
        
        for log in request_logs:
            agent_name = log.get('result', {}).get('agent_name', '')
            
            if agent_name == 'IntakeAgent':
                pass  # Intake is free
            elif agent_name == 'RouterAgent':
                pass  # Router is free
            elif 'Specialist' in agent_name:
                cost += self.cost_config['specialist_response_cost']
            elif agent_name == 'QAAgent':
                cost += self.cost_config['qa_validation_cost']
            elif agent_name == 'EscalationAgent':
                cost += self.cost_config['escalation_cost']
        
        return cost
    
    def _empty_metrics(self) -> Metrics:
        """Return empty metrics"""
        return Metrics(
            total_requests=0,
            successful_responses=0,
            escalated_requests=0,
            avg_response_time_ms=0,
            cost_per_ticket=0,
            quality_score=0,
            escalation_rate=0,
            avg_confidence=0
        )
    
    def calculate_cost_savings(self, metrics: Metrics, human_support_cost: float = None) -> Dict:
        """
        Calculate cost savings vs. human support baseline.
        
        Args:
            metrics: Calculated metrics
            human_support_cost: Cost per ticket for human support (default from config)
            
        Returns:
            Dictionary with savings breakdown
        """
        human_cost = human_support_cost or self.cost_config['human_support_cost_per_ticket']
        
        total_requests = metrics.total_requests
        ai_cost_total = metrics.cost_per_ticket * total_requests
        human_cost_total = human_cost * total_requests
        
        savings = human_cost_total - ai_cost_total
        savings_percentage = (savings / human_cost_total * 100) if human_cost_total > 0 else 0
        
        return {
            'total_requests': total_requests,
            'ai_cost_per_ticket': round(metrics.cost_per_ticket, 2),
            'human_cost_per_ticket': round(human_cost, 2),
            'ai_cost_total': round(ai_cost_total, 2),
            'human_cost_total': round(human_cost_total, 2),
            'total_savings': round(savings, 2),
            'savings_percentage': round(savings_percentage, 1)
        }
