# Verification and recorded findings

Verified locally on 21 October 2026, Windows, Python 3.14.4. UI verification used Streamlit 1.65.0 and Altair 6.3.0 from the existing explorer environment; the project itself does not import that explorer. Qiskit 2.5.2 performed the independent circuit checks. The included GitHub Actions workflow has not yet been run remotely for this project.

## Completed checks

- **13 automated tests passed**, including a Streamlit AppTest that runs both noise modes and confirms stale-result warnings. The 12 core tests need no external packages. Without Streamlit, the UI test is explicitly skipped.
- Exhaustive decoder tests cover all 8 patterns for both bit inputs and all 8 phase patterns.
- Exact pattern sums match the formulas at 101 probabilities for each of 3 noise/input combinations.
- Deterministic cases p=0 and p=1, the p=0.5 theoretical tie, output conservation, known Wilson endpoints, reproducibility, independent arm seeds, reordered sweeps, invalid input, output limits, JSON/CSV and CLI overwrite protection are checked.
- Fixed-seed sampling regression checks use a deliberately generous six-standard-deviation tolerance. They are software checks, not a statistical proof of the research hypothesis.
- **314 independent Qiskit checks passed:** 112 state/pattern checks (7 probe states × 8 patterns × 2 separate noise types) plus 202 channel probability checks (101 probabilities × 2 channels).
- Largest absolute numerical discrepancy: **4.440892098500626e-16**, below the declared tolerance **1e-10**. See [the machine-readable report](../results/quantum-validation.json).
- Both scientific figures were rendered from the saved JSON records and visually inspected.
- The local browser demo was run and inspected at a narrow viewport; the reduction label was shortened to avoid truncation. A screenshot is saved as `docs/preview.png`.
- The portability review added a regression check for exports to paths with spaces and non-ASCII characters under an ASCII-only console. Unsupported display characters are escaped without changing the actual file name. Source line endings are normalized by `.gitattributes` to preserve engine fingerprints across clones.

The Qiskit checks use two CNOTs to encode, inject each X or Z error pattern, and use inverse CNOTs plus a Toffoli for ideal coherent recovery. The two syndrome qubits are traced out. State fidelity compares the recovered qubit to the predicted original or logically flipped state. This validates the ideal recovery/channel model; it is not a physical syndrome-measurement experiment.

## Recorded evidence

Each stored sweep has 15 probabilities, 50,000 shots per arm per point and seed 1806: 1.5 million trials per sweep, 3 million across the bit and phase studies.

| Model and p | Unprotected: observed (theory) | Repetition code: observed (theory) |
|---|---|---|
| Bit, p=.10 | 9.872% (10%) | 2.870% (2.8%) |
| Bit, p=.50 | 50.526% (50%) | 49.964% (50%) |
| Bit, p=.80 | 79.862% (80%) | 89.642% (89.6%) |
| Phase, p=.10 | 10.278% (10%) | 24.420% (24.4%) |

At bit p=.10 the code's pointwise 95% Wilson interval is approximately 2.727%–3.020%. At phase p=.10 it is approximately 24.045%–24.799%.

Not every 95% interval contains theory. For example, the unprotected bit run at p=.50 gives 50.088%–50.964%, missing the true 50%. We retained it. This is expected to occur sometimes with many finite samples; it is not evidence of a real improvement at the theoretical tie. Do not cherry-pick a nicer random seed.

## What remains unverified or excluded

Linux and macOS runtime behavior has not been locally exercised; the CI matrix is a prepared workflow, not a completed remote result. No hardware run, gate or measurement noise, correlated errors, mixed X/Z noise, repeated correction rounds, resource-normalized advantage, formal difference-confidence test or general quantum error correction is included. Saved charts and interval checks do not establish any of those claims.
