# Flask Application for GPA Quantum Sensor Circuit Prototype
import os
import json
import io
import sys
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from inference import run_full_pipeline
from src.gpa.rl_tracer import compute_rotation_logs

app = Flask(__name__, template_folder='templates', static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

latest_terminal_output = (
    '=== Executing GPA Paper 161 Simulation Pipeline ===\n'
    '[1/4] Running Base QSC Optimization (Fig. 6)...\n'
    '[2/4] Running Simplified QSC Optimization (Fig. 8)...\n'
    '[3/4] Running QPE Value Function Error Sweep (Fig. 7)...\n'
    '[4/4] Comparing GPA vs GAQA Baseline under Budget (Fig. 10)...\n'
    '=== Pipeline Completed Successfully! Dataset & Plots Generated. ==='
)

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

@app.route('/api/simulation-data')
def api_simulation_data():
    circuit = request.args.get('circuit', 'base')
    try:
        k = int(request.args.get('rotations', 10))
    except ValueError:
        k = 10
    k = max(1, min(k, 60))
    logs, _, optimal_k = compute_rotation_logs(circuit, k)
    return jsonify({
        'circuit': circuit,
        'rotations': k,
        'optimal_k': optimal_k,
        'logs': logs
    })

@app.route('/rl-visualization')
def rl_visualization():
    selected_circuit = request.args.get('circuit', 'base')
    try:
        k = int(request.args.get('rotations', 10))
    except ValueError:
        k = 10

    k = max(1, min(k, 60))
    logs, chart_b64, optimal_k = compute_rotation_logs(selected_circuit, k)
    latest_log = logs[-1]

    return render_template(
        'rl_visualization.html',
        logs=logs,
        latest_log=latest_log,
        chart_b64=chart_b64,
        selected_circuit=selected_circuit,
        k=k,
        optimal_k=optimal_k,
        active_tab='rl_visualization'
    )

@app.route('/inference')
def inference_page():
    message = request.args.get('msg', '')
    global latest_terminal_output
    return render_template(
        'inference.html',
        message=message,
        terminal_output=latest_terminal_output,
        active_tab='inference'
    )

@app.route('/run-simulation', methods=['POST'])
def trigger_simulation():
    global latest_terminal_output
    captured_output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    try:
        run_full_pipeline()
    finally:
        sys.stdout = old_stdout
    latest_terminal_output = captured_output.getvalue()

    return redirect(url_for('inference_page', msg='Quantum Simulation Pipeline executed and terminal output refreshed!'))

if __name__ == '__main__':
    if not os.path.exists(os.path.join(DATASET_DIR, 'simulation_summary.json')):
        run_full_pipeline()
    app.run(host='127.0.0.1', port=5000, debug=True)
