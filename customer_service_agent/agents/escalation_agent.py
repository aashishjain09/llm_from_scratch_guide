"""
Escalation Agent: Handles escalation of complex issues to human support
"""

import time
import json
from typing import Dict
from agents import BaseAgent, Request, Response


class EscalationAgent(BaseAgent):
    """
    Handles escalation of unresolved issues to human support team.
    Formats conversation context and creates escalation ticket.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, "EscalationAgent")
        self.escalation_tickets = []
    
    def process(self, request: Request, agent_responses: list) -> Response:
        """
        Create escalation ticket with full conversation context.
        
        Args:
            request: Original customer request
            agent_responses: List of responses from processing pipeline
            
        Returns:
            Escalation ticket response
        """
        start_time = time.time()
        
        # Create escalation ticket
        ticket_id = self._generate_ticket_id()
        ticket = {
            'ticket_id': ticket_id,
            'request_id': request.request_id,
            'priority': request.priority.name,
            'customer_request': request.text,
            'intent': request.intent.value,
            'urgency_signals': request.urgency_signals,
            'conversation_history': [resp.to_dict() for resp in agent_responses],
            'escalation_reason': self._generate_escalation_reason(agent_responses),
            'timestamp': time.time(),
            'status': 'pending_human_review'
        }
        
        self.escalation_tickets.append(ticket)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=f"Escalation ticket created: {ticket_id}. A support specialist will review your case shortly.",
            confidence=1.0,
            processing_time_ms=processing_time,
            metadata={
                'ticket_id': ticket_id,
                'escalation_type': 'complex_issue',
                'agent_count': len(agent_responses)
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response
    
    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID"""
        import uuid
        return f"TICKET-{uuid.uuid4().hex[:8].upper()}"
    
    def _generate_escalation_reason(self, agent_responses: list) -> str:
        """
        Generate explanation for why this case is being escalated.
        
        Args:
            agent_responses: List of previous agent responses
            
        Returns:
            Escalation reason string
        """
        reasons = []
        
        for resp in agent_responses:
            if resp.requires_escalation:
                reasons.append(f"Low confidence from {resp.agent_name}")
            if resp.confidence < 0.65:
                reasons.append(f"Specialist confidence below threshold")
        
        if not reasons:
            reasons.append("Manual escalation requested")
        
        return "; ".join(reasons)
    
    def get_escalation_queue(self) -> list:
        """Get all pending escalation tickets"""
        return [t for t in self.escalation_tickets if t['status'] == 'pending_human_review']
    
    def save_escalation_log(self, filepath: str):
        """Save escalation tickets to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.escalation_tickets, f, indent=2, default=str)
