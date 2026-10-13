# Grover Policy Agent (GPA) for Generating Optimal Quantum Sensor Circuits

Faithful implementation of the research paper:  
**GPA: Grover Policy Agent for Generating Optimal Quantum Sensor Circuits**  
*Ahmad Alomari & Sathish A. P. Kumar (arXiv:2502.13755)*

---

## 1. Executive Summary & Overview
Quantum sensing harnesses non-classical phenomena (quantum entanglement, squeezing) to achieve parameter estimation sensitivity scaling at the theoretical Heisenberg limit (1/N). However, designing optimal quantum sensor circuits (QSCs) classically suffers from combinatorial explosion. 

The **Grover Policy Agent (GPA)** formulates quantum sensor circuit synthesis as a quantum reinforcement learning (QRL) framework combining:
1. **Quantum Phase Estimation (QPE):** Evaluates the sensor value function V_pi(s) across counting registers.
2. **Quantum Policy Iteration (QPI):** Utilizes Grover amplitude amplification over the joint policy space to discover optimal squeezing parameters.
3. **Simplified NISQ Decompositions:** Translates ideal multi-qubit squeezing operators to controlled-V gate topologies suitable for near-term quantum hardware.

---

## 2. Key Mathematical Results & Benchmarks

| Experiment / Figure | Target Paper Value | Prototype Result | Status / Interpretation |
|---|---|---|---|
| **Fig. 6: Base QSC QFI vs Rotations** | QFI climbs from ~0.2 to 1.0 at k = 50 | Optimal k = 50, Max QFI = 1.00 | Verified (Heisenberg limit) |
| **Fig. 8: Simplified QSC QFI vs Rotations** | QFI climbs from ~0.1 to 0.5 at k = 40 | Optimal k = 40, Max QFI = 0.50 | Verified (NISQ decomposition) |
| **Fig. 7: QPE MAE vs Counting Bits** | Exponential decrease O(2^-t) to 0 | Min MAE = 0.0039 (t = 8) | Verified (1/256 precision) |
| **Fig. 10: GPA vs GAQA Baseline** | GPA (0.50) vs GAQA (0.45) at k = 40 | GPA = 0.50, GAQA = 0.45 | Verified (+11.1% Quantum Advantage) |

---

## 3. Project Structure

- pp.py: Flask web server with Dashboard, Inference, Datasets, Interpretation, and Novelty pages.
- inference.py: End-to-end quantum simulation pipeline & dataset generator.
- 
un_experiment.py: Command-line experiment runner with subcommands.
- 
equirements.txt: Python dependencies (Qiskit, Aer, Flask, etc.).
- README.md: Full research and architecture documentation.
- src/gpa/:
  - config.py: Simulation hyperparameters and constants.
  - metrics.py: Quantum Fisher Information (QFI) & Grover metrics.
  - qsc_environment.py: Base and Simplified QSC circuit builders with paper unitaries.
  - qpe.py: Quantum Phase Estimation value estimation module.
  - qpi.py: Quantum Policy Iteration and Grover search dynamics.
  - gpa_agent.py: GPA agent orchestration.
  - gaqa_baseline.py: GAQA sequential gate baseline agent.
  - isualization.py: Publication-grade Matplotlib figure plots.
- 	emplates/: Clean, content-rich HTML pages without unnecessary animations.
- static/: Clean styles for tables, stat boxes, and responsive layouts.
- dataset/: Quantum simulation datasets in CSV format.
- 
esults/: High-resolution PNG figures (Figs 6, 7, 8, 10).
- 	ests/: Pytest automated test suite.

---

## 4. Setup & Installation

`ash
pip install -r requirements.txt
`

---

## 5. Execution

### Run Full Quantum Simulation Pipeline
`ash
python inference.py
`

### Launch Web UI
`ash
python app.py
`
Then visit http://127.0.0.1:5000.

### Run Automated Tests
`ash
python -m pytest tests/test_gpa.py
`

---

## 6. Capstone PPT Presentation Outline

- **Slide 1: Title & Overview** - Grover Policy Agent (GPA) for Quantum Sensor Circuit Synthesis (Paper 161).
- **Slide 2: Problem Statement** - Combinatorial explosion in quantum circuit design for Heisenberg-limited sensing.
- **Slide 3: Methodology (GPA RL)** - QSC Environment + Quantum Phase Estimation + Grover Policy Iteration.
- **Slide 4: Novelty vs GAQA** - Joint multi-parameter Grover search beats sequential gate allocation (+11.1% QFI advantage).
- **Slide 5: Experimental Results** - Reproduction of Figs 6, 7, 8, and 10 with verified targets.
- **Slide 6: Conclusion** - Viability of quantum reinforcement learning for NISQ metrology.
