"""Render scientific plots from saved records; never reruns or changes trials."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render(source, target):
    data = json.loads(Path(source).read_text(encoding="utf-8"))
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.5, 1]})
    for arm, color in (("Unprotected", "#C85A44"), ("Repetition code", "#15796E")):
        rows = [r for p in data["points"] for r in p["rows"] if r["arm"] == arm]
        x = [r["p"] for r in rows]
        for ax in axes:
            ax.plot(x, [r["expected"] for r in rows], "--", color=color, label=f"{arm}: theory")
            ax.errorbar(x, [r["rate"] for r in rows],
                        yerr=[[max(0, r["rate"]-r["ci_low"]) for r in rows], [max(0, r["ci_high"]-r["rate"]) for r in rows]],
                        fmt="o", ms=4, capsize=2, color=color, label=f"{arm}: sample + 95% interval")
            ax.grid(alpha=.16)
            ax.set_xlabel("Physical error probability p")
            ax.set_ylabel("Measured / predicted error probability")
    axes[0].set(xlim=(-.01, 1.01), ylim=(-.02, 1.02), title="Full range: includes where the decoder fails")
    axes[1].set(xlim=(-.005, .21), ylim=(-.01, .42 if data["settings"]["noise"] == "phase" else .23), title="Zoom: low error probabilities")
    axes[0].legend(fontsize=8, loc="upper left")
    s = data["settings"]
    fig.suptitle(f"{'Bit-flip protection' if s['noise']=='bit' else 'Phase-flip failure'} | input {s['initial']} | {s['shots']:,} shots per point/arm | seed {s['seed']}", fontweight="bold")
    fig.text(.5, .015, "Ideal single-round model. Intervals are pointwise Wilson 95%, not simultaneous bands. No hardware data.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .93))
    fig.savefig(target, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    for mode in ("bit", "phase"):
        render(f"results/{mode}/experiment.json", f"results/{mode}/comparison.png")
