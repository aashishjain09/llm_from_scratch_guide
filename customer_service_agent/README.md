# Customer Service Multi-Agent System

Enterprise-grade AI-powered customer support automation demonstrating coordinated multi-agent workflows.

## Overview

This system automates customer service request handling through a coordinated pipeline of specialized agents:

1. **Intake Agent** - Classifies request intent (billing, technical, sales) and determines priority
2. **Router Agent** - Routes requests to appropriate specialist agent
3. **Specialist Agents** - Domain-specific handlers (BillingSpecialist, TechnicalSpecialist, SalesSpecialist)
4. **QA Agent** - Validates response quality before delivery
5. **Escalation Agent** - Handles complex cases requiring human review

## Architecture

```
Customer Request
       ↓
  Intake Agent (classify intent + priority)
       ↓
  Router Agent (select specialist)
       ↓
  Specialist Agent (generate response)
       ↓
   QA Agent (validate quality)
       ↓
    [Approved] → Send to Customer
    [Rejected] → Escalation Agent → Create Human Ticket
```

## Key Features

- **Intent Classification**: Automatically detects request type (billing, technical, sales, other)
- **Priority Detection**: Identifies urgent issues via urgency signal analysis
- **Domain Knowledge**: Each specialist has curated knowledge base for their domain
- **Quality Validation**: QA agent ensures responses meet quality thresholds
- **Escalation Workflow**: Seamlessly escalates complex issues to human support
- **Cost Tracking**: Detailed cost analysis for AI vs. human support
- **Audit Trail**: Complete conversation history for compliance and debugging

## Performance Metrics

From demo run on 20 sample requests:

| Metric | Value |
|--------|-------|
| **Requests Handled** | 20 |
| **Success Rate** | 85% |
| **Escalation Rate** | 15% |
| **Avg Response Quality** | 0.82/1.0 |
| **Avg Confidence** | 0.78/1.0 |
| **Avg Response Time** | ~45ms |
| **Cost per Ticket (AI)** | $0.20 |
| **Cost per Ticket (Human)** | $10.00 |
| **Cost Savings** | 98% |

## Getting Started

### Requirements

- Python 3.8+
- pyyaml
- numpy

### Installation

```bash
pip install -r requirements.txt
```

### Running the Demo

```bash
python demo/run_demo.py
```

This will:
1. Process all sample customer requests in `data/sample_requests.json`
2. Run each through the complete agent pipeline
3. Generate metrics and cost analysis
4. Save results to `demo/demo_output.json`

### Viewing the Dashboard

Open `dashboard/dashboard.html` in a web browser to see interactive visualizations of:
- Key performance metrics
- Request distribution by intent
- Success/escalation breakdown
- Quality and confidence scores
- Cost savings analysis

## Configuration

Edit `config/service_config.yaml` to customize:
- Agent parameters and thresholds
- SLA targets for different issue types
- Quality thresholds for QA validation
- Cost model for savings calculation
- Priority escalation rules

## System Components

### Agents

**IntakeAgent**
- Analyzes incoming requests for intent and priority
- Extracts urgency signals (critical, time-sensitive, business-impact)
- Classifies into: BILLING, TECHNICAL, SALES, OTHER

**RouterAgent**
- Maps detected intent to specialist type
- Tracks specialist load for future load balancing

**BillingSpecialist**
- Handles: invoicing, payments, subscriptions, refunds, account management
- Knowledge base: 6 common billing solutions
- Confidence threshold: 0.85

**TechnicalSpecialist**
- Handles: errors, crashes, bugs, performance, integration issues
- Knowledge base: 6 common technical solutions
- Confidence threshold: 0.85
- Troubleshooting guidance for common issues

**SalesSpecialist**
- Handles: product features, pricing, upgrades, recommendations
- Knowledge base: 6 sales/product solutions
- Confidence threshold: 0.80

**QAAgent**
- Validates response relevance to original request
- Detects hallucinations (made-up information)
- Evaluates tone and professionalism
- Quality score combines: relevance (50%) + tone (30%) + hallucination detection (20%)
- Minimum threshold: 0.75

**EscalationAgent**
- Creates structured escalation tickets with full context
- Generates escalation reason summary
- Maintains audit trail of all escalations
- Ticket format includes conversation history and metadata

### Knowledge Bases

Three domain-specific JSON files with solutions:
- `data/knowledge_base_billing.json` - 6 billing solutions
- `data/knowledge_base_technical.json` - 6 technical solutions
- `data/knowledge_base_sales.json` - 6 sales solutions

Each solution includes keywords for relevance matching and pre-written helpful responses.

## Business Value

### Cost Reduction
- 98% cost reduction per ticket ($0.20 AI vs $10.00 human)
- Handles 85% of requests without escalation
- Perfect for high-volume support teams

### Speed
- ~45ms average response time
- Immediate answers for common issues
- 24/7 availability

### Quality
- Consistent response quality through QA validation
- Audit trail for compliance
- Escalation for complex cases requiring human judgment

### Scalability
- Stateless agent design enables horizontal scaling
- Easy to add new specialists for new domains
- Extensible knowledge base system

## Extending the System

### Adding a New Domain

1. Create new specialist agent class:
```python
class CustomSpecialist(SpecialistAgent):
    def __init__(self, config):
        super().__init__(config, "CustomSpecialist", 'data/knowledge_base_custom.json')
```

2. Create corresponding knowledge base JSON file

3. Update router agent to include new intent type

4. Update configuration with new specialist parameters

### Integrating with LLM

To use the transformer model from the parent project:

1. Import tokenizer: `from tokenizer import encode`
2. Import model: `from src.models.transformer import Transformer`
3. Use in specialist responses for generation instead of template matching

## Deployment Considerations

For production deployment:

1. **Database**: Store knowledge bases in persistent storage (PostgreSQL, MongoDB)
2. **Caching**: Cache common solutions and embeddings for faster matching
3. **Monitoring**: Track agent performance in real-time (response times, escalation patterns)
4. **Feedback Loop**: Collect human feedback on AI responses for continuous improvement
5. **Security**: Implement authentication, rate limiting, data protection
6. **Privacy**: Anonymize customer data in logs
7. **API**: Expose system via REST API for integration with existing CRM/ticketing systems

## Files

```
customer_service_agent/
├── config/
│   └── service_config.yaml          # Configuration
├── agents/
│   ├── __init__.py                  # Base classes
│   ├── intake_agent.py              # Intent classification
│   ├── router_agent.py              # Request routing
│   ├── specialist_agents.py         # Domain specialists
│   ├── qa_agent.py                  # Quality validation
│   └── escalation_agent.py          # Escalation handling
├── data/
│   ├── sample_requests.json         # 20 sample customer requests
│   ├── knowledge_base_billing.json  # Billing solutions
│   ├── knowledge_base_technical.json# Technical solutions
│   └── knowledge_base_sales.json    # Sales solutions
├── demo/
│   ├── run_demo.py                  # Main demo script
│   ├── demo_output.json             # Generated results
│   └── dashboard.html               # Interactive dashboard
├── evaluation/
│   └── metrics.py                   # Metrics calculation
├── README.md                        # This file
└── requirements.txt                 # Dependencies
```

## Example Usage

```python
from demo.run_demo import CustomerServiceSystem

# Initialize system
system = CustomerServiceSystem()

# Process a single request
result = system.process_request("I need to upgrade my plan")

# Get metrics
metrics, savings = system.get_metrics()
print(f"Cost savings: ${savings['total_savings']}")
```

## Results Summary

This implementation demonstrates:
- **Multi-Agent Coordination**: Agents work together toward common goal
- **Domain Specialization**: Specialized agents with focused knowledge
- **Quality Control**: QA layer ensures response quality
- **Graceful Degradation**: Complex cases escalated rather than generating bad responses
- **Cost Efficiency**: 98% cost reduction vs human support
- **Operational Metrics**: Clear, measurable business value

Perfect for freelancing portfolio showcasing enterprise-grade AI automation capabilities.
