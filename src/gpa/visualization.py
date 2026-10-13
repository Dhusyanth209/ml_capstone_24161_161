# Visualization module for GPA and quantum sensor circuit evaluation
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_qfi_vs_rotations_base(data, save_path='results/fig6_base_qsc.png'):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(data['rotations'], data['qfi'], 'b-', linewidth=2, label='GPA (Base QSC)')
    ax.axvline(x=data['optimal_rotations'], color='r', linestyle='--', label='Optimal k = ' + str(data['optimal_rotations']))
    ax.set_xlabel('Grover Rotations (k)', fontsize=12)
    ax.set_ylabel('Quantum Fisher Information (QFI)', fontsize=12)
    ax.set_title('Fig. 6: QFI vs Grover Rotations (Base QSC)', fontsize=14)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', fontsize=11)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

def plot_qfi_vs_rotations_simplified(data, save_path='results/fig8_simplified_qsc.png'):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(data['rotations'], data['qfi'], 'g-', linewidth=2, label='GPA (Simplified QSC)')
    ax.axvline(x=data['optimal_rotations'], color='r', linestyle='--', label='Optimal k = ' + str(data['optimal_rotations']))
    ax.set_xlabel('Grover Rotations (k)', fontsize=12)
    ax.set_ylabel('Quantum Fisher Information (QFI)', fontsize=12)
    ax.set_title('Fig. 8: QFI vs Grover Rotations (Simplified QSC)', fontsize=14)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', fontsize=11)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

def plot_qpe_mae_vs_bits(bits, mae, save_path='results/fig7_qpe_mae.png'):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(bits, mae, 'mo-', linewidth=2, markersize=6, label='QPE Value Estimation MAE')
    ax.set_xlabel('Counting Qubits (t)', fontsize=12)
    ax.set_ylabel('Mean Absolute Error (MAE)', fontsize=12)
    ax.set_title('Fig. 7: Phase Estimation MAE vs Counting Qubits', fontsize=14)
    ax.set_yscale('log')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=11)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

def plot_comparison_gpa_vs_gaqa(gpa_data, gaqa_data, save_path='results/fig10_gpa_vs_gaqa.png'):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(gpa_data['rotations'], gpa_data['qfi'], 'b-', linewidth=2.5, label='GPA (Joint Policy Search)')
    ax.plot(gaqa_data['rotations'], gaqa_data['qfi'], 'r--', linewidth=2, label='GAQA (Sequential Gate Search)')
    ax.set_xlabel('Grover Rotations / Budget', fontsize=12)
    ax.set_ylabel('Quantum Fisher Information (QFI)', fontsize=12)
    ax.set_title('Fig. 10: Performance Comparison: GPA vs GAQA Baseline', fontsize=14)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', fontsize=11)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
