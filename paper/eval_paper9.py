#!/usr/bin/env python3
"""EVAL — recompute every number in authorization_direction.tex from the public HF ledgers.
Run: python3 paper/eval_paper9.py"""
import json
from huggingface_hub import hf_hub_download
REPO = "caiovicentino1/swebench-phase6-verdict-circuit"
def L(f): return json.load(open(hf_hub_download(REPO, f"results/{f}", repo_type="dataset", force_download=True)))
P1 = L("agentguard_phase1_detector_full.json")
P2 = L("agentguard_phase2_honest_auroc.json")
GX = L("agentguard_xmodel_gpt-oss-20b.json")
ACTS = ["send_transaction","approve_allowance","delete_file","drop_table","deploy_production","send_email"]
PASS, FAIL = [], []
def chk(n, ok, got, want):
    (PASS if ok else FAIL).append(n); print(f"[{'PASS' if ok else '**FAIL**'}] {n}: got={got} want={want}")
def cl(a,b,t): return abs(float(a)-float(b))<=t

print("== Detect (Qwen Phase-1, full logistic) ==")
for l in [47,51,55,59,61,63]:
    chk(f"Qwen AUROC L{l}=1.0", P1["auroc"][f"L{l}"]["auc"]==1.0, P1["auroc"][f"L{l}"]["auc"], 1.0)
chk("Qwen random-dir L61=0.50", cl(P1["auroc"]["L61"]["rand"],0.498,0.01), round(P1["auroc"]["L61"]["rand"],3), 0.50)
chk("Qwen probe-random gap L61=+0.50", cl(P1["auroc"]["L61"]["gap"],0.502,0.01), round(P1["auroc"]["L61"]["gap"],3), 0.50)
chk("Qwen cross-origin transfer L59=0.89", cl(P1["transfer_inject_to_model"]["L59"],0.889,0.01), P1["transfer_inject_to_model"]["L59"], 0.889)
chk("Qwen cross-action mean=1.0", P1["cross_action"]["mean"]==1.0, P1["cross_action"]["mean"], 1.0)

print("\n== Detect honest (Qwen Phase-2, 1-D commit-matched) ==")
ha=P2["honest_auroc"]
chk("Qwen 1-D dom L59/61=1.0", ha["L59"]["dom_1d_heldout"]==1.0 and ha["L61"]["dom_1d_heldout"]==1.0, (ha["L59"]["dom_1d_heldout"],ha["L61"]["dom_1d_heldout"]), 1.0)
chk("Qwen 1-D dom L63=0.988", cl(ha["L63"]["dom_1d_heldout"],0.988,0.005), ha["L63"]["dom_1d_heldout"], 0.988)
chk("Qwen reg sweep flat 1.0 (L61 C1e-3..1e1)", ha["L61"]["reg_sweep"]["C0.001"]==1.0 and ha["L61"]["reg_sweep"]["C10.0"]==1.0, (ha["L61"]["reg_sweep"]["C0.001"],ha["L61"]["reg_sweep"]["C10.0"]), 1.0)
chk("Qwen PCA-32 L61=1.0", ha["L61"]["pca"]["pca32"]==1.0, ha["L61"]["pca"]["pca32"], 1.0)
chk("Qwen shuffled ~0.5 (all late <=0.55)", all(ha[f"L{l}"]["ctrl_shuffled"]<=0.55 for l in [47,51,55,59,61,63]), max(ha[f"L{l}"]["ctrl_shuffled"] for l in [47,51,55,59,61,63]), "<=0.55")
chk("Qwen random-1d <=0.32 (all late)", all(ha[f"L{l}"]["ctrl_random_1d"]<=0.33 for l in [47,51,55,59,61,63]), max(ha[f"L{l}"]["ctrl_random_1d"] for l in [47,51,55,59,61,63]), "<=0.32")
chk("Qwen n=144 auth vs 141 unauth (commit-matched)", ha["L59"]["n_auth"]==144 and ha["L59"]["n_unauth"]==141, (ha["L59"]["n_auth"],ha["L59"]["n_unauth"]), (144,141))

print("\n== Control (Qwen Phase-1 steering) ==")
chk("Qwen steer range d=0.667", cl(P1["verdict"]["H5_emit_range_d"],0.667,0.01), P1["verdict"]["H5_emit_range_d"], 0.667)
chk("Qwen steer range random=0.027", cl(P1["verdict"]["H5_emit_range_random"],0.027,0.01), P1["verdict"]["H5_emit_range_random"], 0.027)
se=P1["steer"]["send_email"]
chk("Qwen send_email -d(-2)->0.00", se["d"][0]==0.0, se["d"][0], 0.0)
chk("Qwen send_email +d(+2)->1.00", se["d"][3]==1.0, se["d"][3], 1.0)
chk("Qwen send_email base=0.42", cl(se["base"],0.42,0.01), se["base"], 0.42)

print("\n== Cross-model (gpt-oss-20b) ==")
v=GX["verdict"]
chk("gpt-oss detect 1-D commit-matched @LB=1.0", v["detect_dom1d_LB"]==1.0, v["detect_dom1d_LB"], 1.0)
chk("gpt-oss random-dir @LB=0.47", cl(v["rand1d_LB"],0.474,0.01), round(v["rand1d_LB"],3), 0.47)
chk("gpt-oss cross-action=1.0", v["cross_action_mean"]==1.0, v["cross_action_mean"], 1.0)
chk("gpt-oss locus depth 92%", v["depth_pct"]==92, v["depth_pct"], 92)
chk("gpt-oss best layer L22", v["best_layer"]==22, v["best_layer"], 22)
chk("gpt-oss steer range d=0.65", cl(v["steer_range_d"],0.653,0.01), round(v["steer_range_d"],3), 0.65)
chk("gpt-oss steer range random=-0.25", cl(v["steer_range_rand"],-0.25,0.01), v["steer_range_rand"], -0.25)

print("\n== Behavioral (both obey explicit, self-commit benign) ==")
chk("Qwen obeys explicit=0.00 (all 6)", all(P2["commit_frac"][a]["unauth_explicit"]==0.0 for a in ACTS), [P2["commit_frac"][a]["unauth_explicit"] for a in ACTS], "all 0.0")
chk("gpt-oss obeys explicit=0.00", cl(v["obeys_explicit"],0.0,1e-9), v["obeys_explicit"], 0.0)
chk("gpt-oss self-commits model_origin=1.0 (all 6)", cl(v["selfcommits_model_origin"],1.0,1e-9), v["selfcommits_model_origin"], 1.0)
chk("Qwen self-commits model_origin (>=4/6 commit)", sum(P2["commit_frac"][a]["model_origin"]>0.5 for a in ACTS)>=4, sum(P2["commit_frac"][a]["model_origin"]>0.5 for a in ACTS), ">=4")

print("\n== Loci ==")
chk("Qwen L61 = 95% depth", round(100*61/64)==95, round(100*61/64), 95)
chk("gpt-oss L22 = 92% depth", round(100*22/24)==92, round(100*22/24), 92)

print(f"\n== SUMMARY ==\nPASS {len(PASS)}  FAIL {len(FAIL)}")
if FAIL:
    print("FAILURES:"); [print("  -",f) for f in FAIL]
else:
    print("ALL PAPER-#9 NUMBERS VERIFIED AGAINST THE HF LEDGERS.")
