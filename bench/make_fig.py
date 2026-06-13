"""Render the AgentActionBench coverage matrix as a heatmap."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from bench.run_bench import run, COLUMNS, ORIGIN_CLASSES

_, M = run()
row_label = {"input_plain": "input-origin\n(plain)", "input_obf_allow": "input-origin\n(obfusc.+allowlisted)",
             "model_origin": "MODEL-origin\n(clean context)", "benign": "benign\n(false-positive ctrl)"}
rows = ORIGIN_CLASSES
grid = np.array([[M[r][c] for c in COLUMNS] for r in rows])

fig, ax = plt.subplots(figsize=(10, 4.2))
# attacks: green=caught(good). benign row: green should be LOW (0 FP) -> invert color meaning via text.
im = ax.imshow(grid, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(COLUMNS))); ax.set_xticklabels(COLUMNS, fontsize=9)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([row_label[r] for r in rows], fontsize=9)
for i, r in enumerate(rows):
    for j, c in enumerate(COLUMNS):
        v = grid[i, j]
        txt = f"{v*100:.0f}%"
        if r == "benign":
            txt = f"{v*100:.0f}%\nFP"
        ax.text(j, i, txt, ha="center", va="center", fontsize=8.5,
                color="black" if 0.25 < v < 0.85 else "white")
# divider before the union column
ax.axvline(len(COLUMNS) - 1.5, color="black", lw=2)
ax.set_title("AgentActionBench — irreversible-action attack coverage (24 scenarios, 6 actions x 4 origins)\n"
             "attacks: green = caught (want 100%).  benign row: FP rate (want 0%).  "
             "L2 = model-internal brake (grounded in Zenodo 10.5281/zenodo.20679287)", fontsize=8.5)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), "..", "figures", "agentactionbench_coverage.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight")
print("saved", os.path.normpath(out))
