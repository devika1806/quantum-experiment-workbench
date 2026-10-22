# Platform support and access

The application is a Python program with a browser interface. It contains no Windows API calls, drive-letter paths or Windows-only runtime dependencies. The core uses Python's standard library, portable `pathlib` paths and explicit UTF-8 file encoding.

| Platform | Intended use | Verification status |
|---|---|---|
| Windows | CLI, Streamlit app, Qiskit verifier, static plots | Locally exercised on Python 3.14.4 |
| macOS | Same tools using a Unix-style virtual environment | CI configured; execution pending |
| Linux | Same tools using a Unix-style virtual environment | CI configured; execution pending |
| Android / iPhone / iPad | Browser access to a separately hosted instance | No native app or mobile test; public hosting not configured |

## Automated checks

GitHub Actions schedules core tests on Windows, macOS and Ubuntu with Python 3.11 and 3.14. Separate jobs install UI and research dependencies on all three OSes with Python 3.12, check dependency consistency, run every test, perform Qiskit verification and render figures. These are nine planned jobs. Each runner represents one OS/architecture combination, not every release or processor architecture.

Configured checks are not passed checks. Update the table only after the corresponding remote runs complete. Python 3.12 is recommended for a fresh setup because the full dependency checks target that version; the code requires at least Python 3.11. Windows local verification used 3.14.4.

## Installation

The [README](../README.md) contains complete Windows PowerShell and macOS/Linux command blocks. On macOS/Linux, use `python3 -m venv .venv`, then `.venv/bin/python` for installation and execution. On Windows use `python -m venv .venv`, then `.\.venv\Scripts\python.exe`.

If Python is missing, install Python 3.12 for your OS first. Some Linux distributions package `venv` separately; install the matching Python venv package using that distribution's instructions. Commands invoke the environment's Python directly, so shell activation and PowerShell execution-policy changes are unnecessary.

The CLI needs no Streamlit installation: `python -m workbench --help` on Windows, or `python3 -m workbench --help` on macOS/Linux. For optional circuit checks and figures, install `requirements-research.txt` in the same environment. Plotting uses the headless Agg backend, so Linux servers need no desktop display.

## Browser access is different from OS support

After starting Streamlit, open the local URL it prints on that same computer. `http://127.0.0.1:8502` points to this computer only. On a phone or another laptop, `127.0.0.1` points to that other device, not this running demo.

Publishing source on GitHub does **not** host a Python application. GitHub Pages alone cannot run this Streamlit server. A shareable browser link requires a separate Streamlit-capable hosting deployment, which has not been configured. Local setup does not require changing firewall settings or exposing your computer to the internet.

The UI was visually checked in a local desktop browser at a narrow viewport. Safari, Firefox, Chrome and mobile-browser coverage have not been separately established.

## Reproducibility across machines

Use the same seed, settings, engine version and Python version. Records include the runtime version and engine SHA256. `.gitattributes` keeps Python source line endings as LF so Windows checkout conversion does not change that fingerprint. JSON/CSV use UTF-8; tests check exports to paths containing spaces and non-ASCII characters. Floating-point reference comparisons use a tolerance rather than assuming identical last bits on every math library.
