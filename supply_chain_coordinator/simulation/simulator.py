"""
Supply Chain Simulation Engine
Simulates 90-day supply chain operations with different scenarios
"""

import json
import random
from typing import Dict, List, Tuple
from copy import deepcopy


class DemandGenerator:
    """Generates daily demand based on scenario configuration"""
    
    def __init__(self, scenario_config: Dict):
        self.config = scenario_config
        self.base_demand = scenario_config.get('base_daily_demand', {})
        self.seasonal_factor = scenario_config.get('seasonal_factor', 1.0)
        self.volatility = scenario_config.get('volatility', 0.1)
        self.spike_days = scenario_config.get('spike_days', {})
        self.supplier_failure = scenario_config.get('supplier_failure', {})
    
    def generate_daily_demand(self, day: int) -> Dict[str, float]:
        """Generate demand for a specific day"""
        demand = {}
        
        # Check if we're in a spike period
        in_spike = False
        if self.spike_days:
            start = self.spike_days.get('start', 0)
            duration = self.spike_days.get('duration', 0)
            if start <= day < start + duration:
                in_spike = True
                factor = self.seasonal_factor
            else:
                factor = 1.0
        else:
            factor = self.seasonal_factor
        
        for sku, base in self.base_demand.items():
            # Add randomness (volatility)
            noise = random.normalvariate(0, base * self.volatility)
            daily = (base + noise) * factor
            demand[sku] = max(0, daily)
        
        return demand


class SupplyChainSimulator:
    """Simulates supply chain operations over time"""
    
    def __init__(self, config: Dict, scenario_name: str):
        self.config = config
        self.scenario_name = scenario_name
        self.scenario_config = config['demand_scenarios'].get(scenario_name, {})
        
        self.horizon_days = config['simulation']['horizon_days']
        
        # Initialize warehouses
        self.warehouses = {}
        for wh_id, wh_config in config['warehouses'].items():
            self.warehouses[wh_id] = {
                'name': wh_config['name'],
                'capacity': wh_config['capacity'],
                'stock': deepcopy(wh_config['initial_stock']),
                'location': wh_config['location']
            }
        
        # Initialize suppliers
        self.suppliers = config['suppliers']
        
        # Initialize tracking
        self.daily_logs = []
        self.demand_generator = DemandGenerator(self.scenario_config)
        
        # Metrics tracking
        self.total_cost = 0.0
        self.total_fulfilled = 0
        self.total_demand = 0
        self.stockout_days = 0
        self.inventory_holding_cost = 0.0
        self.procurement_cost = 0.0
        self.shipping_cost = 0.0
    
    def simulate(self) -> List[Dict]:
        """Run the simulation for the entire horizon"""
        
        for day in range(self.horizon_days):
            daily_log = self._simulate_day(day)
            self.daily_logs.append(daily_log)
        
        return self.daily_logs
    
    def _simulate_day(self, day: int) -> Dict:
        """Simulate a single day of operations"""
        
        log = {
            'day': day,
            'demand': self.demand_generator.generate_daily_demand(day),
            'actions': [],
            'inventory_start': self._get_total_inventory(),
            'cost': 0.0
        }
        
        # Process demand
        for sku, daily_demand in log['demand'].items():
            self.total_demand += daily_demand
            
            # Try to fulfill from inventory
            fulfilled = self._fulfill_demand(sku, int(daily_demand))
            self.total_fulfilled += fulfilled
            
            if fulfilled < daily_demand:
                self.stockout_days += 1
                shortfall = daily_demand - fulfilled
                log['actions'].append({
                    'type': 'stockout',
                    'sku': sku,
                    'shortfall': int(shortfall)
                })
            
            # Automatic reorder if stock low
            if self._get_sku_stock(sku) < daily_demand * 3:  # Less than 3 days
                order_qty = int(daily_demand * 10)  # Order for 10 days
                cost = order_qty * self.suppliers['supplier_1']['cost_per_unit']
                self.procurement_cost += cost
                log['actions'].append({
                    'type': 'procurement',
                    'sku': sku,
                    'quantity': order_qty,
                    'cost': round(cost, 2)
                })
                # Add stock after lead time (simplified - add today for simulation)
                self._add_stock_to_largest_warehouse(sku, order_qty)
        
        # Calculate holding cost
        current_stock = self._get_total_inventory()
        holding_cost = current_stock * self.config['costs']['inventory_holding_cost_per_unit_per_day']
        self.inventory_holding_cost += holding_cost
        log['cost'] = round(self.procurement_cost + self.shipping_cost + holding_cost, 2)
        
        self.total_cost += log['cost']
        log['inventory_end'] = current_stock
        
        return log
    
    def _fulfill_demand(self, sku: str, quantity: int) -> int:
        """Fulfill demand from available inventory"""
        fulfilled = 0
        remaining = quantity
        
        # Try each warehouse in order
        for wh_id in sorted(self.warehouses.keys()):
            if remaining <= 0:
                break
            
            available = self.warehouses[wh_id]['stock'].get(sku, 0)
            to_fulfill = min(remaining, available)
            
            self.warehouses[wh_id]['stock'][sku] = available - to_fulfill
            fulfilled += to_fulfill
            remaining -= to_fulfill
        
        return fulfilled
    
    def _get_sku_stock(self, sku: str) -> int:
        """Get total stock for a SKU across all warehouses"""
        total = 0
        for wh in self.warehouses.values():
            total += wh['stock'].get(sku, 0)
        return total
    
    def _get_total_inventory(self) -> int:
        """Get total inventory across all warehouses and SKUs"""
        total = 0
        for wh in self.warehouses.values():
            total += sum(wh['stock'].values())
        return total
    
    def _add_stock_to_largest_warehouse(self, sku: str, quantity: int):
        """Add stock to warehouse with most space"""
        largest_wh = max(
            self.warehouses.items(),
            key=lambda x: x[1]['capacity'] - sum(x[1]['stock'].values())
        )
        largest_wh[1]['stock'][sku] = largest_wh[1]['stock'].get(sku, 0) + quantity
    
    def get_metrics(self) -> Dict:
        """Calculate scenario metrics"""
        fulfillment_rate = self.total_fulfilled / max(1, self.total_demand)
        avg_daily_cost = self.total_cost / max(1, self.horizon_days)
        
        return {
            'scenario': self.scenario_name,
            'horizon_days': self.horizon_days,
            'total_cost': round(self.total_cost, 2),
            'avg_daily_cost': round(avg_daily_cost, 2),
            'procurement_cost': round(self.procurement_cost, 2),
            'holding_cost': round(self.inventory_holding_cost, 2),
            'shipping_cost': round(self.shipping_cost, 2),
            'total_demand': int(self.total_demand),
            'total_fulfilled': int(self.total_fulfilled),
            'fulfillment_rate': round(fulfillment_rate, 3),
            'stockout_incidents': self.stockout_days,
            'final_inventory': self._get_total_inventory()
        }
