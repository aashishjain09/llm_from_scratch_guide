"""
Specialist Agents: Domain-specific agents for handling customer requests
"""

import time
import json
import random
from typing import Dict, List, Tuple
from agents import BaseAgent, Request, Response, load_knowledge_base


class SpecialistAgent(BaseAgent):
    """Base class for specialist agents"""
    
    def __init__(self, config: Dict, agent_name: str, knowledge_base_path: str):
        super().__init__(config, agent_name)
        self.knowledge_base = load_knowledge_base(knowledge_base_path)
        self.solutions = self.knowledge_base.get('solutions', {})
    
    def _find_relevant_solution(self, request_text: str) -> Tuple[str, float]:
        """
        Find relevant solution from knowledge base.
        
        Args:
            request_text: Customer request text
            
        Returns:
            Tuple of (solution, confidence_score)
        """
        text_lower = request_text.lower()
        best_match = None
        best_score = 0.0
        
        for solution_id, solution in self.solutions.items():
            keywords = solution.get('keywords', [])
            score = 0.0
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = solution
        
        # Normalize confidence: more keyword matches = higher confidence
        confidence = min(best_score / len(best_match.get('keywords', [])) if best_match else 0, 1.0)
        confidence = max(confidence, 0.5)  # Minimum confidence of 0.5
        
        return best_match, confidence
    
    def process(self, request: Request) -> Response:
        """
        Process request with specialist knowledge.
        Should be overridden by subclasses.
        """
        raise NotImplementedError


class BillingSpecialist(SpecialistAgent):
    """Handles billing, invoicing, subscription, and payment issues"""
    
    def __init__(self, config: Dict):
        super().__init__(
            config,
            "BillingSpecialist",
            'data/knowledge_base_billing.json'
        )
    
    def process(self, request: Request) -> Response:
        """
        Process billing-related request.
        
        Args:
            request: Customer request
            
        Returns:
            Response with billing solution
        """
        start_time = time.time()
        
        solution, confidence = self._find_relevant_solution(request.text)
        
        if solution:
            response_text = solution.get('answer', 'Unable to resolve billing issue.')
        else:
            response_text = "I understand you have a billing inquiry. For complex issues, I recommend contacting our billing support team directly."
            confidence = 0.6
        
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=response_text,
            confidence=confidence,
            requires_escalation=confidence < 0.65,
            processing_time_ms=processing_time,
            metadata={
                'specialist_type': 'billing',
                'solution_found': solution is not None,
                'confidence': confidence
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response


class TechnicalSpecialist(SpecialistAgent):
    """Handles technical issues, bugs, errors, and troubleshooting"""
    
    def __init__(self, config: Dict):
        super().__init__(
            config,
            "TechnicalSpecialist",
            'data/knowledge_base_technical.json'
        )
    
    def process(self, request: Request) -> Response:
        """
        Process technical support request.
        
        Args:
            request: Customer request
            
        Returns:
            Response with troubleshooting steps
        """
        start_time = time.time()
        
        solution, confidence = self._find_relevant_solution(request.text)
        
        if solution:
            response_text = solution.get('answer', 'Unable to resolve technical issue.')
        else:
            response_text = "I understand you're experiencing a technical issue. Please provide error messages or specific symptoms, and I'll help troubleshoot."
            confidence = 0.65
        
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=response_text,
            confidence=confidence,
            requires_escalation=confidence < 0.70,
            processing_time_ms=processing_time,
            metadata={
                'specialist_type': 'technical',
                'solution_found': solution is not None,
                'confidence': confidence
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response


class SalesSpecialist(SpecialistAgent):
    """Handles product questions, features, pricing, and recommendations"""
    
    def __init__(self, config: Dict):
        super().__init__(
            config,
            "SalesSpecialist",
            'data/knowledge_base_sales.json'
        )
    
    def process(self, request: Request) -> Response:
        """
        Process sales/product inquiry.
        
        Args:
            request: Customer request
            
        Returns:
            Response with product information
        """
        start_time = time.time()
        
        solution, confidence = self._find_relevant_solution(request.text)
        
        if solution:
            response_text = solution.get('answer', 'Unable to provide product information.')
        else:
            response_text = "I'd be happy to help with your product inquiry! Our sales team can provide personalized recommendations."
            confidence = 0.72
        
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=response_text,
            confidence=confidence,
            requires_escalation=confidence < 0.65,
            processing_time_ms=processing_time,
            metadata={
                'specialist_type': 'sales',
                'solution_found': solution is not None,
                'confidence': confidence
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response
