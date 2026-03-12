"""
Demo runner: Execute the multi-agent system on sample customer requests
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path to import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Request, Priority
from agents.intake_agent import IntakeAgent
from agents.router_agent import RouterAgent
from agents.specialist_agents import BillingSpecialist, TechnicalSpecialist, SalesSpecialist
from agents.qa_agent import QAAgent
from agents.escalation_agent import EscalationAgent
from evaluation.metrics import MetricsCalculator


class CustomerServiceSystem:
    """Complete customer service multi-agent system"""
    
    def __init__(self, config_path: str = 'config/service_config.yaml'):
        """Initialize all agents"""
        import yaml
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.intake_agent = IntakeAgent(self.config)
        self.router_agent = RouterAgent(self.config)
        self.billing_specialist = BillingSpecialist(self.config)
        self.technical_specialist = TechnicalSpecialist(self.config)
        self.sales_specialist = SalesSpecialist(self.config)
        self.qa_agent = QAAgent(self.config)
        self.escalation_agent = EscalationAgent(self.config)
        
        self.all_execution_logs = []
    
    def process_request(self, request_text: str, request_id: str = None) -> dict:
        """
        Process a customer request through the multi-agent pipeline.
        
        Args:
            request_text: Customer request text
            request_id: Unique request identifier
            
        Returns:
            Complete response with all agent interactions
        """
        if not request_id:
            request_id = f"req_{int(time.time() * 1000)}"
        
        # Create request object
        request = Request(request_id=request_id, text=request_text)
        
        pipeline_responses = []
        
        # Step 1: Intake - classify intent and priority
        print(f"\n[{request_id}] Processing: {request_text[:60]}...")
        intake_response = self.intake_agent.process(request)
        pipeline_responses.append(intake_response)
        print(f"  ✓ Intake: Intent={request.intent.value}, Priority={request.priority.name}")
        self.all_execution_logs.append({
            'request_id': request_id,
            'result': intake_response.to_dict()
        })
        
        # Step 2: Router - determine specialist
        router_response = self.router_agent.process(request)
        pipeline_responses.append(router_response)
        target_specialist = router_response.metadata['target_specialist']
        print(f"  ✓ Router: Routed to {target_specialist} specialist")
        self.all_execution_logs.append({
            'request_id': request_id,
            'result': router_response.to_dict()
        })
        
        # Step 3: Specialist - generate response
        if target_specialist == 'billing':
            specialist_response = self.billing_specialist.process(request)
        elif target_specialist == 'technical':
            specialist_response = self.technical_specialist.process(request)
        else:  # sales
            specialist_response = self.sales_specialist.process(request)
        
        pipeline_responses.append(specialist_response)
        print(f"  ✓ {specialist_response.agent_name}: confidence={specialist_response.confidence:.2f}")
        self.all_execution_logs.append({
            'request_id': request_id,
            'result': specialist_response.to_dict()
        })
        
        # Step 4: QA - validate response
        qa_response = self.qa_agent.process(specialist_response, request)
        pipeline_responses.append(qa_response)
        approved = qa_response.metadata['approved']
        print(f"  ✓ QA: {'APPROVED' if approved else 'NEEDS ESCALATION'} (score={qa_response.confidence:.2f})")
        self.all_execution_logs.append({
            'request_id': request_id,
            'result': qa_response.to_dict()
        })
        
        # Step 5: Escalation (if needed)
        if not approved:
            escalation_response = self.escalation_agent.process(request, pipeline_responses)
            pipeline_responses.append(escalation_response)
            print(f"  ✓ Escalation: Ticket {escalation_response.metadata['ticket_id']} created")
            self.all_execution_logs.append({
                'request_id': request_id,
                'result': escalation_response.to_dict()
            })
            final_response = escalation_response.content
        else:
            final_response = specialist_response.content
        
        return {
            'request_id': request_id,
            'input': request_text,
            'final_response': final_response,
            'escalated': not approved,
            'avg_processing_time_ms': sum(r.processing_time_ms for r in pipeline_responses),
            'confidence': specialist_response.confidence,
            'pipeline': [r.to_dict() for r in pipeline_responses]
        }
    
    def process_batch(self, sample_file: str) -> list:
        """
        Process a batch of sample requests.
        
        Args:
            sample_file: Path to JSON file with sample requests
            
        Returns:
            List of results for all requests
        """
        with open(sample_file, 'r') as f:
            samples = json.load(f)
        
        results = []
        for sample in samples:
            result = self.process_request(sample['text'], sample['id'])
            results.append(result)
        
        return results
    
    def get_metrics(self):
        """Calculate system metrics"""
        calculator = MetricsCalculator(
            self.config.get('cost_model', {})
        )
        metrics = calculator.calculate(self.all_execution_logs)
        savings = calculator.calculate_cost_savings(metrics)
        return metrics, savings


def print_demo_results(results: list, metrics, savings):
    """Pretty print demo results"""
    print("\n" + "="*80)
    print("CUSTOMER SERVICE MULTI-AGENT SYSTEM - DEMO RESULTS")
    print("="*80)
    
    print(f"\nProcessed {metrics.total_requests} customer requests")
    print(f"  ✓ Successful: {metrics.successful_responses} ({100*metrics.successful_responses/metrics.total_requests:.1f}%)")
    print(f"  ✓ Escalated: {metrics.escalated_requests} ({100*metrics.escalation_rate:.1f}%)")
    
    print(f"\nPerformance Metrics:")
    print(f"  • Avg Response Time: {metrics.avg_response_time_ms:.1f}ms")
    print(f"  • Avg Quality Score: {metrics.quality_score:.2f}/1.00")
    print(f"  • Avg Confidence: {metrics.avg_confidence:.2f}/1.00")
    
    print(f"\nCost Analysis:")
    print(f"  • AI Cost per Ticket: ${savings['ai_cost_per_ticket']}")
    print(f"  • Human Support Cost: ${savings['human_cost_per_ticket']}")
    print(f"  • Total Savings: ${savings['total_savings']} ({savings['savings_percentage']:.1f}%)")
    
    print(f"\nSample Responses (first 5):")
    for i, result in enumerate(results[:5], 1):
        escalated_marker = "⚠️  ESCALATED" if result['escalated'] else "✓"
        print(f"\n  {i}. {escalated_marker}")
        print(f"     Q: {result['input'][:60]}...")
        print(f"     A: {result['final_response'][:70]}...")


if __name__ == '__main__':
    print("Initializing Customer Service Multi-Agent System...")
    system = CustomerServiceSystem()
    
    print("Processing sample requests...\n")
    results = system.process_batch('data/sample_requests.json')
    
    metrics, savings = system.get_metrics()
    print_demo_results(results, metrics, savings)
    
    # Save results to JSON
    output = {
        'results': results,
        'metrics': metrics.to_dict(),
        'savings': savings
    }
    
    with open('demo/demo_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Demo results saved to demo/demo_output.json")
    print("="*80)
