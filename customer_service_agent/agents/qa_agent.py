"""
QA Agent: Validates response quality and accuracy before sending to customer
"""

import time
from typing import Dict
from agents import BaseAgent, Request, Response


class QAAgent(BaseAgent):
    """
    Validates specialist responses for quality, relevance, and accuracy.
    Can approve responses or request revisions.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, "QAAgent")
        self.quality_threshold = config.get('quality', {}).get('min_response_relevance', 0.75)
    
    def process(self, specialist_response: Response, original_request: Request) -> Response:
        """
        Validate specialist response quality.
        
        Args:
            specialist_response: Response from specialist agent
            original_request: Original customer request
            
        Returns:
            QA validation response
        """
        start_time = time.time()
        
        # Perform quality checks
        relevance_score = self._check_relevance(
            original_request.text,
            specialist_response.content
        )
        hallucination_score = self._check_hallucination(specialist_response.content)
        tone_score = self._check_tone(specialist_response.content)
        
        # Calculate overall quality score
        quality_score = (relevance_score * 0.5 + tone_score * 0.3 + hallucination_score * 0.2)
        
        approved = quality_score >= self.quality_threshold
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=specialist_response.request_id,
            content=f"QA Check: {'APPROVED' if approved else 'NEEDS REVISION'} (Quality Score: {quality_score:.2f})",
            confidence=quality_score,
            requires_escalation=not approved,
            processing_time_ms=processing_time,
            metadata={
                'approved': approved,
                'quality_score': quality_score,
                'relevance_score': relevance_score,
                'hallucination_score': hallucination_score,
                'tone_score': tone_score,
                'specialist': specialist_response.agent_name
            }
        )
        
        self.log_execution(specialist_response.request_id, response.to_dict())
        return response
    
    def _check_relevance(self, request_text: str, response_text: str) -> float:
        """
        Check if response is relevant to the request.
        
        Args:
            request_text: Original customer request
            response_text: Agent response
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Simple implementation: check for key terms overlap
        request_words = set(request_text.lower().split())
        response_words = set(response_text.lower().split())
        
        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'to', 'and', 'or', 'in', 'of', 'for', 'i'}
        request_words -= stopwords
        response_words -= stopwords
        
        if not request_words:
            return 0.7
        
        overlap = len(request_words & response_words) / len(request_words)
        return min(overlap + 0.3, 1.0)  # Baseline boost for general responses
    
    def _check_hallucination(self, response_text: str) -> float:
        """
        Check for hallucinations or made-up information.
        
        Args:
            response_text: Agent response
            
        Returns:
            Score where 1.0 = no hallucination, 0.0 = severe hallucination
        """
        # Simple heuristics for detecting likely hallucinations
        hallucination_signals = [
            'i can access',
            'i can view your',
            'i can modify your',
            'i guarantee',
            'this will definitely',
            'i have confirmed',
            'our system shows'
        ]
        
        text_lower = response_text.lower()
        violations = sum(1 for signal in hallucination_signals if signal in text_lower)
        
        # Score decreases with more violations
        return max(1.0 - (violations * 0.15), 0.6)
    
    def _check_tone(self, response_text: str) -> float:
        """
        Check if tone is professional and helpful.
        
        Args:
            response_text: Agent response
            
        Returns:
            Tone score (0.0 to 1.0)
        """
        # Check for polite language
        positive_signals = [
            'please', 'thank', 'happy', 'help', 'understand',
            'appreciate', 'assist', 'welcome', 'sincerely'
        ]
        
        negative_signals = [
            'cannot help', 'impossible', 'not allowed', 'forbidden',
            'ridiculous', 'stupid', 'idiot'
        ]
        
        text_lower = response_text.lower()
        
        positive_count = sum(1 for signal in positive_signals if signal in text_lower)
        negative_count = sum(1 for signal in negative_signals if signal in text_lower)
        
        # Base tone score
        tone_score = 0.7  # Neutral baseline
        tone_score += positive_count * 0.1
        tone_score -= negative_count * 0.15
        
        return max(min(tone_score, 1.0), 0.5)
