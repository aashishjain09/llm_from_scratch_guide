"""
Customer Service Multi-Agent System
Base agent classes and utilities
"""

import json
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import yaml


class Priority(Enum):
    """Request priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Intent(Enum):
    """Customer request intent types"""
    BILLING = "billing"
    TECHNICAL = "technical"
    SALES = "sales"
    OTHER = "other"


@dataclass
class Request:
    """Customer service request"""
    request_id: str
    text: str
    intent: Intent = Intent.OTHER
    priority: Priority = Priority.MEDIUM
    urgency_signals: List[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.urgency_signals is None:
            self.urgency_signals = []
    
    def to_dict(self):
        data = asdict(self)
        data['intent'] = self.intent.value
        data['priority'] = self.priority.name
        return data


@dataclass
class Response:
    """Agent response"""
    agent_name: str
    request_id: str
    content: str
    confidence: float
    requires_escalation: bool = False
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        return asdict(self)


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, config: Dict[str, Any], agent_name: str):
        """
        Initialize agent
        
        Args:
            config: Configuration dict from service_config.yaml
            agent_name: Name of the agent
        """
        self.config = config
        self.agent_name = agent_name
        self.execution_history = []
    
    def process(self, request: Request) -> Response:
        """
        Process a request. Subclasses should override this.
        
        Args:
            request: Customer request
            
        Returns:
            Response from the agent
        """
        raise NotImplementedError
    
    def log_execution(self, request_id: str, result: Dict[str, Any]):
        """Log agent execution for debugging"""
        self.execution_history.append({
            'timestamp': time.time(),
            'request_id': request_id,
            'result': result
        })
    
    def load_config(self, config_path: str = 'config/service_config.yaml') -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)


def load_knowledge_base(filepath: str) -> Dict[str, Any]:
    """Load knowledge base from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_execution_log(log_data: List[Dict], filepath: str):
    """Save execution logs to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(log_data, f, indent=2)
