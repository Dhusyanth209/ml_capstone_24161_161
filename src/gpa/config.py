# GPA Configuration
import numpy as np
from dataclasses import dataclass

@dataclass
class GPAConfig:
    n_sensing_qubits: int = 2
    n_counting_qubits: int = 4
    n_simplified_qubits: int = 3
    phi_target: float = 0.5
    theta_min: float = 0.0
    theta_max: float = 2.0 * np.pi
    grid_size_base: int = 64
    grid_size_simplified: int = 50
    max_grover_rotations_base: int = 60
    max_grover_rotations_simplified: int = 50
    gaqa_gate_budget: int = 25
    random_seed: int = 42
