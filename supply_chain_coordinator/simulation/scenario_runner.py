"""
Scenario Runner: Execute supply chain simulations across multiple scenarios
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import load_supply_chain_config
from simulator import SupplyChainSimulator


def run_all_scenarios(config_path: str = 'config/supply_chain_config.yaml') -> Dict:
    """
    Run supply chain simulations across all defined scenarios.
    
    Returns:
        Dictionary with results for all scenarios
    """
    config = load_supply_chain_config(config_path)
    
    scenario_names = list(config['demand_scenarios'].keys())
    results = {
        'timestamp': str(__import__('datetime').datetime.now()),
        'scenarios': {}
    }
    
    print("="*80)
    print("SUPPLY CHAIN MULTI-AGENT COORDINATOR - SIMULATION")
    print("="*80)
    print(f"\nRunning {len(scenario_names)} scenarios...\n")
    
    for scenario_name in scenario_names:
        print(f"▶ Scenario: {scenario_name.upper()}")
        
        # Get scenario description
        scenario_config = config['demand_scenarios'][scenario_name]
        description = scenario_config.get('description', 'No description')
        print(f"  Description: {description}")
        
        # Run simulation
        simulator = SupplyChainSimulator(config, scenario_name)
        daily_logs = simulator.simulate()
        metrics = simulator.get_metrics()
        
        # Store results
        results['scenarios'][scenario_name] = {
            'description': description,
            'metrics': metrics,
            'daily_summary': _summarize_daily_logs(daily_logs),
            'final_state': {
                'warehouses': {
                    wh_id: {
                        'name': wh['name'],
                        'total_stock': sum(wh['stock'].values()),
                        'utilization': round(sum(wh['stock'].values()) / wh['capacity'], 2)
                    }
                    for wh_id, wh in simulator.warehouses.items()
                }
            }
        }
        
        # Print summary
        print(f"  ✓ Total Cost: ${metrics['total_cost']}")
        print(f"  ✓ Fulfillment Rate: {metrics['fulfillment_rate']*100:.1f}%")
        print(f"  ✓ Stockout Incidents: {metrics['stockout_incidents']}")
        print()
    
    return results


def _summarize_daily_logs(daily_logs: list) -> Dict:
    """Summarize daily logs into key statistics"""
    daily_costs = [log['cost'] for log in daily_logs]
    daily_inventory = [log['inventory_end'] for log in daily_logs]
    
    return {
        'avg_daily_cost': round(sum(daily_costs) / len(daily_costs), 2) if daily_costs else 0,
        'max_daily_cost': round(max(daily_costs), 2) if daily_costs else 0,
        'min_daily_cost': round(min(daily_costs), 2) if daily_costs else 0,
        'avg_inventory': round(sum(daily_inventory) / len(daily_inventory), 2) if daily_inventory else 0,
        'max_inventory': max(daily_inventory) if daily_inventory else 0,
        'min_inventory': min(daily_inventory) if daily_inventory else 0,
    }


def compare_scenarios(results: Dict) -> Dict:
    """Compare metrics across scenarios"""
    comparison = {
        'scenarios': {},
        'best_cost': None,
        'best_fulfillment': None,
        'worst_fulfillment': None
    }
    
    best_cost_scenario = None
    best_cost_value = float('inf')
    best_fulfillment_scenario = None
    best_fulfillment_value = 0
    worst_fulfillment_scenario = None
    worst_fulfillment_value = 1.0
    
    for scenario_name, scenario_data in results.get('scenarios', {}).items():
        metrics = scenario_data['metrics']
        comparison['scenarios'][scenario_name] = {
            'cost': metrics['total_cost'],
            'fulfillment_rate': metrics['fulfillment_rate'],
            'stockout_incidents': metrics['stockout_incidents']
        }
        
        if metrics['total_cost'] < best_cost_value:
            best_cost_value = metrics['total_cost']
            best_cost_scenario = scenario_name
        
        if metrics['fulfillment_rate'] > best_fulfillment_value:
            best_fulfillment_value = metrics['fulfillment_rate']
            best_fulfillment_scenario = scenario_name
        
        if metrics['fulfillment_rate'] < worst_fulfillment_value:
            worst_fulfillment_value = metrics['fulfillment_rate']
            worst_fulfillment_scenario = scenario_name
    
    comparison['best_cost'] = {'scenario': best_cost_scenario, 'value': round(best_cost_value, 2)}
    comparison['best_fulfillment'] = {'scenario': best_fulfillment_scenario, 'value': round(best_fulfillment_value, 3)}
    comparison['worst_fulfillment'] = {'scenario': worst_fulfillment_scenario, 'value': round(worst_fulfillment_value, 3)}
    
    return comparison


if __name__ == '__main__':
    from typing import Dict
    
    # Run all scenarios
    results = run_all_scenarios()
    
    # Compare scenarios
    comparison = compare_scenarios(results)
    results['comparison'] = comparison
    
    # Save results
    with open('demo/scenario_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print comparison
    print("="*80)
    print("SCENARIO COMPARISON")
    print("="*80)
    print(f"\n✓ Best Cost Scenario: {comparison['best_cost']['scenario']}")
    print(f"  Cost: ${comparison['best_cost']['value']}")
    print(f"\n✓ Best Fulfillment: {comparison['best_fulfillment']['scenario']}")
    print(f"  Rate: {comparison['best_fulfillment']['value']*100:.1f}%")
    print(f"\n✓ Worst Fulfillment: {comparison['worst_fulfillment']['scenario']}")
    print(f"  Rate: {comparison['worst_fulfillment']['value']*100:.1f}%")
    
    print(f"\n✓ Results saved to demo/scenario_results.json")
    print("="*80)
