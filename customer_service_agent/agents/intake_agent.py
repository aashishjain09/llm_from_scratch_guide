"""
Intake Agent: Receives requests, extracts intent and priority
"""

import time
import re
from typing import Dict, Tuple
from agents import BaseAgent, Request, Response, Intent, Priority


class IntakeAgent(BaseAgent):
    """
    Analyzes incoming customer requests, classifies intent, determines priority.
    Extracts urgency signals and structures the request for routing.
    """
    
    # Intent classification keywords
    INTENT_KEYWORDS = {
        Intent.BILLING: [
            "billing", "invoice", "payment", "charge", "subscription", "cancel",
            "refund", "credit", "balance", "account", "cost", "price", "fee"
        ],
        Intent.TECHNICAL: [
            "error", "bug", "crash", "broken", "not working", "issue", "problem",
            "slow", "performance", "api", "integration", "fail", "doesn't work",
            "exception", "timeout", "connection"
        ],
        Intent.SALES: [
            "upgrade", "downgrade", "product", "feature", "plan", "pricing",
            "recommendation", "which plan", "what features", "how much",
            "licensing", "trial", "demo", "enterprise"
        ]
    }
    
    # Urgency signal keywords that elevate priority
    URGENCY_SIGNALS = {
        "critical": ["critical", "urgent", "emergency", "down", "outage", "cannot work"],
        "time_sensitive": ["asap", "deadline", "today", "now", "immediately"],
        "business_impact": ["business", "production", "customers", "revenue", "stuck"]
    }
    
    def __init__(self, config: Dict):
        super().__init__(config, "IntakeAgent")
    
    def process(self, request: Request) -> Response:
        """
        Process incoming request: classify intent, determine priority, extract signals.
        
        Args:
            request: Raw customer request
            
        Returns:
            Response with structured request
        """
        start_time = time.time()
        
        # Extract intent from text
        intent = self._classify_intent(request.text)
        request.intent = intent
        
        # Extract urgency signals
        urgency_signals = self._extract_urgency_signals(request.text)
        request.urgency_signals = urgency_signals
        
        # Determine priority
        priority = self._determine_priority(urgency_signals)
        request.priority = priority
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=f"Request classified: intent={intent.value}, priority={priority.name}",
            confidence=0.95,
            processing_time_ms=processing_time,
            metadata={
                'intent': intent.value,
                'priority': priority.name,
                'urgency_signals': urgency_signals,
                'request_length': len(request.text)
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response
    
    def _classify_intent(self, text: str) -> Intent:
        """
        Classify request intent based on keywords.
        
        Args:
            text: Request text
            
        Returns:
            Detected Intent
        """
        text_lower = text.lower()
        intent_scores = {intent: 0 for intent in Intent}
        
        # Count keyword matches for each intent
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent_scores[intent] += 1
        
        # Return intent with highest score, default to OTHER
        max_intent = max(intent_scores, key=intent_scores.get)
        return max_intent if intent_scores[max_intent] > 0 else Intent.OTHER
    
    def _extract_urgency_signals(self, text: str) -> list:
        """
        Extract urgency signals from request text.
        
        Args:
            text: Request text
            
        Returns:
            List of detected urgency signals
        """
        signals = []
        text_lower = text.lower()
        
        for signal_type, keywords in self.URGENCY_SIGNALS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    signals.append(signal_type)
                    break  # Only count each signal type once
        
        return signals
    
    def _determine_priority(self, urgency_signals: list) -> Priority:
        """
        Determine priority level based on urgency signals.
        
        Args:
            urgency_signals: List of detected urgency signals
            
        Returns:
            Priority level
        """
        if "critical" in urgency_signals:
            return Priority.HIGH
        elif "business_impact" in urgency_signals:
            return Priority.HIGH
        elif "time_sensitive" in urgency_signals:
            return Priority.MEDIUM
        else:
            return Priority.LOW
