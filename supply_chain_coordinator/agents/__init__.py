"""
Base classes for supply chain agents
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from enum import Enum
import yaml


@dataclass
class Decision:
    """Agent decision with context"""
    agent_name: str
    day: int
    decision_type: str  # 'procurement', 'shipment', 'inventory_adjustment', etc.
    details: Dict[str, Any]
    cost: float = 0.0
    impact: str = ""
    
    def to_dict(self):
        return asdict(self)


class SupplyChainAgent:
    """Base class for supply chain agents"""
    
    def __init__(self, agent_name: str, config: Dict):
        self.agent_name = agent_name
        self.config = config
        self.decisions = []
    
    def make_decision(self, state: Dict) -> Decision:
        """
        Make a decision based on current supply chain state.
        Override in subclasses.
        """
        raise NotImplementedError
    
    def log_decision(self, decision: Decision):
        """Record a decision"""
        self.decisions.append(decision)
    
    def get_decisions(self) -> List[Decision]:
        """Get all decisions made by this agent"""
        return self.decisions


def load_supply_chain_config(config_path: str = 'config/supply_chain_config.yaml') -> Dict:
    """Load supply chain configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def calculate_distance(loc1: List[float], loc2: List[float]) -> float:
    """Calculate great circle distance between two coordinates (simplified)"""
    import math
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    
    # Simplified distance calculation (latitude difference)
    # Real implementation would use Haversine formula
    dx = (lon2 - lon1) * 111  # ~111 km per degree longitude at equator
    dy = (lat2 - lat1) * 111  # ~111 km per degree latitude
    
    return math.sqrt(dx**2 + dy**2)
