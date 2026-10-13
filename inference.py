# Complete End-to-End Simulation Pipeline and Data Generator
import os
import csv
import json
import numpy as np
from src.gpa.config import GPAConfig
from src.gpa.gpa_agent import GPAAgent
from src.gpa.gaqa_baseline import GAQAAgent
from src.gpa.qpe import QuantumPhaseEstimator
from src.gpa.visualization import (
    plot_qfi_vs_rotations_base,
    plot_qfi_vs_rotations_simplified,
    plot_qpe_mae_vs_bits,
    plot_comparison_gpa_vs_gaqa
)

def run_full_pipeline():
    print('=== Executing GPA Paper 161 Simulation Pipeline ===')
    config = GPAConfig()
    agent = GPAAgent(config)
    gaqa = GAQAAgent(config)
    qpe = QuantumPhaseEstimator()
    
    os.makedirs('dataset', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # 1. Base QSC Simulation (Fig. 6)
    print('[1/4] Running Base QSC Optimization (Fig. 6)...')
    base_results = agent.run_base_qsc_optimization()
    with open('dataset/base_qsc_rotations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['grover_rotations', 'qfi', 'p_success'])
        for r, q, p in zip(base_results['rotations'], base_results['qfi'], base_results['p_success']):
            writer.writerow([r, round(q, 4), round(p, 4)])
    plot_qfi_vs_rotations_base(base_results, 'results/fig6_base_qsc.png')
    
    # 2. Simplified QSC Simulation (Fig. 8)
    print('[2/4] Running Simplified QSC Optimization (Fig. 8)...')
    simp_results = agent.run_simplified_qsc_optimization()
    with open('dataset/simplified_qsc_rotations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['grover_rotations', 'qfi', 'p_success'])
        for r, q, p in zip(simp_results['rotations'], simp_results['qfi'], simp_results['p_success']):
            writer.writerow([r, round(q, 4), round(p, 4)])
    plot_qfi_vs_rotations_simplified(simp_results, 'results/fig8_simplified_qsc.png')
    
    # 3. QPE MAE Sweep (Fig. 7 / Fig. 5)
    print('[3/4] Running QPE Value Function Error Sweep (Fig. 7)...')
    bits, mae = qpe.estimate_value_error_curve(max_counting_bits=8)
    with open('dataset/qpe_mae_curve.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['counting_qubits', 'mean_absolute_error'])
        for b, m in zip(bits, mae):
            writer.writerow([b, round(m, 6)])
    plot_qpe_mae_vs_bits(bits, mae, 'results/fig7_qpe_mae.png')
    
    # 4. GPA vs GAQA Baseline Comparison (Fig. 10)
    print('[4/4] Comparing GPA vs GAQA Baseline under Budget (Fig. 10)...')
    gaqa_results = gaqa.run_sequential_optimization(total_rotations=config.max_grover_rotations_simplified)
    with open('dataset/gpa_vs_gaqa_comparison.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['rotations', 'gpa_qfi', 'gaqa_qfi'])
        for r, g_q, ga_q in zip(simp_results['rotations'], simp_results['qfi'], gaqa_results['qfi']):
            writer.writerow([r, round(g_q, 4), round(ga_q, 4)])
    plot_comparison_gpa_vs_gaqa(simp_results, gaqa_results, 'results/fig10_gpa_vs_gaqa.png')
    
    # Export summary metadata for UI
    summary = {
        'base_optimal_k': base_results['optimal_rotations'],
        'base_max_qfi': round(base_results['max_qfi'], 4),
        'base_initial_qfi': round(base_results['initial_qfi'], 4),
        'simplified_optimal_k': simp_results['optimal_rotations'],
        'simplified_max_qfi': round(simp_results['max_qfi'], 4),
        'simplified_initial_qfi': round(simp_results['initial_qfi'], 4),
        'qpe_min_mae': round(mae[-1], 6),
        'gaqa_max_qfi': round(max(gaqa_results['qfi']), 4)
    }
    with open('dataset/simulation_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
        
    print('=== Pipeline Completed Successfully! Dataset & Plots Generated. ===')

if __name__ == '__main__':
    run_full_pipeline()
