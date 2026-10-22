"""Exact theory and physical-error Monte Carlo; standard library only.

Bit mode: computational inputs, Z readout, majority decoding.
Phase mode: plus input, X readout after ideal bit-code recovery/decoding.
The latter fails for odd numbers of Z errors. No general noise is modeled.
"""
from dataclasses import asdict, dataclass
import hashlib
import math
import random

MAX_SHOTS = 1_000_000
MAX_TOTAL_SHOTS = 2_000_000  # per arm over the entire sweep


def probability(p):
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("Error probability must be a finite number from 0 to 1.")
    return float(p)


@dataclass(frozen=True)
class Settings:
    noise: str = "bit"
    initial: str = "0"
    shots: int = 20_000
    seed: int = 1806

    def __post_init__(self):
        if self.noise not in ("bit", "phase"):
            raise ValueError("Noise must be 'bit' or 'phase'.")
        if self.initial not in (("0", "1") if self.noise == "bit" else ("+",)):
            raise ValueError("Bit noise uses input 0 or 1; the phase demonstration uses +.")
        if type(self.shots) is not int or not 1 <= self.shots <= MAX_SHOTS:
            raise ValueError(f"Shots must be an integer from 1 to {MAX_SHOTS:,}.")
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError("Seed must be an integer from 0 to 4294967295.")


def theory(p, noise="bit"):
    p = probability(p)
    if noise == "bit":
        return 3 * p**2 - 2 * p**3
    if noise == "phase":
        return 3 * p * (1 - p)**2 + p**3
    raise ValueError("Unknown noise model.")


def pattern_outcome(mask, initial="0", noise="bit"):
    """Return final measured bit. Mask bit i marks an error on data qubit i."""
    if type(mask) is not int or not 0 <= mask < 8:
        raise ValueError("Error mask must be an integer from 0 to 7.")
    if noise == "bit" and initial in ("0", "1"):
        received = [int(initial) ^ ((mask >> q) & 1) for q in range(3)]
        return int(sum(received) >= 2)
    if noise == "phase" and initial == "+":
        return mask.bit_count() % 2  # X outcome 1 is minus, an error for input plus.
    raise ValueError("Unsupported noise/input combination.")


def exact_enumeration(p, settings):
    """Sum eight physical error patterns independently of the closed formula."""
    p = probability(p)
    target = int(settings.initial) if settings.noise == "bit" else 0
    return sum(p**m.bit_count() * (1-p)**(3-m.bit_count())
               for m in range(8)
               if pattern_outcome(m, settings.initial, settings.noise) != target)


def wilson(errors, shots):
    """Approximate two-sided 95% Wilson interval; not a joint sweep interval."""
    if type(shots) is not int or shots < 1 or type(errors) is not int or not 0 <= errors <= shots:
        raise ValueError("Counts must satisfy 0 <= errors <= shots and shots > 0.")
    z = 1.959963984540054
    rate = errors / shots
    denom = 1 + z*z/shots
    center = (rate + z*z/(2*shots)) / denom
    half = z * math.sqrt(rate*(1-rate)/shots + z*z/(4*shots*shots)) / denom
    return (0.0 if errors == 0 else max(0.0, center-half),
            1.0 if errors == shots else min(1.0, center+half))


def stream_seed(seed, p, noise, arm):
    # Stable across sweep ordering; domain-separated streams, no global RNG state.
    value = f"qew-v1|{seed}|{float(p).hex()}|{noise}|{arm}"
    return int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big")


def run_point(p, settings):
    p = probability(p)
    if p == 0:
        p = 0.0  # canonicalize negative zero
    bare_rng = random.Random(stream_seed(settings.seed, p, settings.noise, "bare"))
    code_rng = random.Random(stream_seed(settings.seed, p, settings.noise, "code"))
    bare_errors = sum(bare_rng.random() < p for _ in range(settings.shots))
    histogram = [0] * 8
    for _ in range(settings.shots):
        mask = sum((code_rng.random() < p) << q for q in range(3))
        histogram[mask] += 1
    target = int(settings.initial) if settings.noise == "bit" else 0
    code_errors = sum(count for m, count in enumerate(histogram)
                      if pattern_outcome(m, settings.initial, settings.noise) != target)
    rows = []
    for arm, errors, expected in (("Unprotected", bare_errors, p),
                                  ("Repetition code", code_errors, theory(p, settings.noise))):
        low, high = wilson(errors, settings.shots)
        rows.append({"p": p, "arm": arm, "errors": errors, "shots": settings.shots,
                     "rate": errors/settings.shots, "expected": expected,
                     "ci_low": low, "ci_high": high,
                     "outcome_0": settings.shots-errors if target == 0 else errors,
                     "outcome_1": errors if target == 0 else settings.shots-errors,
                     "stream_seed": str(stream_seed(settings.seed, p, settings.noise,
                                                    "bare" if arm == "Unprotected" else "code"))})
    return {"p": p, "rows": rows,
            "physical_error_patterns_q2q1q0": {f"{m:03b}": n for m, n in enumerate(histogram)}}


def run_sweep(rates, settings=Settings()):
    rates = [probability(p) for p in rates]
    if not rates or len(rates) > 101 or len(set(rates)) != len(rates):
        raise ValueError("Choose 1 to 101 distinct error probabilities.")
    if len(rates) * settings.shots > MAX_TOTAL_SHOTS:
        raise ValueError(f"Use at most {MAX_TOTAL_SHOTS:,} total shots per arm across the sweep.")
    return {"settings": asdict(settings), "rates": rates,
            "points": [run_point(p, settings) for p in rates]}
