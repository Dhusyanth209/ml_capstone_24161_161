# Quantum Fisher Information (QFI) and Grover metrics
import numpy as np

def compute_qfi_from_state(statevector, n_qubits=2):
    # Normalized QFI formula:
    # QFI = 4 * ( <Z_total^2> - <Z_total>^2 ) / (n^2)
    # where Z_total = Z (x) Z (for 2 sensing qubits)
    # Z (x) Z has eigenvalues +1, -1, so (Z(x)Z)^2 = I.
    # Therefore <Z_total^2> = 1.
    # <Z_total> = <psi| Z(x)Z |psi>.
    # QFI = 4 * (1 - <Z(x)Z>^2) / 4 = 1 - <Z(x)Z>^2 in [0, 1].
    # For general states of 2 sensing qubits:
    state = np.asarray(statevector).flatten()
    
    # Pauli Z matrix
    z = np.array([[1, 0], [0, -1]], dtype=complex)
    identity = np.eye(2, dtype=complex)
    
    if len(state) == 4:
        # 2-qubit state
        zz = np.kron(z, z)
        exp_zz = np.real(np.vdot(state, zz @ state))
        # Normalized QFI
        qfi = 1.0 - (exp_zz ** 2)
        return float(np.clip(qfi, 0.0, 1.0))
    elif len(state) == 8:
        # 3-qubit state (simplified QSC: 2 sensing qubits + 1 ancilla)
        # Z_sensing = Z (x) Z (x) I
        zz_i = np.kron(np.kron(z, z), identity)
        exp_zz = np.real(np.vdot(state, zz_i @ state))
        qfi = 1.0 - (exp_zz ** 2)
        return float(np.clip(qfi, 0.0, 1.0))
    else:
        # Fallback for arbitrary 2^n
        dim = len(state)
        n = int(np.log2(dim))
        op = z
        for _ in range(n - 1):
            op = np.kron(op, z)
        exp_op = np.real(np.vdot(state, op @ state))
        qfi = 1.0 - (exp_op ** 2)
        return float(np.clip(qfi, 0.0, 1.0))

def grover_success_probability(k, M, N):
    if N <= 0 or M <= 0:
        return 0.0
    theta = np.arcsin(np.sqrt(min(M / N, 1.0)))
    prob = np.sin((2 * k + 1) * theta) ** 2
    return float(np.clip(prob, 0.0, 1.0))

def grover_optimal_rotations(M, N):
    if N <= 0 or M <= 0:
        return 0
    return int(np.round((np.pi / 4.0) * np.sqrt(N / M)))

def mean_absolute_error(y_true, y_pred):
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))
