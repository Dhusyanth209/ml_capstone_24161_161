import pytest
import numpy as np
from src.gpa.config import GPAConfig
from src.gpa.metrics import compute_qfi_from_state, grover_success_probability, grover_optimal_rotations
from src.gpa.qsc_environment import build_base_qsc, build_simplified_qsc, get_statevector
from src.gpa.qpe import QuantumPhaseEstimator
from src.gpa.gpa_agent import GPAAgent
from src.gpa.gaqa_baseline import GAQAAgent

def test_qfi_bounds():
    psi_bell = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / np.sqrt(2)
    qfi = compute_qfi_from_state(psi_bell, n_qubits=2)
    assert 0.0 <= qfi <= 1.0

def test_qsc_circuits():
    qc_base = build_base_qsc(np.pi/4, np.pi/4, 0.5)
    assert qc_base.num_qubits == 2
    sv_base = get_statevector(qc_base)
    assert len(sv_base) == 4
    
    qc_simp = build_simplified_qsc(np.pi/4, np.pi/4, 0.5)
    assert qc_simp.num_qubits == 3
    sv_simp = get_statevector(qc_simp)
    assert len(sv_simp) == 8

def test_gpa_agent_base_simulation():
    agent = GPAAgent()
    res = agent.run_base_qsc_optimization()
    assert res['optimal_rotations'] == 50
    assert np.isclose(res['max_qfi'], 1.0, atol=1e-3)
    assert len(res['rotations']) == 61

def test_gpa_vs_gaqa_advantage():
    agent = GPAAgent()
    gaqa = GAQAAgent()
    res_gpa = agent.run_simplified_qsc_optimization()
    res_gaqa = gaqa.run_sequential_optimization(total_rotations=50)
    qfi_gpa_40 = res_gpa['qfi'][40]
    qfi_gaqa_40 = res_gaqa['qfi'][40]
    assert qfi_gpa_40 > qfi_gaqa_40
    assert np.isclose(qfi_gpa_40, 0.5, atol=1e-2)
    assert np.isclose(qfi_gaqa_40, 0.45, atol=1e-2)
