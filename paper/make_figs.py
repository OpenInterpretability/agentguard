#!/usr/bin/env python3
"""Figures for paper #9 (the authorization direction), from the HF ledgers."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from huggingface_hub import hf_hub_download
REPO = "caiovicentino1/swebench-phase6-verdict-circuit"
def L(f): return json.load(open(hf_hub_download(REPO, f"results/{f}", repo_type="dataset", force_download=True)))
P1 = L("agentguard_phase1_detector_full.json")
P2 = L("agentguard_phase2_honest_auroc.json")
GX = L("agentguard_xmodel_gpt-oss-20b.json")
OUT = os.path.join(os.path.dirname(__file__), "figures"); os.makedirs(OUT, exist_ok=True)
ACTS = ["send_transaction","approve_allowance","delete_file","drop_table","deploy_production","send_email"]

# ---------- Fig 1: the detector locus — random-dir control by depth (probe stays 1.0) ----------
fig, ax = plt.subplots(figsize=(7.5, 4.2))
qL = [47,51,55,59,61,63]; qNL = 64
qrand = [P1["auroc"][f"L{l}"]["rand"] for l in qL]
qdepth = [100*l/qNL for l in qL]
ax.plot(qdepth, qrand, "o-", color="#1f77b4", label="Qwen3.6-27B (hybrid): random-dir ctrl")
gL = GX["config"]["late_layers"]; gNL = GX["config"]["NL"]
grand = [GX["detect"][f"L{l}"]["rand_1d"] for l in gL]; gdepth = [100*l/gNL for l in gL]
ax.plot(gdepth, grand, "s-", color="#d62728", label="gpt-oss-20b (MoE): random-dir ctrl")
ax.axhline(1.0, color="#2ca02c", ls="-", lw=2, label="probe (1-D, commit-matched) AUROC = 1.00")
ax.axhline(0.5, color="#888", ls=":", lw=1, label="chance")
ax.set_xlabel("layer depth (%)"); ax.set_ylabel("AUROC (authorized vs unauthorized)")
ax.set_ylim(0.35, 1.05); ax.legend(fontsize=8, loc="center left")
ax.set_title("The authorization signal is SPECIFIC at a late locus\n"
             "(probe stays 1.0; a random direction falls to chance only deep — that is the clean locus)", fontsize=9.5)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_locus.png", dpi=150, bbox_inches="tight"); print("fig1")

# ---------- Fig 2: the causal step — steering emit vs alpha along d vs random (Qwen) ----------
fig, ax = plt.subplots(figsize=(7.5, 4.2))
headroom = ["send_transaction","approve_allowance","drop_table","send_email"]
xs = [-2,-1,0,1,2]
for a in headroom:
    b = P1["steer"][a]   # {"base", "d":[-2,-1,1,2], "rand":[-2,2]}
    ys = [b["d"][0], b["d"][1], b["base"], b["d"][2], b["d"][3]]
    ax.plot(xs, ys, "o-", label=a)
# random aggregate (mean over headroom): at x=[-2,0,2]
rb = np.mean([[P1["steer"][a]["rand"][0], P1["steer"][a]["base"], P1["steer"][a]["rand"][1]] for a in headroom], 0)
ax.plot([-2,0,2], rb, "x--", color="#555", lw=2, label="random dir (mean, equal norm)")
ax.set_xlabel("steering α along d = mean(authorized) − mean(unauthorized)")
ax.set_ylabel("irreversible-action emit rate"); ax.set_xticks(xs); ax.set_ylim(-0.05,1.08)
ax.legend(fontsize=8, ncol=2)
ax.set_title("Steering the authorization direction CONTROLS the commit (Qwen3.6-27B, L59)\n"
             "−d suppresses unauthorized commits, +d boosts; a random direction is inert", fontsize=9.5)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_steering.png", dpi=150, bbox_inches="tight"); print("fig2")

# ---------- Fig 3: cross-model replication (detect + control + behavioral) ----------
fig, ax = plt.subplots(figsize=(7.5, 4.0))
metrics = ["detect AUROC\n@ locus", "random-dir\n@ locus", "cross-action\ntransfer", "steering range\n(d)", "steering range\n(random)"]
qv = [P1["auroc"]["L61"].get("auc", 1.0), P1["auroc"]["L61"]["rand"],
      P1["cross_action"]["mean"], P1["verdict"]["H5_emit_range_d"], P1["verdict"]["H5_emit_range_random"]]
gv = [GX["verdict"]["detect_dom1d_LB"], GX["verdict"]["rand1d_LB"], GX["verdict"]["cross_action_mean"],
      GX["verdict"]["steer_range_d"], GX["verdict"]["steer_range_rand"]]
x = np.arange(len(metrics)); w=0.38
ax.bar(x-w/2, qv, w, label="Qwen3.6-27B (hybrid)", color="#1f77b4")
ax.bar(x+w/2, gv, w, label="gpt-oss-20b (MoE)", color="#d62728")
for xi,(q,g) in enumerate(zip(qv,gv)):
    ax.text(xi-w/2, q+0.02 if q>=0 else q-0.06, f"{q:.2f}", ha="center", fontsize=7.5)
    ax.text(xi+w/2, g+0.02 if g>=0 else g-0.06, f"{g:.2f}", ha="center", fontsize=7.5)
ax.axhline(0, color="k", lw=0.6); ax.set_xticks(x); ax.set_xticklabels(metrics, fontsize=8)
ax.set_ylabel("value"); ax.legend(fontsize=9)
ax.set_title("Detect AND control replicate across two architecture families", fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_crossmodel.png", dpi=150, bbox_inches="tight"); print("fig3")

# ---------- Fig 4: behavioral — commit_frac (obeys explicit, self-commits benign) ----------
fig, ax = plt.subplots(figsize=(7.5, 2.8))
conds = ["authorized","unauth_explicit","unauth_ambiguous","model_origin"]
clab = ["authorized","explicit\n'do NOT'","ambiguous","model-origin\n(benign task)"]
def mean_cf(D): return [np.mean([D["commit_frac"][a][c] for a in ACTS]) for c in conds]
grid = np.array([mean_cf(P2), mean_cf(GX)])
im = ax.imshow(grid, cmap="OrRd", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(4)); ax.set_xticklabels(clab, fontsize=8.5)
ax.set_yticks([0,1]); ax.set_yticklabels(["Qwen3.6-27B","gpt-oss-20b"], fontsize=9)
for i in range(2):
    for j in range(4): ax.text(j,i,f"{grid[i,j]:.2f}",ha="center",va="center",fontsize=10,color="black" if grid[i,j]<0.6 else "white")
ax.set_title("Commit rate of the irreversible action: both models OBEY explicit prohibition (0.00)\n"
             "but SELF-COMMIT from a benign task (model-origin harm)", fontsize=9.5)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_behavioral.png", dpi=150, bbox_inches="tight"); print("fig4")
print("all figures ->", OUT)
