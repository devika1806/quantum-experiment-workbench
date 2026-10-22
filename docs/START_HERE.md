# Start here: a small laboratory for mistakes

## 1. Learn the six words

- **Physical qubit:** one actual information carrier in the model.
- **Logical qubit:** the information we want to preserve, represented across several physical qubits.
- **Bit flip (X):** swaps 0 and 1.
- **Phase flip (Z):** changes a relative sign; plus becomes minus.
- **Decoder:** a rule that tries to recover the intended information.
- **Shot:** one fresh preparation, error trial and readout.

## 2. Start with ordinary bits

Store 0 as 000. A single error might make 010. Two zeros still win the vote, so recover 0. But two errors can make 110; now a majority vote gives the wrong answer. There are three ways to choose two erroneous positions and one way to flip all three.

Try every pattern by hand. The pattern marks which positions flip, not their measured value:

| Error pattern | Number of flips | Majority decoder succeeds? |
|---|---:|---|
| 000 | 0 | Yes |
| 001, 010, 100 | 1 | Yes |
| 011, 101, 110 | 2 | No |
| 111 | 3 | No |

The same rule works for input 1, encoded as 111.

## 3. Connect to a quantum code carefully

An unknown state a|0> + b|1> is encoded as a|000> + b|111> with two CNOT gates. This creates correlations and can create entanglement. It does **not** produce three separate copies of the unknown state.

For arbitrary quantum information, measuring all three data qubits would destroy the superposition. Quantum recovery instead learns error parity (a syndrome) without learning whether the logical state is 0 or 1. Our independent circuit check uses an ideal coherent equivalent: undo the two encoding CNOTs, then a Toffoli controlled by the two syndrome qubits corrects the first qubit. The syndrome qubits are traced out.

The main 0/1 experiment needs only the much simpler pattern simulation. Both representations agree for the restricted experiment, and we check that agreement.

## 4. Follow five small investigations

1. **Controls:** p=0 must produce zero errors. At p=1, all bits flip and both arms fail. At p=0.5, both predicted rates are 50% (samples need not be exactly equal).
2. **A useful regime:** p=0.1 predicts 10% unprotected and 2.8% protected. Say what counts as an error before looking at the results.
3. **A failure regime:** p=0.8 predicts 80% versus 89.6%. The fixed majority decoder is wrong more often. A different decoder could exploit known high p; we have deliberately held this rule fixed.
4. **Uncertainty:** compare 1,000 with 20,000 shots. Ranges usually narrow. More shots do not guarantee a closer estimate on every run. A displayed 95% interval is a method with approximate repeated-experiment coverage, not a guarantee that this range contains the answer.
5. **A different kind of error:** switch to phase mode at p=0.1. Plus input and X readout make phase damage visible. Predict why one phase error cannot be repaired by this code.

## 5. Explain the phase failure

The encoded plus state is (|000> + |111>)/sqrt(2). A Z error on any one qubit gives (|000> - |111>)/sqrt(2). The bit-error parity checks have not changed, so they cannot signal this error. Decoding gives minus, detected as X outcome 1. Two Z errors cancel their signs; three flip the sign again.

For independent phase errors, failure means an odd number of errors: three ways to have exactly one, plus one way to have three. That gives 3p(1-p)^2 + p^3. This is a deliberate failure demonstration, not a newly implemented phase-correcting code.

## 6. Write a tiny lab note

Copy this into your downloaded JSON reflection or a notebook:

> My question was ___. I predicted ___ because ___. I used noise ___, input ___, p ___, shots ___, seed ___. The expected rates were ___. The observed rates and intervals were ___. I changed only ___. This result supports ___ under the assumptions ___. It does not show ___.

Self-check: does zero observed errors prove an error probability of zero? No: with finite samples, the Wilson upper endpoint is still positive. Does a low Z error rate prove a qubit's phase is safe? No: use a phase-sensitive preparation and readout.
