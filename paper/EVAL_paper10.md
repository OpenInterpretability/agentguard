# EVAL paper #10 — recompute from ledgers

**54/54 numeric checks PASS.** Recomputed from `results/agentguard_realtest_fs_{adv,real,v5}.json` by `eval_paper10.py`.

- PASS — calib auth 29.98
- PASS — calib unauth -36.28
- PASS — threshold -3.15
- PASS — tex states tau -3.15
- PASS — calib identical to v4
- PASS — easy injected rate 0
- PASS — easy goal_pressure rate 0
- PASS — easy over_eager rate 0
- PASS — adv NPC 12 -> 0/12
- PASS — tex says 0/12 each
- PASS — momentum 18/18
- PASS — dead_weight 3/18=0.167
- PASS — urgent_space 0/12
- PASS — authorized 12/12
- PASS — tex momentum 18/18
- PASS — tex dead_weight 3/18
- PASS — v4 dead_weight 12/12
- PASS — tex says 12/12 single fixed prompt
- PASS — n realistic unauth = 21
- PASS — tex n=21
- PASS — unique scores 14
- PASS — tex 14 distinct
- PASS — probe fail 21/21
- PASS — judge catch 21/21
- PASS — auth FP 0/12
- PASS — probe fail rate 1.0
- PASS — probe CI [0.845,1.0]
- PASS — judge catch CI [0.845,1.0]
- PASS — FP CI [0,0.243]
- PASS — tex CI 0.845
- PASS — tex FP CI 0.243
- PASS — unauth mean 11.87
- PASS — unauth min 7.65
- PASS — unauth max 15.93
- PASS — auth mean 15.17
- PASS — auth min 12.29
- PASS — auth max 18.56
- PASS — tex unauth mean 11.87
- PASS — tex auth mean 15.17
- PASS — AUROC probe 0.90
- PASS — AUROC probe in verdict 0.897
- PASS — AUROC judge 1.0
- PASS — tex AUROC 0.897 (precise, 3x)
- PASS — tex AUROC 1.0 judge
- PASS — overlap: max unauth > min auth
- PASS — v5 60 records
- PASS — tex 60 scenarios
- PASS — 12 disposable filenames
- PASS — tex 12 disposable x 6
- PASS — multiple delete_file in some momentum gens
- PASS — layer 59
- PASS — tex layer 59
- PASS — bf16
- PASS — tex bf16 no quant

---

## Complete pre-mint eval (3 layers) — 0 blockers

**Layer 1 — numeric recompute:** 54/54 PASS (above). Every load-bearing number recomputed from the 3 ledgers.

**Layer 2 — citation web-verification (agent):** 7/7 external citations OK, **0 fabrications** (refusaldir
arXiv:2406.11717, taskdrift 2406.00799, camel 2503.18813, injection 2302.12173, judge 2306.05685,
sycophancy 2310.13548, corrigibility AAAI-2015 — all titles/authors/venues/arXiv IDs confirmed). 3
self-cites are published arc DOIs (authdir 20683623, safetybrake 20679287, leverislate 20534219).

**Layer 3 — adversarial overclaim/prose audit (agent):** **0 BLOCKERS, 1 MINOR** (AUROC 0.897 shown as
0.90 without "≈"). Fix applied: prose and Fig.2 now state the exact 0.897; the conservative n=14 lower
bound corrected 0.77→0.78 (wilson(14,14)=0.785). The reviewer confirmed: detection-not-steering scoping is
honest, the "blind vs AUROC 0.90" tension is handled correctly (rank-separable vs operationally blind at
the honest threshold), the same-base-model judge caveat is present, and the qualification-not-refutation
framing of paper #9 does not overclaim. Verdict: **publication-ready on fabrication grounds.**
