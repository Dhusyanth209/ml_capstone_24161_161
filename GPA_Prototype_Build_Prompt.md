# GPA Prototype — Implementation Prompt

**How to use this:** paste this entire document as your first message to your AI coding assistant in VS Code (Claude Code, Copilot Chat, Cursor — any of them). It is a complete specification, not a rough idea — the assistant should scaffold the full project structure below and implement it in the build order given in Section 8, asking you a question only where Section 10 explicitly says the paper is ambiguous.

---

## 1. Project Summary

Build a clean, modular Python prototype reproducing the **Grover Policy Agent (GPA)** from:

> Alomari, A., & Kumar, S. A. P. (2024). *"GPA: Grover Policy Agent for Generating Optimal Quantum Sensor Circuits."*

GPA is a fully quantum reinforcement-learning agent that designs Quantum Sensor Circuits (QSCs) by combining:

- **QPE (Quantum Policy Evaluation)** — quantum phase estimation that evaluates the value function of candidate gate sequences and builds a search space of policies.
- **QPI (Quantum Policy Improvement)** — Grover search + amplitude amplification over that search space, converging on the policy (gate sequence) that maximizes **Quantum Fisher Information (QFI)** while minimizing gate count.

The prototype must also implement the paper's own baseline, **GAQA** (Grover search only, no phase estimation), so GPA can be compared directly against it — reproducing the paper's headline result: GPA reaches QFI = 0.5 vs. GAQA's 0.45 on a simplified QSC under an identical 40-Grover-rotation budget, and QFI = 1 (N00N state) on the base 2-qubit QSC after 50 rotations.

---

## 2. Tech Stack

- Python 3.10+
- Qiskit (latest 1.x) + `qiskit-aer` for statevector simulation
- NumPy for classical math (QFI cross-checks, Grover-rotation count formula)
- Matplotlib for all plots
- `pytest` for unit tests
- `argparse` or Typer for the CLI
- No external dataset required — everything is generated via simulation

---

## 3. Non-Negotiable Code-Quality Requirements

- **Modular**: one responsibility per file/class — no god-files, no 500-line scripts.
- **Type-hinted everywhere** (should pass `mypy` cleanly).
- **Docstrings** (Google style) on every public function/class — explain purpose, args, returns, and cite the paper's equation number where relevant.
- **No magic numbers** — every physical constant (rotation angles, shot counts, qubit counts, thresholds) lives in a single `Config` dataclass.
- **Logging** via Python's `logging` module, never bare `print` (except the final CLI summary table).
- **Explicit exception handling** for invalid parameters (qubit-count mismatches, out-of-range angles, negative shot counts) — never fail silently or swallow exceptions.
- **Deterministic runs**: a `--seed` CLI flag that seeds NumPy and the Qiskit simulator, so results are reproducible.
- **Unit tests** for every quantum-independent piece of math (QFI formula, Grover-rotation count formula) and smoke tests for every circuit builder (correct qubit count, correct gate count, builds and runs without error).
- **README** documenting setup, usage, and a table mapping each of the paper's figures to the script/function that reproduces it.
- **`requirements.txt`** pinned to the versions actually tested.

---

## 4. Project Structure

```
gpa-prototype/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   └── gpa/
│       ├── __init__.py
│       ├── config.py
│       ├── qsc_environment.py
│       ├── qpe.py
│       ├── qpi.py
│       ├── gpa_agent.py
│       ├── gaqa_baseline.py
│       ├── metrics.py
│       └── visualization.py
├── scripts/
│   └── run_experiment.py
├── tests/
│   ├── test_metrics.py
│   ├── test_qsc_environment.py
│   ├── test_qpe.py
│   ├── test_qpi.py
│   └── test_gpa_agent.py
└── results/            # generated plots/artifacts — gitignored
```

---

## 5. Module-by-Module Specification

### 5.1 `config.py`
A `GPAConfig` dataclass holding: base/extended qubit counts (2 and 6), rotation angles (π/2 default for Rx/Ry, 0.05 default for Rz), QPE counting-qubit count (4), shot counts (4096 for value-function estimation, sweep up to 1024 for the MAE curve), Grover-rotation budgets (50 for the base QSC, 40 for the simplified QSC), the `k` hyperparameter used in the rotation-count formula, simulator backend name, and random seed.

### 5.2 `qsc_environment.py`
- `build_base_qsc(theta_x, theta_y) -> QuantumCircuit` — 2-qubit circuit: Rx(θx) and Ry(θy) on both qubits, then the Squeezing gate S. Reference: Eq. 1–2, Fig. 2 (left portion). **See Section 10 — the squeezing gate's exact matrix is not fully specified in the paper; derive it per the note there and document the assumption.**
- `build_qfi_subtraction_circuit(...) -> QuantumCircuit` — the 6-qubit extended circuit: qubits 0–3 carry the QSC gates (Rx, Ry, Rz, S); qubits 4–5 are borrow/counting qubits. Compute QFI via Qiskit's `CDKMRippleCarryAdder` (inverse mode) to get the difference between qubits {0,1} and {2,3}. Reference: Fig. 2, Section III-A.
- `compute_qfi_classical(statevector, generator="Z") -> float` — classical cross-check implementing Eq. 1 directly: `QFI = 4(⟨ψ|Z²|ψ⟩ − ⟨ψ|Z|ψ⟩²) / n`. Used in unit tests to validate the quantum subtraction circuit's output against ground truth.
- `build_simplified_qsc(theta_rz, episode: int) -> QuantumCircuit` — the 3-qubit-per-episode simplified circuit (Fig. 7): Rx/Ry at 90° for episode 1, 45° for episode 2, plus CNOT + controlled-V / controlled-V† gates implementing the simplified subtraction (V and V_inv matrices given explicitly in the paper — implement exactly).

### 5.3 `qpe.py`
`class QPE` — builds the 12-qubit phase-estimation circuit: 4 counting qubits, Hadamards, controlled-unitary gates (rotation angle π/4) wrapping the QSC environment, inverse QFT, measurement.
- `estimate_value_function(policy_circuit, shots) -> tuple[float, dict]` — returns the estimated `v_π^H(s)` and the raw measurement-outcome distribution (reproduces Fig. 4).
- `mean_absolute_error_sweep(shots_list) -> list[float]` — reproduces Fig. 5's MAE-vs-shots curve.

### 5.4 `qpi.py`
`class QPI` — implements the Grover oracle `O_π` (Eq. 7, flips the phase of policies whose value exceeds a threshold) and the Grover diffusion/amplitude-amplification operator (Eq. 6, 8).
- `compute_grover_rotations(reward, value_estimate, k, theta) -> int` — implements `L = min(⌊k(r + V(s'))⌋, ⌊π/(4θ) − 1/2⌋)` exactly as described around Eq. 8.
- `run(search_space_circuit, rotations) -> Policy` — amplifies and returns the best policy found.

### 5.5 `gpa_agent.py`
`class GPAAgent` — orchestrates one GPA episode: build QSC → QPE evaluates the value function → QPI amplifies the best policy → return the chosen circuit + its QFI + gate count. `run_episode()` returns a structured result object (`qfi`, `gate_count`, `chosen_angles`, `rotations_used`) for logging and plotting.

### 5.6 `gaqa_baseline.py`
`class GAQAAgent` — the no-QPE baseline: sequential action selection (gate ∈ {Rx, Ry, Rz, CNOT}) with amplitude amplification per action, up to 10 actions/episode or QFI = 1, whichever comes first (the paper's stopping rule). Must run on the same simplified QSC and rotation budget as GPA for a fair, apples-to-apples comparison.

### 5.7 `metrics.py`
Pure functions: QFI (Eq. 1), the value-function target formula (Eq. 3), and any shared numeric utilities. This module is where the whole prototype's correctness lives — target 100% unit-test coverage here.

### 5.8 `visualization.py`
One function per paper figure, each **returning** a Matplotlib `Figure` (not just showing/saving it directly, so tests can inspect the object):
- `plot_qpe_output_distribution(counts) -> Figure` (Fig. 4)
- `plot_mae_vs_shots(shots_list, mae_list) -> Figure` (Fig. 5)
- `plot_qfi_vs_rotations(rotations, qfi_values, label) -> Figure` (Fig. 6 / Fig. 8)
- `plot_gpa_vs_gaqa(rotations, gpa_qfi, gaqa_qfi) -> Figure` (Fig. 10)

### 5.9 `scripts/run_experiment.py`
CLI entry point with subcommands:
- `run-base-qsc` — reproduces Fig. 4–6
- `run-simplified-qsc` — reproduces Fig. 7–8
- `run-comparison` — GPA vs. GAQA, reproduces Fig. 10

Each subcommand prints a clear summary table to stdout and saves its plot(s) to `results/`.

---

## 6. Validation Targets

The prototype should land close to these (simulator noise aside — exact reproduction isn't the bar, a defensible result is):

- QPE value-function estimate on the base QSC ≈ **0.99** at 4096 shots (Fig. 4)
- MAE trending toward **0** as shots increase to 1024 (Fig. 5)
- QPI with **50** Grover rotations on the base 2-qubit QSC reaches **QFI ≈ 1** (N00N state) (Fig. 6)
- On the simplified QSC at **40** Grover rotations: GPA reaches **QFI ≈ 0.5**, GAQA reaches **QFI ≈ 0.45** (Fig. 10)

If a run diverges meaningfully from these, that's fine — report and explain the gap honestly in the README rather than silently tuning parameters until numbers match.

---

## 7. Explicit Non-Goals

- No real quantum-hardware execution — Aer statevector simulator only.
- No hyperparameter search over `k` — use the paper's approach (a few manually tried values; report what worked and why).
- No GPU acceleration required.
- No packaging/publishing to PyPI.

---

## 8. Suggested Build Order

Work incrementally, not all-at-once — verify each stage before moving on:

1. `config.py` + `metrics.py` + their tests (get the QFI math right first — everything depends on it).
2. `qsc_environment.py` (base QSC) + tests.
3. `qpe.py` + tests → reproduce Fig. 4 and Fig. 5.
4. `qpi.py` + tests → reproduce Fig. 6.
5. `gpa_agent.py`, wiring QPE + QPI together on the base QSC.
6. Extend `qsc_environment.py` with the simplified/6-qubit circuits.
7. `gaqa_baseline.py` + tests.
8. `scripts/run_experiment.py` tying everything together → reproduce Fig. 8 and Fig. 10.
9. README + final polish pass (docstrings, type hints, lint clean, remove any leftover debug prints).

---

## 9. Deliverable Checklist

- [ ] All files above exist and import cleanly.
- [ ] `pytest` passes with no warnings.
- [ ] `python scripts/run_experiment.py run-comparison --seed 42` runs end-to-end and saves a plot to `results/`.
- [ ] README documents setup (`pip install -r requirements.txt`), how to run each experiment, and a table mapping each paper figure to the script/function that reproduces it.
- [ ] No print-debugging left in committed code; `logging` used throughout.
- [ ] `mypy` and a linter (e.g. `ruff`) run clean.

---

## 10. Where the Paper Is Underspecified — Document, Don't Guess Silently

Be upfront about these in the README's "Implementation Notes" section rather than quietly picking an interpretation:

- **Squeezing gate matrix**: the paper defines it conceptually (`S = exp(−iZ²θ/2)`, entangles two qubits, creates squeezed states) but doesn't give an explicit 4×4 matrix. Derive it from the exponential-of-generator definition using a collective `Z⊗Z` generator, validate empirically that the resulting state is entangled (non-zero concurrence or a non-separable statevector), and state this derivation explicitly in the README.
- **Controlled-unitary wiring inside QPE**: the paper specifies the rotation angle (π/4) but not the exact control-qubit-to-environment wiring for all 4 counting qubits — implement the standard textbook QPE wiring (counting qubit *i* controls `U^(2^i)`) and note that this is the standard convention being assumed.
- **GAQA's per-action reward shaping**: the paper describes the overall loop (select gate → compute QFI via Eq. 1 → amplify → repeat) but not the exact reward formula between actions — use QFI-so-far as the reward signal, and say so explicitly.

Flag anything else you find similarly underspecified the same way — a clean prototype makes its assumptions legible, it doesn't hide them.
