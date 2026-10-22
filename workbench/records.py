"""Versioned, portable experiment records; deterministic content, no timestamps."""
import csv
import hashlib
import io
import json
import platform
from pathlib import Path
from . import __version__


def record(sweep):
    source = Path(__file__).parent / "engine.py"
    return {"schema_version": 1, "engine_version": __version__,
            "engine_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "python_version": platform.python_version(),
            "rng": "Python random.Random; SHA256-derived independent arm/rate streams v1",
            "interval": "Pointwise approximate 95% Wilson; not simultaneous or a difference test",
            "assumptions": ["One round; independent identical errors on data qubits only",
                            "Ideal preparation, encoding, recovery, decoding and readout",
                            "Fixed majority decoder; no optimization above p=0.5",
                            "Phase demonstration uses plus input and X readout"], **sweep}


def json_text(result):
    return json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"


def csv_text(result):
    rows = []
    for point in result["points"]:
        for row in point["rows"]:
            rows.append({"schema_version": result["schema_version"],
                         "engine_version": result["engine_version"],
                         "engine_sha256": result["engine_sha256"],
                         "python_version": result["python_version"],
                         **result["settings"], **row})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
