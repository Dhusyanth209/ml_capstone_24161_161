# GPA Implementation Plan
### Grover Policy Agent for Generating Optimal Quantum Sensor Circuits
*Grounded directly in Alomari & Kumar (2024) — Sections III (Methodology) and IV (Experimental Results). This plan does not draw from the review-phase slide decks; every component below is traced to a specific equation, figure, or section of the paper itself.*

---

## 1. Objective

Implement a working prototype that reproduces, in order:

1. The GPA architecture (Fig. 1): QPE → QPI → optimal QSC.
2. The two QSC circuits the paper actually builds (Fig. 2 base/extended, Fig. 7 simplified).
3. The four experimental results the paper reports (Figs. 4–6, 8, 10).

---

## 2. Scope Mapping — Paper Reference → Implementation Component

| Paper Reference | What It Specifies | Component to Build |
|---|---|---|
| Sec. III-A / Fig. 1 | Overall GPA workflow: QPE generates search space → QPI amplifies best policy | Agent orchestrator |
| Sec. III-A / Fig. 2 (left) | Base 2-qubit QSC: Rx, Ry, S gate sequence | `qsc_environment` — base builder |
| Eq. 1 | QFI = 4(⟨ψ\|Z²\|ψ⟩ − ⟨ψ\|Z\|ψ⟩²) / n | `metrics` module |
| Eq. 2 | Squeezing gate S = exp(−iZ²θ/2) | Gate factory inside `qsc_environment` |
| Sec. III-A / Fig. 2 (full) | Extended 6-qubit circuit: qubits 0–3 = QSC gates (Rx, Ry, Rz, S); qubits 4–5 = borrow qubits; CDKM adder (inverse) computes QFI as a subtraction | `qsc_environment` — extended builder |
| Sec. III-B / Fig. 3 | QPE circuit: 4 counting qubits, Hadamards, CU(π/4) × 4, inverse QFT, measurement | `qpe` module |
| Eq. 3–5 | Value-function encoding via phase estimation (φ(x) mapping, bounds ḡ, g) | `qpe` module |
| Sec. III-C, Eq. 6 | Search-space preparation operator A_QPE | `qpi` module |
| Eq. 7 | Oracle O_π — phase-flips policies above the value threshold | `qpi` module |
| Eq. 8 | Grover operator Q_QPI and the rotation-count formula L | `qpi` module |
| Sec. IV-A / Figs. 4–5 | Base-QSC results: v_π^H(s) ≈ 0.99 @ 4096 shots; MAE curve over 1024 shots | Experiment script 1 |
| Sec. IV-A / Fig. 6 | QFI vs. Grover rotations, reaching QFI = 1 at 50 rotations | Experiment script 1 |
| Sec. IV-A / Fig. 7 | Simplified QSC: two 3-qubit episodes, V / V_inv gates, CNOT | `qsc_environment` — simplified builder |
| Sec. IV-A / Fig. 8 | GPA on simplified QSC, reaching QFI = 0.5 at 40 rotations | Experiment script 2 |
| Sec. IV-B / Fig. 9 | GAQA workflow: sequential action selection, no phase estimation | `gaqa_baseline` module |
| Sec. IV-B / Fig. 10 | GPA vs. GAQA — 0.5 vs. 0.45 at 40 rotations | Experiment script 3 |
| Appendix, Table III | Gate/notation definitions | Reference for all gate factories |

---

## 3. Architecture (per Fig. 1)

```
                 ┌─────────────────────┐
  QSC Environment│  (Fig. 2 / Fig. 7)  │
  Rx, Ry, Rz, S  └──────────┬──────────┘
                             │  |ψ_φ⟩
                             ▼
                 ┌─────────────────────┐
                 │   QPE (Fig. 3)      │  4 counting qubits,
                 │  Eq. 3–5            │  H, CU(π/4), QFT⁻¹
                 └──────────┬──────────┘
                             │  v_π^H(s) per policy
                             ▼
                 ┌─────────────────────┐
                 │   QPI (Eq. 6–8)     │  Oracle O_π,
                 │  Grover + AA        │  Q_QPI × L rotations
                 └──────────┬──────────┘
                             │
                             ▼
                    Optimal QSC (max QFI,
                     min gate count)
```

---

## 4. Component-Level Specification

### 4.1 QSC Environment

- **Base QSC (Fig. 2, left; 2 qubits)** — apply Rx(π/2) and Ry(π/2) to both qubits, then the squeezing gate S (Eq. 2). The *gate sequence itself is the policy* GPA searches over — don't hard-code a fixed order, parameterize it so QPE/QPI can evaluate alternatives.
- **Extended QSC (Fig. 2, full; 6 qubits)** — qubits 0–3 carry Rx(π/2), Ry(π/2), Rz(0.05 default), and S; qubits 4–5 are borrow/counting qubits. Use Qiskit's `CDKMRippleCarryAdder` in inverse mode to compute (qubits 2,3 sum) − (qubits 0,1 sum); the borrow qubits (4,5) carry the sign of the result, which represents QFI computed via Rz as the generator.
- **Simplified QSC (Fig. 7; 3 qubits per episode)** — Episode 1 (qubits 0–2): Rx/Ry at 90°. Episode 2 (qubits 3–5): Rx/Ry at 45°. Rz swept over [0, 0.1]. One CNOT + two controlled-V + one controlled-V† per episode implement the simplified subtraction, where:
  - V = (1+i)/2 · [[1, −i], [−i, 1]]
  - V_inv = (1−i)/2 · [[1, i], [i, 1]]

### 4.2 Metrics (Eq. 1)

`QFI = 4(⟨ψ|Z²|ψ⟩ − ⟨ψ|Z|ψ⟩²) / n`, with n = qubit count (2 for the base QSC). Implement two paths:
- Classical/statevector computation — for unit-testing the quantum circuit's output.
- Full quantum computation via the subtraction circuit above — this is the paper's actual claimed contribution ("a fully quantum approach, without relying on classical techniques").

### 4.3 QPE Module (Fig. 3, Eq. 3–5)

- 12-qubit total circuit for base-QSC evaluation: 4 counting qubits + 8 qubits representing the environment |ψ_φ⟩. **Note:** the extended QSC circuit itself is only 6 qubits (Sec. 4.1) — the paper's stated 8-qubit environment register is 2 qubits larger than that. Treat this as an assumption to resolve explicitly (see Section 8) rather than silently padding qubits to make the count match.
- Hadamard on all counting qubits, controlled-unitary (rotation angle π/4) from each counting qubit onto the environment register, inverse QFT on the counting register, measure.
- Encode the value function via the φ(x) mapping in Eq. 4, using bounds ḡ, g on the return.
- Run at 4096 shots → reproduce Fig. 4 (output distribution, v_π^H(s) ≈ 0.99).
- Sweep shot counts up to 1024 → reproduce Fig. 5 (MAE trending toward 0).

### 4.4 QPI Module (Eq. 6–8)

- `A_QPE` (Eq. 6): Hadamard-based superposition combined with the QPE-evaluated value function per policy.
- Oracle `O_π` (Eq. 7): phase-flips a policy |x⟩ when its estimated value exceeds a reference threshold — implement the condition exactly as `1/φ(sin²(πx/2^t)) > r` where t = QPE qubit count.
- Grover operator `Q_QPI` (Eq. 8): `−A_QPE ∘ S₀ ∘ A_QPE† ∘ (Id ⊗ O_π)` — standard Grover diffusion sandwiched around the oracle.
- Rotation count: `L = min(⌊k(r + V(s'))⌋, ⌊π/(4θ) − 1/2⌋)`.
- Run L = 50 on the base QSC → reproduce Fig. 6 (QFI climbing to 1 across 0–50 rotations).

### 4.5 GPA Agent Orchestration

- `run_episode()`: build QSC → QPE evaluates candidate policies → QPI amplifies the best one across increasing rotation counts (track QFI at each step for the Fig. 6 / Fig. 8 curves) → return chosen gate angles, final QFI, gate count.
- Simplified-QSC mode: run both episodes (QSC1, QSC2) **independently/in parallel** (this is the paper's explicit contrast with GAQA, which runs sequentially) and select whichever reaches the higher QFI — the paper reports QSC1 winning with Rz = 0.1, QFI = 0.5.

### 4.6 GAQA Baseline (Fig. 9, Sec. IV-B)

- Sequential loop: select a gate action ∈ {Rx, Ry, Rz, CNOT} → compute QFI via Eq. 1 → apply amplitude amplification biased toward the best action so far → use (probability, QFI) as the reward for the next selection.
- Stop at QFI = 1 or 10 actions/episode, whichever comes first.
- Run exactly 2 episodes, **sequentially**, on the same simplified QSC and rotation budget as GPA, for a fair comparison.

---

## 5. Implementation Phases

| Phase | Objective | Paper Reference | Definition of Done |
|---|---|---|---|
| 0 | Environment setup | — | Repo scaffolded, Qiskit + Aer installed, imports clean |
| 1 | Metrics & classical QFI | Eq. 1 | Unit tests pass on known states (e.g., product state → QFI ≈ 0) |
| 2 | Base 2-qubit QSC + S gate | Eq. 2, Fig. 2 (left) | Circuit builds, runs on statevector sim without error |
| 3 | Extended 6-qubit QFI-subtraction circuit | Fig. 2 (full) | Quantum-computed QFI matches classical Eq. 1 result within simulator tolerance |
| 4 | QPE circuit | Fig. 3, Eq. 3–5 | Reproduces v_π^H(s) ≈ 0.99 (Fig. 4) and a decreasing MAE curve (Fig. 5) |
| 5 | QPI: oracle + Grover operator + rotation formula | Eq. 6–8 | Reproduces QFI reaching ≈ 1 at 50 rotations (Fig. 6) |
| 6 | GPA orchestration (QPE + QPI wired together) | Fig. 1 | End-to-end `run_episode()` returns a valid optimal policy on the base QSC |
| 7 | Simplified QSC (V / V_inv gates, 2 episodes) | Fig. 7, Fig. 8 | GPA on simplified QSC reaches QFI ≈ 0.5 at 40 rotations |
| 8 | GAQA baseline | Fig. 9 | Sequential 2-episode run completes and returns a QFI value |
| 9 | GPA vs. GAQA comparison | Fig. 10 | GPA ≥ GAQA's QFI at the same 40-rotation budget (paper: 0.5 vs. 0.45) |
| 10 | Docs, tests, packaging | — | README complete, `pytest` clean, all plots saved to `results/` |

---

## 6. Validation Plan

Each phase's Definition of Done above *is* the validation criterion — don't move to the next phase until the current one's numeric target is met or the divergence is understood and documented. Final acceptance test: `Phase 9` reproduces the paper's directional result (GPA outperforms GAQA under an identical rotation budget), even if the exact decimal values differ slightly due to simulator/implementation variance.

---

## 7. Tools & Environment

Matches the paper's own setup (Sec. IV): Python + Qiskit, **statevector simulator only** — no real quantum hardware, no GPU requirement. Add NumPy for classical cross-checks, Matplotlib for plots, `pytest` for tests.

---

## 8. Where the Paper Is Ambiguous — Resolve Explicitly, Don't Guess Silently

- **Squeezing gate matrix**: Eq. 2 gives the generator form (`exp(−iZ²θ/2)`), not an explicit 4×4 matrix — derive one from the generator and document the derivation.
- **QPE's 8-qubit environment register vs. the 6-qubit extended QSC**: the paper states 12 total qubits (4 counting + 8 environment) for a QSC that Sec. III-A defines as 6 qubits. Decide and document whether the extra 2 qubits are ancillas for the controlled-unitary wiring, and state that choice plainly.
- **GAQA's exact reward formula**: the paper says it "uses this probability and the generated QFI as a reward" but doesn't give the combining formula — pick one (e.g., a weighted sum) and state it.
- **The `k` hyperparameter** in the rotation-count formula: the paper says only that it ran "several experiments" — report whatever value you land on and why.

---

## 9. Deliverables

- A codebase matching the architecture in Section 3.
- Reproduced plots for Figs. 4, 5, 6, 8, and 10, saved to `results/`.
- A short reconciliation note in the README for any place your numbers diverge from the paper's — this is expected and fine to report honestly.
