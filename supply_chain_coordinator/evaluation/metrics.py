"""
Evaluation: Compare multi-agent system performance vs. baseline policies
"""

import json
from typing import Dict, List


class BaselineSimulator:
    """Implements traditional reorder point strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.warehouses = {}
        
        for wh_id, wh_config in config['warehouses'].items():
            self.warehouses[wh_id] = {
                'name': wh_config['name'],
                'capacity': wh_config['capacity'],
                'stock': dict(wh_config['initial_stock']),
                'location': wh_config['location']
            }
    
    def simulate_day(self, day: int, demand: Dict[str, float]) -> Dict:
        """Simulate one day using baseline policy (simple reorder point)"""
        
        log = {
            'day': day,
            'demand': demand,
            'actions': [],
            'cost': 0.0
        }
        
        baseline_safety_multiplier = self.config['baseline_policy']['safety_stock_multiplier']
        
        for sku, daily_demand in demand.items():
            # Get current stock
            current_stock = sum(wh['stock'].get(sku, 0) for wh in self.warehouses.values())
            
            # Fulfill demand
            fulfilled, cost = self._fulfill_demand(sku, int(daily_demand))
            log['cost'] += cost
            
            # Reorder point logic: if stock <= demand * 5 days
            reorder_point = daily_demand * 5 * baseline_safety_multiplier
            
            if current_stock <= reorder_point:
                order_qty = int(daily_demand * 10)
                procurement_cost = order_qty * self.config['costs']['procurement_per_unit']
                log['cost'] += procurement_cost
                log['actions'].append({
                    'type': 'reorder',
                    'sku': sku,
                    'quantity': order_qty
                })
                # Add to largest warehouse
                largest_wh = max(self.warehouses.items(),
                               key=lambda x: x[1]['capacity'] - sum(x[1]['stock'].values()))
                largest_wh[1]['stock'][sku] = largest_wh[1]['stock'].get(sku, 0) + order_qty
        
        return log
    
    def _fulfill_demand(self, sku: str, quantity: int) -> tuple:
        """Fulfill from available inventory"""
        fulfilled = 0
        cost = 0
        
        for wh in sorted(self.warehouses.keys()):
            if fulfilled >= quantity:
                break
            
            available = self.warehouses[wh]['stock'].get(sku, 0)
            to_fulfill = min(quantity - fulfilled, available)
            
            self.warehouses[wh]['stock'][sku] = available - to_fulfill
            fulfilled += to_fulfill
            cost += to_fulfill * 0.10  # Small fulfillment cost
        
        return fulfilled, cost


class EvaluationMetrics:
    """Calculate comparison metrics between agent and baseline"""
    
    @staticmethod
    def calculate_improvements(agent_metrics: Dict, baseline_metrics: Dict) -> Dict:
        """
        Calculate improvement percentages.
        
        Args:
            agent_metrics: Metrics from agent-based simulation
            baseline_metrics: Metrics from baseline simulation
            
        Returns:
            Dictionary with improvement percentages
        """
        improvements = {}
        
        # Cost improvement (lower is better)
        agent_cost = agent_metrics.get('total_cost', 0)
        baseline_cost = baseline_metrics.get('total_cost', agent_cost)
        cost_improvement = ((baseline_cost - agent_cost) / baseline_cost * 100) if baseline_cost > 0 else 0
        improvements['cost_reduction_pct'] = round(cost_improvement, 1)
        improvements['cost_savings_usd'] = round(baseline_cost - agent_cost, 2)
        
        # Fulfillment improvement (higher is better)
        agent_fulfillment = agent_metrics.get('fulfillment_rate', 0)
        baseline_fulfillment = baseline_metrics.get('fulfillment_rate', 0)
        fulfillment_improvement = (agent_fulfillment - baseline_fulfillment) * 100
        improvements['fulfillment_improvement_pct'] = round(fulfillment_improvement, 1)
        
        # Stockout reduction
        agent_stockouts = agent_metrics.get('stockout_incidents', 0)
        baseline_stockouts = baseline_metrics.get('stockout_incidents', 0)
        stockout_reduction = baseline_stockouts - agent_stockouts
        improvements['stockout_reduction'] = int(stockout_reduction)
        
        # Inventory turns efficiency
        agent_holding = agent_metrics.get('holding_cost', 0)
        baseline_holding = baseline_metrics.get('holding_cost', 0)
        holding_improvement = ((baseline_holding - agent_holding) / baseline_holding * 100) if baseline_holding > 0 else 0
        improvements['holding_cost_reduction_pct'] = round(holding_improvement, 1)
        
        return improvements


def generate_evaluation_report(agent_results: Dict, baseline_results: Dict = None) -> Dict:
    """
    Generate comprehensive evaluation report.
    
    Args:
        agent_results: Results from agent simulations
        baseline_results: Results from baseline simulations (optional)
        
    Returns:
        Evaluation report with comparisons
    """
    
    report = {
        'evaluation_summary': {},
        'scenario_analysis': {}
    }
    
    # Analyze each scenario
    for scenario_name, agent_scenario in agent_results.get('scenarios', {}).items():
        agent_metrics = agent_scenario.get('metrics', {})
        
        scenario_eval = {
            'agent_metrics': agent_metrics,
            'improvements_vs_baseline': {}
        }
        
        # If baseline results available, compare
        if baseline_results and scenario_name in baseline_results.get('scenarios', {}):
            baseline_scenario = baseline_results['scenarios'][scenario_name]
            baseline_metrics = baseline_scenario.get('metrics', {})
            
            improvements = EvaluationMetrics.calculate_improvements(agent_metrics, baseline_metrics)
            scenario_eval['improvements_vs_baseline'] = improvements
            scenario_eval['baseline_metrics'] = baseline_metrics
        
        report['scenario_analysis'][scenario_name] = scenario_eval
    
    # Overall summary
    if agent_results.get('comparison'):
        report['evaluation_summary'] = {
            'best_cost_scenario': agent_results['comparison']['best_cost']['scenario'],
            'best_cost_value': agent_results['comparison']['best_cost']['value'],
            'best_fulfillment_scenario': agent_results['comparison']['best_fulfillment']['scenario'],
            'best_fulfillment_rate': agent_results['comparison']['best_fulfillment']['value'],
            'average_cost_across_scenarios': round(
                sum(s['metrics']['total_cost'] for s in agent_results['scenarios'].values()) / 
                max(1, len(agent_results['scenarios'])), 2
            ),
            'average_fulfillment_across_scenarios': round(
                sum(s['metrics']['fulfillment_rate'] for s in agent_results['scenarios'].values()) / 
                max(1, len(agent_results['scenarios'])), 3
            )
        }
    
    return report


if __name__ == '__main__':
    # Load agent results
    with open('demo/scenario_results.json', 'r') as f:
        agent_results = json.load(f)
    
    # Generate evaluation report
    report = generate_evaluation_report(agent_results)
    
    # Save report
    with open('evaluation/evaluation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✓ Evaluation report generated: evaluation/evaluation_report.json")
