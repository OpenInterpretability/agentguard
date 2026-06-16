# EVAL — Form, Not Granted (34/34 numeric checks PASS)

Recomputed from the 4 SAE ledgers by `eval_commit_ontology.py`.

- PASS — v1 supervised 0.838
- PASS — matched supervised 0.08
- PASS — tex flip 0.838
- PASS — tex flip 0.08
- PASS — tex flip phrase
- PASS — within A 1.0
- PASS — within B 1.0
- PASS — cross A2B 0.5
- PASS — cross B2A 0.993
- PASS — sup cross A2B 0.764
- PASS — sup cross B2A 1.0
- PASS — pooled 0.998
- PASS — pooled p 0
- PASS — pooled feat 34355
- PASS — featA 1574
- PASS — featB 10017
- PASS — tex A2B 0.50
- PASS — tex B2A 0.993 (exact)
- PASS — tex 5 new cites present
- PASS — tex pooled 0.998
- PASS — tex featA 34355
- PASS — naming 34355 = format boilerplate
- PASS — naming 10017 = scaffold <function=
- PASS — naming 1574 = format example
- PASS — tex names example_function_name
- PASS — v1 best feat is scaffold
- PASS — matched best feat is file-listing
- PASS — tex naming claim surface
- PASS — d_sae 40960
- PASS — tex d_sae 40960
- PASS — recon relerr ~0.58
- PASS — tex FVE 0.66
- PASS — tex qualifies not refutes
- PASS — tex absence caveat

## Final pre-mint eval (3 layers) — 0 blockers
- **Numeric:** recompute from 4 ledgers, all PASS.
- **Citations:** 13 total. 10 external web-verified (refusaldir, monosemantic, saefind, topk, geometry,
  interpillusion + the 5 added: controltasks/Hewitt-Liang, saeeval/Makelov-Lange-Nanda, nonlinear/Engels,
  shortcut/Geirhos, scalingmono/Templeton), 0 fabrications; 2 self-cite published arc DOIs.
- **Adversarial prose audit (agent):** 0 BLOCKERS, 3 MINOR — all fixed: (1) B→A 0.99→0.993 (exact ledger);
  (2) clarified #10017 as "the B→A transferring feature" not loosely "invariant"; (3) the "1000×" permutation
  count is hardcoded in the runners (`agentguard_sae_{counterfactual,autopsy}.py`, `for _ in range(1000)`),
  reproducible. Auditor confirmed H_0 hedged correctly, qualifies-not-refutes consistent, FVE/absence-of-
  evidence caveats present, flip is selection-free, verdict_native flag debunked, em-dash self-correction stated.
