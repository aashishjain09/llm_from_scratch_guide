"""
Supply Chain Agents: Demand, Inventory, Logistics, Supplier, Exception Handler, Orchestrator
"""

from agents import SupplyChainAgent, Decision, calculate_distance
from typing import Dict, List, Tuple
import statistics


class DemandAgent(SupplyChainAgent):
    """Analyzes demand forecasts and recommends safety stock levels"""
    
    def __init__(self, config: Dict):
        super().__init__("DemandAgent", config)
    
    def analyze_demand(self, current_inventory: Dict[str, int], 
                      demand_forecast: Dict[str, float]) -> Dict[str, int]:
        """
        Analyze demand and recommend inventory levels.
        
        Args:
            current_inventory: Current stock levels by SKU
            demand_forecast: Forecasted demand by SKU
            
        Returns:
            Recommended inventory targets for each SKU
        """
        safety_stock_multiplier = self.config['agents']['demand']['reorder_point_multiplier']
        
        recommendations = {}
        for sku, demand in demand_forecast.items():
            # Target = demand * days_of_supply * safety_multiplier
            target_stock = int(demand * 30 * safety_stock_multiplier)  # 30-day buffer
            recommendations[sku] = max(target_stock, 100)  # Minimum 100 units
        
        return recommendations


class InventoryAgent(SupplyChainAgent):
    """Tracks inventory levels and recommends rebalancing"""
    
    def __init__(self, config: Dict):
        super().__init__("InventoryAgent", config)
        self.warehouse_stocks = {}
    
    def update_inventory(self, warehouse_id: str, sku: str, quantity: int, operation: str):
        """
        Update inventory for a warehouse/SKU combination.
        
        Args:
            warehouse_id: Warehouse identifier
            sku: Stock keeping unit
            quantity: Quantity to add/remove
            operation: 'add', 'remove', or 'set'
        """
        if warehouse_id not in self.warehouse_stocks:
            self.warehouse_stocks[warehouse_id] = {}
        
        current = self.warehouse_stocks[warehouse_id].get(sku, 0)
        
        if operation == 'add':
            self.warehouse_stocks[warehouse_id][sku] = current + quantity
        elif operation == 'remove':
            self.warehouse_stocks[warehouse_id][sku] = max(0, current - quantity)
        elif operation == 'set':
            self.warehouse_stocks[warehouse_id][sku] = quantity
    
    def get_total_stock(self, sku: str) -> int:
        """Get total stock across all warehouses for a SKU"""
        total = 0
        for warehouse in self.warehouse_stocks.values():
            total += warehouse.get(sku, 0)
        return total
    
    def get_warehouse_utilization(self, warehouse_id: str, capacity: int) -> float:
        """Calculate warehouse utilization percentage"""
        warehouse = self.warehouse_stocks.get(warehouse_id, {})
        total_stock = sum(warehouse.values())
        return total_stock / capacity if capacity > 0 else 0


class LogisticsAgent(SupplyChainAgent):
    """Plans shipments and optimizes routes"""
    
    def __init__(self, config: Dict):
        super().__init__("LogisticsAgent", config)
        self.warehouses = config['warehouses']
        self.shipping_cost_per_km = config['costs']['shipping_cost_per_km']
    
    def plan_shipment(self, source_warehouse: str, dest_warehouse: str, 
                     sku: str, quantity: int) -> Tuple[float, Decision]:
        """
        Plan a shipment between warehouses.
        
        Args:
            source_warehouse: Source warehouse ID
            dest_warehouse: Destination warehouse ID
            sku: Stock to ship
            quantity: Quantity to ship
            
        Returns:
            Tuple of (shipping_cost, decision_object)
        """
        source_loc = self.warehouses[source_warehouse]['location']
        dest_loc = self.warehouses[dest_warehouse]['location']
        
        distance = calculate_distance(source_loc, dest_loc)
        shipping_cost = distance * self.shipping_cost_per_km * quantity / 100  # Cost scales with quantity
        
        decision = Decision(
            agent_name=self.agent_name,
            day=0,
            decision_type='shipment',
            details={
                'from': source_warehouse,
                'to': dest_warehouse,
                'sku': sku,
                'quantity': quantity,
                'distance_km': round(distance, 1)
            },
            cost=shipping_cost,
            impact=f"Ship {quantity} units of {sku} from {source_warehouse} to {dest_warehouse}"
        )
        
        self.log_decision(decision)
        return shipping_cost, decision
    
    def consolidate_shipments(self, pending_shipments: List[Dict]) -> Dict:
        """Consolidate small shipments to reduce cost"""
        consolidation_threshold = self.config['agents']['logistics']['consolidation_threshold']
        
        # Group by route
        routes = {}
        for shipment in pending_shipments:
            route_key = (shipment['from'], shipment['to'])
            if route_key not in routes:
                routes[route_key] = []
            routes[route_key].append(shipment)
        
        # Consolidate if fill rate exceeds threshold
        consolidated = {}
        for route, shipments in routes.items():
            total_volume = sum(s.get('quantity', 0) for s in shipments)
            avg_capacity = 1000  # Average shipment capacity
            fill_rate = total_volume / avg_capacity
            
            if fill_rate >= consolidation_threshold:
                consolidated[route] = shipments
        
        return consolidated


class SupplierAgent(SupplyChainAgent):
    """Manages supplier relationships and procurement"""
    
    def __init__(self, config: Dict):
        super().__init__("SupplierAgent", config)
        self.suppliers = config['suppliers']
        self.procurement_per_unit = config['costs']['procurement_per_unit']
    
    def plan_procurement(self, day: int, sku: str, required_quantity: int) -> List[Decision]:
        """
        Plan procurement orders to meet demand.
        
        Args:
            day: Current simulation day
            sku: SKU to procure
            required_quantity: Required quantity
            
        Returns:
            List of procurement decisions
        """
        decisions = []
        remaining = required_quantity
        
        # Distribute across suppliers based on capacity and cost
        for supplier_id, supplier in self.suppliers.items():
            if remaining <= 0:
                break
            
            max_capacity = supplier['capacity_units_per_day']
            to_procure = min(remaining, max_capacity)
            
            cost = to_procure * supplier['cost_per_unit']
            
            decision = Decision(
                agent_name=self.agent_name,
                day=day,
                decision_type='procurement',
                details={
                    'supplier': supplier_id,
                    'sku': sku,
                    'quantity': to_procure,
                    'lead_time_days': supplier['lead_time_days'],
                    'cost_per_unit': supplier['cost_per_unit']
                },
                cost=cost,
                impact=f"Order {to_procure} units from {supplier_id} (delivery day {day + supplier['lead_time_days']})"
            )
            
            self.log_decision(decision)
            decisions.append(decision)
            remaining -= to_procure
        
        return decisions


class ExceptionHandler(SupplyChainAgent):
    """Detects and handles anomalies and constraint violations"""
    
    def __init__(self, config: Dict):
        super().__init__("ExceptionHandler", config)
        self.exceptions = []
    
    def check_constraints(self, state: Dict) -> List[Dict]:
        """
        Check for constraint violations.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check stockouts (inventory < 0)
        if 'inventory' in state:
            for warehouse, skus in state['inventory'].items():
                for sku, quantity in skus.items():
                    if quantity < 0:
                        anomalies.append({
                            'type': 'stockout',
                            'warehouse': warehouse,
                            'sku': sku,
                            'shortfall': abs(quantity),
                            'severity': 'high'
                        })
        
        # Check capacity violations
        if 'warehouse_capacity' in state:
            for warehouse, capacity_info in state['warehouse_capacity'].items():
                if capacity_info['used'] > capacity_info['capacity']:
                    anomalies.append({
                        'type': 'capacity_violation',
                        'warehouse': warehouse,
                        'excess': capacity_info['used'] - capacity_info['capacity'],
                        'severity': 'high'
                    })
        
        self.exceptions.extend(anomalies)
        return anomalies
    
    def get_exceptions(self) -> List[Dict]:
        """Get all detected exceptions"""
        return self.exceptions


class OrchestratorAgent(SupplyChainAgent):
    """Coordinates all agents and resolves conflicts"""
    
    def __init__(self, config: Dict, agents: Dict):
        super().__init__("Orchestrator", config)
        self.agents = agents  # Dict of agent instances
        self.conflict_resolution = config['agents']['orchestrator']['conflict_resolution']
    
    def coordinate(self, day: int, state: Dict) -> Dict:
        """
        Coordinate agent decisions and resolve conflicts.
        
        Returns:
            Final coordinated plan for the day
        """
        plan = {
            'day': day,
            'decisions': [],
            'total_cost': 0.0,
            'exceptions': []
        }
        
        # Get decisions from all agents
        all_decisions = []
        for agent in self.agents.values():
            if hasattr(agent, 'decisions'):
                all_decisions.extend(agent.decisions[-1:] if agent.decisions else [])
        
        # Check for exceptions
        exceptions = self.agents['exception'].check_constraints(state) if 'exception' in self.agents else []
        plan['exceptions'] = exceptions
        
        # Apply priority-based resolution
        if self.conflict_resolution == 'cost_priority':
            # Sort decisions by cost efficiency
            all_decisions.sort(key=lambda d: d.cost / max(1, len(str(d.details))), reverse=False)
        
        plan['decisions'] = all_decisions
        plan['total_cost'] = sum(d.cost for d in all_decisions)
        
        return plan
