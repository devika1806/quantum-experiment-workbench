"""Presentation only: all simulation and exports live in workbench/."""
import altair as alt
import streamlit as st
from workbench.engine import Settings, run_sweep
from workbench.records import record, csv_text, json_text

st.set_page_config(page_title="Quantum Experiment Workbench", page_icon="🔬", layout="wide")
st.caption("QUANTUM EXPERIMENT WORKBENCH  /  INVESTIGATION 02")
st.title("When do three qubits help?")
st.write("Make a prediction. Compare a single unprotected qubit with a three-qubit repetition code. Then inspect the evidence.")
st.info("An ideal simulator: one noise round, independent errors, perfect encoding and decoding. No hardware experiment or quantum speed advantage is claimed.")

with st.sidebar:
    st.header("Design your experiment")
    mode = st.selectbox("Investigation", ["Bit flips · can repetition help?", "Phase flips · see the limitation"])
    noise = "bit" if mode.startswith("Bit") else "phase"
    initial = st.selectbox("Input state", ["0", "1"] if noise == "bit" else ["+"])
    selected_p = st.slider("Physical error probability p", 0.0, 1.0, 0.10, 0.01)
    shots = st.number_input("Shots per probability, per arm", min_value=100, max_value=100_000, value=20_000, step=100)
    seed = st.number_input("Random seed", min_value=0, max_value=2**32-1, value=1806, step=1)
    sweep = st.checkbox("Compare across p = 0 to 1", value=True)
    st.caption("The sweep uses 11 values plus your selected p. Each arm uses fresh independent samples. Saved results retain the settings that produced them.")

if noise == "bit":
    st.subheader("1 · Predict before running")
    st.write("For input 0: encode 000 → flip each bit with chance p → choose the majority. Input 1 works the same way, starting from 111.")
else:
    st.subheader("1 · Predict a failure")
    st.warning("This is still the bit-flip code. We deliberately apply phase errors it cannot correct. Input + and X readout reveal the damage; Z readout of 0 or 1 would hide it.")
    st.write("Encode + as (000 + 111)/√2. An odd number of phase flips changes the relative sign. The bit-error checks see no error, and X readout after decoding returns minus.")

prediction = st.text_input("Your prediction (optional)", placeholder="I think repetition will help below… because…")
if st.button("Run experiment", type="primary"):
    try:
        rates = sorted(set([round(i/10, 2) for i in range(11)] + [selected_p])) if sweep else [selected_p]
        with st.spinner("Preparing fresh trials and counting outcomes…"):
            result = record(run_sweep(rates, Settings(noise, initial, int(shots), int(seed))))
        result["prediction"] = prediction
        result["selected_p"] = selected_p
        st.session_state["result"] = result
    except ValueError as exc:
        st.error(str(exc))

if "result" not in st.session_state:
    st.caption("Choose settings on the left and press Run experiment. No trials have been run yet.")
else:
    result = st.session_state["result"]
    saved = result["settings"]
    expected_rates = sorted(set([round(i/10, 2) for i in range(11)] + [selected_p])) if sweep else [selected_p]
    if saved != {"noise": noise, "initial": initial, "shots": int(shots), "seed": int(seed)} or result["rates"] != expected_rates or result["selected_p"] != selected_p:
        st.warning("Settings changed. These are the previous run's results. Press Run experiment to apply your new settings.")
    st.subheader("2 · Inspect the evidence")
    st.caption(f"Saved run: {saved['noise']} noise · input {saved['initial']} · {saved['shots']:,} shots per arm and p · seed {saved['seed']} · {len(result['rates'])} probabilities")
    if result.get("prediction"):
        st.write("Your saved prediction:", result["prediction"])
    point = next(p for p in result["points"] if p["p"] == result["selected_p"])
    cols = st.columns(3)
    for col, row in zip(cols, point["rows"]):
        with col:
            st.metric(row["arm"] + " measured error", f"{row['rate']:.2%}")
            st.caption(f"{row['errors']:,} errors / {row['shots']:,} trials at p={point['p']:.2f}. Theory: {row['expected']:.2%}.")
    with cols[2]:
        gain = point["rows"][0]["expected"] - point["rows"][1]["expected"]
        st.metric("Predicted reduction", f"{gain*100:+.2f} pp")
        st.caption("pp = percentage points. Positive means fewer errors with the code. This theoretical difference is not a significance test.")

    rows = [r for p in result["points"] for r in p["rows"]]
    base = alt.Chart(alt.Data(values=rows)).encode(
        x=alt.X("p:Q", title="Physical error probability p", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("arm:N", title="Protection", scale=alt.Scale(domain=["Unprotected", "Repetition code"], range=["#C85A44", "#15796E"])))
    predicted = base.mark_line(strokeDash=[6, 4], point=True).encode(
        y=alt.Y("expected:Q", title="Error probability", scale=alt.Scale(domain=[0, 1])),
        tooltip=["arm:N", "p:Q", alt.Tooltip("expected:Q", format=".4f")])
    intervals = base.mark_rule(strokeWidth=2).encode(y="ci_low:Q", y2="ci_high:Q")
    measured = base.mark_point(filled=True, size=70).encode(
        y="rate:Q", tooltip=["arm:N", "p:Q", "errors:Q", "shots:Q", alt.Tooltip("rate:Q", format=".4f"), "ci_low:Q", "ci_high:Q"])
    st.altair_chart((predicted + intervals + measured).properties(height=360), width="stretch")
    st.caption("Dashed lines: theory evaluated at the selected probabilities (joined for guidance). Solid dots: samples. Vertical bars: pointwise approximate 95% Wilson intervals. A whole curve is not guaranteed 95% coverage; interval overlap is not a test of the difference.")
    if saved["noise"] == "bit":
        st.latex(r"P_{\mathrm{code}}=3p^2(1-p)+p^3=3p^2-2p^3")
        st.write("Two or three flips defeat the majority. This fixed decoder helps for 0 < p < 0.5, ties at 0, 0.5 and 1, and hurts for 0.5 < p < 1. This crossover is not a hardware fault-tolerance threshold.")
    else:
        st.latex(r"P_{\mathrm{phase}}=3p(1-p)^2+p^3")
        st.write("An odd number of phase errors survives. At p=0.1, the predicted phase error rises from 10% unprotected to 24.4% encoded. This code does not correct a single phase error.")
    with st.expander("Inspect the physical error patterns and all measurements"):
        st.write("At the selected p, 1 means an error on that data qubit. Strings are ordered q2 q1 q0; they are error masks, not measured data values.")
        st.json(point["physical_error_patterns_q2q1q0"])
        st.dataframe(rows, hide_index=True)
    st.subheader("3 · Explain and save")
    reflection = st.text_area("What changed your mind? What would you test next?", key="reflection")
    export = {**result, "reflection": reflection}
    left, right = st.columns(2)
    left.download_button("Download full JSON record", json_text(export), "experiment.json", "application/json")
    right.download_button("Download measurement CSV", csv_text(export), "experiment.csv", "text/csv")
    st.caption("JSON includes settings, error-pattern counts, code fingerprint, prediction and reflection. CSV includes the measurement rows and reproducibility settings.")

with st.expander("A five-minute learning route"):
    st.markdown("""1. Run bit noise at p=0.1. Compare 10% with the predicted 2.8%.
2. Try p=0, 0.5 and 1. Explain the ties.
3. Try p=0.8. A fixed majority rule now makes things worse.
4. Increase shots with the same seed. The estimate should usually become steadier, but need not get closer every time.
5. Switch to phase flips at p=0.1. Explain why a code that fixes X errors can still fail for Z errors.

The core bit experiment is equivalent to a classical three-bit repetition calculation. A separate Qiskit verification checks ideal quantum encoding and decoding, including superpositions. Encoding an unknown qubit creates an entangled state; it does not make three independent copies.
""")
st.caption("Read README.md and docs/RESEARCH.md for the experiment protocol, derivation, limitations and primary sources.")
