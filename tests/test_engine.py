import csv
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from workbench.engine import Settings, run_sweep, theory, pattern_outcome, exact_enumeration, wilson
from workbench.records import record, json_text, csv_text


class EngineTests(unittest.TestCase):
    def test_all_bit_patterns_both_inputs(self):
        for initial in ("0", "1"):
            for mask in range(8):
                actual = pattern_outcome(mask, initial)
                self.assertEqual(actual != int(initial), mask.bit_count() >= 2)

    def test_phase_errors_are_not_corrected(self):
        for mask in range(8):
            self.assertEqual(pattern_outcome(mask, "+", "phase"), mask.bit_count() % 2)
        for mask in (1, 2, 4):
            self.assertEqual(pattern_outcome(mask, "+", "phase"), 1)

    def test_exact_enumeration_matches_theory(self):
        for noise, initial in (("bit", "0"), ("bit", "1"), ("phase", "+")):
            for i in range(101):
                p = i/100
                self.assertAlmostEqual(exact_enumeration(p, Settings(noise, initial)), theory(p, noise), places=14)

    def test_known_values_and_crossover(self):
        self.assertAlmostEqual(theory(.1), .028)
        self.assertAlmostEqual(theory(.1, "phase"), .244)
        for p in (0, .5, 1):
            self.assertEqual(theory(p), p)
        for i in range(1, 50):
            self.assertLess(theory(i/100), i/100)
            self.assertGreater(theory(.5+i/100), .5+i/100)

    def test_deterministic_boundaries_and_output_conservation(self):
        for noise, initial in (("bit", "0"), ("bit", "1"), ("phase", "+")):
            result = run_sweep([0, 1], Settings(noise, initial, 101))
            for p in result["points"]:
                self.assertEqual(sum(p["physical_error_patterns_q2q1q0"].values()), 101)
                for r in p["rows"]:
                    self.assertEqual(r["errors"], 101*p["p"])
                    self.assertEqual(r["outcome_0"]+r["outcome_1"], 101)

    def test_reproducibility_and_rate_order_independence(self):
        s = Settings(shots=1000)
        a = run_sweep([.1, .2], s)
        self.assertEqual(a, run_sweep([.1, .2], s))
        self.assertEqual(a["points"], list(reversed(run_sweep([.2, .1], s)["points"])))
        self.assertNotEqual(a["points"], run_sweep([.1, .2], Settings(shots=1000, seed=1807))["points"])
        self.assertNotEqual(a["points"][0]["rows"][0]["stream_seed"], a["points"][0]["rows"][1]["stream_seed"])

    def test_sample_rates_plausible(self):
        # Fixed seeds and a generous 6-sigma bound: a regression check, not a research conclusion.
        for noise, initial in (("bit", "0"), ("phase", "+")):
            for point in run_sweep([.1, .5, .8], Settings(noise, initial, 40000))["points"]:
                for r in point["rows"]:
                    tolerance = 6*math.sqrt(r["expected"]*(1-r["expected"])/r["shots"]) + 1/r["shots"]
                    self.assertLess(abs(r["rate"]-r["expected"]), tolerance)

    def test_wilson_boundaries_and_known_value(self):
        lo, hi = wilson(50, 100)
        self.assertAlmostEqual(lo, .4038315304, places=9)
        self.assertAlmostEqual(hi, .5961684696, places=9)
        self.assertEqual(wilson(0, 100)[0], 0)
        self.assertEqual(wilson(100, 100)[1], 1)
        self.assertGreater(wilson(0, 100)[1], 0)

    def test_invalid_settings_and_rates(self):
        for kw in ({"shots": 0}, {"shots": True}, {"shots": 1.2}, {"seed": -1}, {"seed": 2**32}, {"noise": "mixed"}, {"noise": "phase", "initial": "0"}):
            with self.assertRaises(ValueError): Settings(**kw)
        for rates in ([], [.1, .1], [-1], [1.1], [float("nan")], [float("inf")], [True]):
            with self.assertRaises(ValueError): run_sweep(rates)
        with self.assertRaises(ValueError): run_sweep([0, .5, 1], Settings(shots=1_000_000))
        with self.assertRaises(ValueError): wilson(3, 2)

    def test_exports_round_trip(self):
        result = record(run_sweep([.1], Settings(shots=100)))
        self.assertEqual(json.loads(json_text(result)), result)
        rows = list(csv.DictReader(io.StringIO(csv_text(result))))
        self.assertEqual(len(rows), 2)
        self.assertEqual(int(rows[1]["errors"]), result["points"][0]["rows"][1]["errors"])
        self.assertEqual(rows[0]["engine_sha256"], result["engine_sha256"])

    def test_cli_creates_records_and_protects_existing_output(self):
        root = Path(__file__).resolve().parents[1]
        temp_root = root / "local-runs"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            args = [sys.executable, "-m", "workbench", "--rates", "0,0.1,1", "--shots", "100", "--out", folder]
            first = subprocess.run(args, cwd=root, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((Path(folder)/"experiment.csv").exists())
            second = subprocess.run(args, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Output exists", second.stderr)
            bad = subprocess.run([sys.executable, "-m", "workbench", "--rates", "nan"], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertNotIn("Traceback", bad.stderr)

    def test_unicode_export_path_with_ascii_console(self):
        root = Path(__file__).resolve().parents[1]
        temp_root = root / "local-runs"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            destination = Path(folder) / "trial space \u03b4"
            run = subprocess.run([sys.executable, "-m", "workbench", "--rates", "0.1", "--shots", "20", "--out", str(destination)],
                                 cwd=root, capture_output=True, text=True, encoding="ascii",
                                 env={**os.environ, "PYTHONIOENCODING": "ascii"})
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((destination / "experiment.json").read_text(encoding="utf-8"))
            self.assertEqual(data["settings"]["shots"], 20)


if __name__ == "__main__":
    unittest.main()
