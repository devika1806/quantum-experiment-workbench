# Research notebook: when does the repetition code help?

## Question and hypothesis

Under one round of independent, identically distributed X errors on three data qubits, with ideal operations, when does fixed majority decoding reduce error relative to one unprotected qubit at the same per-qubit error probability p?

Define an error before running trials: for inputs 0 and 1, the final decoded Z outcome differs from the input. Predict P(bare error)=p. Majority decoding fails on exactly two or three errors:

```
P(code error) = C(3,2) p²(1-p) + p³ = 3p² - 2p³
P(code error) - p = p(1-p)(2p-1)
```

Thus the code strictly helps for 0<p<0.5, ties at p=0,0.5,1, and hurts for 0.5<p<1. This is an algebraic crossover for a fixed decoder, not an experimentally estimated hardware threshold. An optimized decoder could exploit p>0.5 by changing its decision rule; neither arm uses that optimization here.

## Reproducible protocol

- Rates: 0, .01, .02, .05, .10, .15, .20, .30, .40, .50, .60, .70, .80, .90, 1.
- 50,000 shots per arm and probability; seed 1806; input 0 for the stored bit sweep.
- Separate streams for both arms and each p; no reuse of a bare-qubit error as part of a protected trial.
- Save all points, including failures and boundaries. Do not choose a seed because its plot looks good.
- Plot theory, observed rates and pointwise approximate 95% Wilson intervals. Inspect exact pattern enumeration as a deterministic check.
- Repeat the decoder and enumeration checks with input 1. A symmetric X channel predicts the same error rate.
- Run a separate Z-noise demonstration with plus input and X readout, retaining the original bit-flip recovery.

The two arms have equal trial counts and equal per-data-qubit error probability, but unequal physical resources. Encoding/decoding costs are assumed zero. This is not a fair device-cost or memory-lifetime comparison.

## How to interpret uncertainty

An interval belongs to one arm at one p. Its approximate 95% repeated-sampling coverage does not imply simultaneous coverage of every plotted point, and overlap/non-overlap is not our test of a difference. The improvement region comes from the exact formula. Samples illustrate and test implementation consistency; a finite random curve does not prove an algebraic identity. Near the crossover, small apparent improvements may be sampling variation.

No trial-count stopping rule is used. Future empirical claims about a difference need a predeclared confidence procedure for that difference and a multiple-comparison strategy. Do not label every data point “significant” based on visual separation.

## Phase errors reveal what a bit-only result misses

For plus input, any odd number of independent Z errors acts as a logical phase flip, so X-readout error is 3p(1-p)²+p³. A single Z error is uncorrectable. The bit-code parity checks do not reveal it. For 0 or 1 with Z readout, phase errors would be invisible, which is why this separate preparation/readout is essential.

## Reliable sources and what they actually support

Sources checked on 21 October 2026. These are primary educational documentation and original research; no unverified blog result is used as numerical ground truth.

| Source | Role in this project | Difference from our work |
|---|---|---|
| [IBM Quantum: Repetition codes](https://quantum.cloud.ibm.com/docs/en/tutorials/repetition-codes) | Official practical reference for bit-error correction and its limitations | Uses dynamic circuits and repeated device cycles with syndrome ancillas; our model is a single ideal round, with no hardware execution |
| [IBM Quantum Learning: Error correction II](https://quantum.cloud.ibm.com/learning/en/courses/tools-for-quantum-advantage/error-correction-ii) | Independent reference for the majority-code polynomial and p=1/2 crossover | The wider lesson treats more advanced error correction and resources; we reproduce only the small-code result |
| [Chen et al., Nature 595, 383–387 (2021)](https://doi.org/10.1038/s41586-021-03588-y), [author manuscript](https://arxiv.org/abs/2102.06132) | Original peer-reviewed hardware research: repeated error correction on superconducting qubits | It studies larger codes and repeated rounds; we do not reproduce its hardware experiments or claim comparable suppression |
| [NIST Engineering Statistics Handbook: intervals for proportions](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) | Source for the Wilson interval method used on binomial counts | Statistical interval reference, not a quantum-physics result |

The comparison with Chen et al. uses the abstract and bibliographic record to establish scope; it is not a full paper replication. The actual independent numerical reference run is Qiskit circuit evolution, recorded in `results/quantum-validation.json`.

## Self-check before claiming a result

Can the simulator fail where theory predicts failure? Yes, above p=0.5 with fixed majority decoding. Can it expose a phase error that Z counts conceal? Yes, with plus preparation and X readout. Can it defend an arbitrary quantum-state claim from 0/1 trials alone? No: the separate circuit checks are necessary and still limited to ideal operations. Can this experiment establish quantum advantage or fault tolerance? No.

The distinctive design choice is an **assumption audit**: show the success regime, the decoder's failure regime, and the phase failure in the same reproducible workbench. The scientific formulas are established; the contribution is the implementation and clear evidence trail.
