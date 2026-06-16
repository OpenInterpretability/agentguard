# EVAL — Form, Not Granted (33/33 numeric checks PASS)

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
- PASS — tex B2A 0.99
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

---
## Pre-mint eval (3 layers) — 0 blockers
- **Numeric:** 33/33 PASS (above) — every number recomputed from the 4 SAE ledgers.
- **Citations:** 5/5 external web-verified (Bricken/Towards-Monosemanticity, Cunningham 2309.08600,
  Gao 2406.04093 TopK, Marks&Tegmark 2310.06824, Bolukbasi 2104.07143; refusaldir 2406.11717 verified prior),
  0 fabrications; 2 self-cites are published arc DOIs (authdir 20683623, feltnotgranted 20685264).
- **Reproducibility:** the decisive counterfactual run reproduced bit-for-bit across two GPU sessions
  (crossA2B 0.50, crossB2A 0.993, pooled 0.998, feats 34355/1574/10017 — verified in the session log).
- **Honest scope present:** qualifies-not-refutes #9/#10; FVE 0.66; absence-of-evidence caveat; one
  model/locus/domain; steering-control not re-tested.
