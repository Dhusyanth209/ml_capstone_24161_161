# Quantum Sensor Circuit (QSC) Environment
# Implements Base QSC and Simplified QSC with the paper's exact unitary definitions
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

def squeezing_unitary(theta):
    # exp(-i * (theta / 2) * (Z (x) Z)) = cos(theta / 2) * I - i * sin(theta / 2) * (Z (x) Z)
    z = np.array([[1, 0], [0, -1]], dtype=complex)
    zz = np.kron(z, z)
    eye = np.eye(4, dtype=complex)
    u = np.cos(theta / 2.0) * eye - 1j * np.sin(theta / 2.0) * zz
    return u

def v_matrix():
    # Paper definition: V = (1 + i) / 2 * [[1, -i], [-i, 1]]
    # Note: V @ V^dagger = I, so V is unitary
    v = ((1.0 + 1j) / 2.0) * np.array([[1.0, -1j], [-1j, 1.0]], dtype=complex)
    return v

def v_dagger_matrix():
    # V^dagger = (1 - i) / 2 * [[1, i], [i, 1]]
    vdag = ((1.0 - 1j) / 2.0) * np.array([[1.0, 1j], [1j, 1.0]], dtype=complex)
    return vdag

def build_base_qsc(theta_1, theta_2, phi_target=0.5):
    # Base QSC (2 qubits):
    # |00> -> H on each -> Squeezing(theta_1) -> Rz(phi_target) on each -> Squeezing(theta_2)
    qc = QuantumCircuit(2, name='Base_QSC')
    qc.h(0)
    qc.h(1)
    
    # Squeezing unitary 1
    u1 = squeezing_unitary(theta_1)
    qc.unitary(Operator(u1), [0, 1], label='S_th1')
    
    # Parameter encoding: Rz(phi_target)
    qc.rz(phi_target, 0)
    qc.rz(phi_target, 1)
    
    # Squeezing unitary 2
    u2 = squeezing_unitary(theta_2)
    qc.unitary(Operator(u2), [0, 1], label='S_th2')
    
    return qc

def build_simplified_qsc(theta_1, theta_2, phi_target=0.5):
    # Simplified QSC: 3 qubits (q0, q1 sensing, q2 ancilla)
    # Replaces multi-qubit squeezing entanglers with Controlled-V gates + single-qubit rotations
    qc = QuantumCircuit(3, name='Simplified_QSC')
    
    # Initial state preparation
    qc.h(0)
    qc.h(1)
    qc.h(2)
    
    # Controlled-V and single rotations approximating squeezing theta_1
    v_op = Operator(v_matrix())
    vdag_op = Operator(v_dagger_matrix())
    
    # Entanglement step 1
    qc.unitary(v_op, [0], label='V')
    qc.cx(0, 1)
    qc.rz(theta_1 / 2.0, 1)
    qc.cx(0, 1)
    qc.unitary(vdag_op, [0], label='V_dag')
    
    # Parameter encoding on sensing qubits
    qc.rz(phi_target, 0)
    qc.rz(phi_target, 1)
    
    # Entanglement step 2
    qc.unitary(v_op, [1], label='V')
    qc.cx(1, 2)
    qc.rz(theta_2 / 2.0, 2)
    qc.cx(1, 2)
    qc.unitary(vdag_op, [1], label='V_dag')
    
    return qc

def get_statevector(qc):
    return Statevector.from_instruction(qc).data
