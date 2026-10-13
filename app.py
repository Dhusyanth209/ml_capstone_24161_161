# Flask Application for GPA Quantum Sensor Circuit Prototype
import os
import csv
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from inference import run_full_pipeline

app = Flask(__name__, template_folder='templates', static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

def load_summary():
    summary_path = os.path.join(DATASET_DIR, 'simulation_summary.json')
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'base_optimal_k': 50,
        'base_max_qfi': 1.0,
        'simplified_optimal_k': 40,
        'simplified_max_qfi': 0.5,
        'gaqa_max_qfi': 0.45,
        'qpe_min_mae': 0.003906
    }

def read_csv(filename):
    file_path = os.path.join(DATASET_DIR, filename)
    rows = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    return rows

@app.route('/app-static/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

@app.route('/app-results/<path:filename>')
def custom_results(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'results'), filename)

@app.route('/')
def dashboard():
    summary = load_summary()
    return render_template('dashboard.html', summary=summary, active_tab='dashboard')

@app.route('/inference')
def inference_page():
    message = request.args.get('msg', '')
    return render_template('inference.html', message=message, active_tab='inference')

@app.route('/run-simulation', methods=['POST'])
def trigger_simulation():
    run_full_pipeline()
    return redirect(url_for('inference_page', msg='Simulation pipeline executed and refreshed successfully!'))

@app.route('/dataset')
def dataset_page():
    base_data = read_csv('base_qsc_rotations.csv')
    comp_data = read_csv('gpa_vs_gaqa_comparison.csv')
    return render_template('dataset.html', base_data=base_data, comp_data=comp_data, active_tab='dataset')

@app.route('/interpretation')
def interpretation_page():
    return render_template('interpretation.html', active_tab='interpretation')

@app.route('/novelty')
def novelty_page():
    return render_template('novelty.html', active_tab='novelty')

if __name__ == '__main__':
    if not os.path.exists(os.path.join(DATASET_DIR, 'simulation_summary.json')):
        run_full_pipeline()
    app.run(host='127.0.0.1', port=5000, debug=True)
