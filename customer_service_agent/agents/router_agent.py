"""
Router Agent: Routes requests to appropriate specialist agent
"""

import time
from typing import Dict, List
from agents import BaseAgent, Request, Response, Intent


class RouterAgent(BaseAgent):
    """
    Routes classified requests to appropriate specialist agent.
    Considers intent, priority, and current specialist load.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, "RouterAgent")
        self.specialist_load = {
            'billing': 0,
            'technical': 0,
            'sales': 0
        }
    
    def process(self, request: Request) -> Response:
        """
        Route request to appropriate specialist.
        
        Args:
            request: Classified customer request
            
        Returns:
            Response indicating routing decision
        """
        start_time = time.time()
        
        # Determine target specialist based on intent
        target_specialist = self._determine_specialist(request.intent)
        
        # Update specialist load
        self.specialist_load[target_specialist] += 1
        
        processing_time = (time.time() - start_time) * 1000
        
        response = Response(
            agent_name=self.agent_name,
            request_id=request.request_id,
            content=f"Routed to {target_specialist} specialist",
            confidence=0.98,
            processing_time_ms=processing_time,
            metadata={
                'target_specialist': target_specialist,
                'specialist_load': self.specialist_load.copy()
            }
        )
        
        self.log_execution(request.request_id, response.to_dict())
        return response
    
    def _determine_specialist(self, intent: Intent) -> str:
        """
        Map intent to specialist type.
        
        Args:
            intent: Request intent
            
        Returns:
            Specialist type (billing, technical, sales)
        """
        intent_to_specialist = {
            Intent.BILLING: 'billing',
            Intent.TECHNICAL: 'technical',
            Intent.SALES: 'sales',
            Intent.OTHER: 'technical'  # Default to technical for other
        }
        return intent_to_specialist.get(intent, 'technical')
