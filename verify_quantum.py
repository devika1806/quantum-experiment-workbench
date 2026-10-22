"""Independent Qiskit circuit check: pure-state encoding, error, coherent recovery.

Not a hardware or dynamic syndrome-circuit run. Qubits 1 and 2 retain the
syndrome during ideal unitary recovery and are traced out after decoding.
"""
import json
from pathlib import Path
import math
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity
from workbench.engine import theory


def check():
    s = 1/math.sqrt(2)
    states = {"0": [1, 0], "1": [0, 1], "+": [s, s], "-": [s, -s],
              "+i": [s, 1j*s], "-i": [s, -1j*s], "tilted": [math.sqrt(.3), math.sqrt(.7)*complex(math.cos(.37), math.sin(.37))]}
    errors, comparisons = [], 0
    for noise in ("bit", "phase"):
        for name, initial in states.items():
            for mask in range(8):
                qc = QuantumCircuit(3)
                qc.initialize(initial, [0])
                qc.cx(0, 1); qc.cx(0, 2)
                for q in range(3):
                    if (mask >> q) & 1:
                        getattr(qc, "x" if noise == "bit" else "z")(q)
                qc.cx(0, 2); qc.cx(0, 1); qc.ccx(1, 2, 0)
                reduced = partial_trace(Statevector.from_instruction(qc), [1, 2])
                failed = mask.bit_count() >= 2 if noise == "bit" else mask.bit_count() % 2
                expected = list(initial)
                if failed:
                    expected = list(reversed(initial)) if noise == "bit" else [initial[0], -initial[1]]
                errors.append(abs(1-state_fidelity(reduced, Statevector(expected))))
                comparisons += 1
    # Directly sum circuit-derived measurement failure over the physical channel.
    for noise, initial, basis in (("bit", [1, 0], "Z"), ("phase", [s, s], "X")):
        conditional = []
        for mask in range(8):
            qc = QuantumCircuit(3)
            qc.initialize(initial, [0]); qc.cx(0, 1); qc.cx(0, 2)
            for q in range(3):
                if mask >> q & 1: getattr(qc, "x" if noise == "bit" else "z")(q)
            qc.cx(0, 2); qc.cx(0, 1); qc.ccx(1, 2, 0)
            if basis == "X": qc.h(0)
            conditional.append(float(Statevector.from_instruction(qc).probabilities([0])[1]))
        for i in range(101):
            p = i/100
            actual = sum(v*p**mask.bit_count()*(1-p)**(3-mask.bit_count()) for mask, v in enumerate(conditional))
            errors.append(abs(actual-theory(p, noise)))
            comparisons += 1
    result = {"qiskit_version": qiskit.__version__, "state_pattern_checks": 112,
              "channel_probability_checks": 202, "total_checks": comparisons,
              "max_absolute_error": max(errors), "tolerance": 1e-10,
              "passed": max(errors) < 1e-10,
              "scope": "Ideal unitary encoding/recovery; 7 probe states; all 8 patterns; separate X and Z noise; no hardware"}
    if not result["passed"]: raise AssertionError(result)
    return result


if __name__ == "__main__":
    result = check()
    path = Path("results/quantum-validation.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
