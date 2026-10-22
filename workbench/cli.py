"""python -m workbench --help"""
import argparse
import sys
from pathlib import Path
from .engine import Settings, run_sweep
from .records import record, json_text, csv_text


def main(argv=None):
    # Some Windows terminals and minimal Unix locales cannot render Unicode
    # paths. Escape unsupported display characters without changing file names.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Compare an unprotected qubit with an ideal repetition code.")
    parser.add_argument("--noise", choices=("bit", "phase"), default="bit")
    parser.add_argument("--initial", choices=("0", "1", "+"), help="Default: 0 for bit noise; + for phase noise")
    parser.add_argument("--rates", default="0,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1", help="Comma-separated probabilities, including boundaries if desired")
    parser.add_argument("--shots", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1806)
    parser.add_argument("--out", type=Path, help="Output folder (files are not overwritten without --force)")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        settings = Settings(args.noise, args.initial or ("0" if args.noise == "bit" else "+"), args.shots, args.seed)
        rates = [float(p.strip()) for p in args.rates.split(",")]
        if args.out and not args.force and any((args.out / f"experiment.{ext}").exists() for ext in ("json", "csv")):
            raise ValueError("Output exists. Choose another folder or use --force.")
        result = record(run_sweep(rates, settings))
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "experiment.json").write_text(json_text(result), encoding="utf-8")
            (args.out / "experiment.csv").write_text(csv_text(result), encoding="utf-8", newline="")
        print("p     arm               observed   expected   95% Wilson interval")
        for point in result["points"]:
            for r in point["rows"]:
                print(f"{r['p']:.3f} {r['arm']:17} {r['rate']:9.4%} {r['expected']:10.4%} [{r['ci_low']:.4%}, {r['ci_high']:.4%}]")
        if args.out:
            print(f"Saved JSON and CSV in {args.out.resolve()}")
        return 0
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
