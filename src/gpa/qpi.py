# Quantum Policy Iteration (QPI) and Grover search dynamics
import numpy as np

def grover_qfi_trajectory(k_range, qfi_initial, qfi_target, k_optimal):
    # Model amplitude amplification of marked optimal sensor policies:
    # P(success | k) = sin^2((2k + 1) * theta)
    # where sin^2((2 * k_optimal + 1) * theta) = 1.0 -> theta = pi / (2 * (2 * k_optimal + 1))
    theta = np.pi / (2.0 * (2.0 * k_optimal + 1.0))
    qfi_curve = []
    p_succ_curve = []
    
    for k in k_range:
        # Grover rotation probability
        # Saturate at k_optimal to represent agent picking optimal stopping point
        k_eff = min(k, k_optimal)
        p = np.sin((2.0 * k_eff + 1.0) * theta) ** 2
        # Smooth interpolation between baseline initial policy QFI and target maximum
        qfi = qfi_initial + (qfi_target - qfi_initial) * p
        qfi_curve.append(float(np.clip(qfi, 0.0, 1.0)))
        p_succ_curve.append(float(np.clip(p, 0.0, 1.0)))
        
    return qfi_curve, p_succ_curve
