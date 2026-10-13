# Command-Line Experiment Runner for GPA Quantum Sensor Prototype
import argparse
from inference import run_full_pipeline
from src.gpa.config import GPAConfig
from src.gpa.gpa_agent import GPAAgent
from src.gpa.gaqa_baseline import GAQAAgent

def main():
    parser = argparse.ArgumentParser(description='GPA Quantum Sensor Optimization')
    parser.add_argument('--run-all', action='store_true')
    parser.add_argument('--base-qsc', action='store_true')
    parser.add_argument('--simplified-qsc', action='store_true')
    parser.add_argument('--compare', action='store_true')
    args = parser.parse_args()

    config = GPAConfig()
    agent = GPAAgent(config)

    if args.base_qsc:
        res = agent.run_base_qsc_optimization()
        print('Base QSC Optimal Rotations:', res['optimal_rotations'])
        print('Base QSC Max QFI:', res['max_qfi'])
    elif args.simplified_qsc:
        res = agent.run_simplified_qsc_optimization()
        print('Simplified QSC Optimal Rotations:', res['optimal_rotations'])
        print('Simplified QSC Max QFI:', res['max_qfi'])
    elif args.compare:
        gaqa = GAQAAgent(config)
        res_gpa = agent.run_simplified_qsc_optimization()
        res_gaqa = gaqa.run_sequential_optimization(total_rotations=config.max_grover_rotations_simplified)
        print('GPA QFI at k=40:', res_gpa['qfi'][40])
        print('GAQA QFI at k=40:', res_gaqa['qfi'][40])
    else:
        run_full_pipeline()

if __name__ == '__main__':
    main()
