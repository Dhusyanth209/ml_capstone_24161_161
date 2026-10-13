# Quantum Phase Estimation (QPE) module
# Value function estimation via phase estimation on unitary operators
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector

class QuantumPhaseEstimator:
    def __init__(self, n_counting=4):
        self.n_counting = n_counting

    def build_qpe_circuit(self, unitary_gate, eigenstate_prep_circuit=None):
        n_target = unitary_gate.num_qubits
        qc = QuantumCircuit(self.n_counting + n_target, self.n_counting)
        
        # Eigenstate preparation
        if eigenstate_prep_circuit is not None:
            qc.compose(eigenstate_prep_circuit, qubits=range(self.n_counting, self.n_counting + n_target), inplace=True)
            
        # Superposition on counting qubits
        for i in range(self.n_counting):
            qc.h(i)
            
        # Controlled-U^(2^j) operations
        for j in range(self.n_counting):
            power = 2 ** j
            u_power = unitary_gate.power(power)
            c_u = u_power.control(1)
            qc.compose(c_u, qubits=[j] + list(range(self.n_counting, self.n_counting + n_target)), inplace=True)
            
        # Inverse QFT on counting qubits
        inv_qft = QFT(self.n_counting, inverse=True)
        qc.compose(inv_qft, qubits=range(self.n_counting), inplace=True)
        
        return qc

    def estimate_value_error_curve(self, max_counting_bits=8):
        # Generates Mean Absolute Error vs counting qubits sweep
        # MAE scales theoretically as O(2^-t)
        bits = list(range(1, max_counting_bits + 1))
        mae_values = []
        for t in bits:
            # Analytical precision of t-bit QPE: phase resolution delta = 1 / (2^t)
            error = 1.0 / (2 ** t)
            mae_values.append(error)
        return bits, mae_values
