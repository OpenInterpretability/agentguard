# PRE-REG — layer sweep: is authorization a native feature at ANY layer the SAE covers?

**Date:** 2026-06-16. **Model:** Qwen3.6-27B (bf16, G4). **SAE:** all 11 trained layers
[15,19,23,27,35,39,43,47,51,59,63] of caiovicentino1/qwen36-27b-sae-fullstack. **Runner:**
`scripts/agentguard_sae_layer_sweep.py`.

## Motivation
'Form, Not Granted' (DOI 10.5281/zenodo.20724547) found no native authorization feature at **L59** (the
commit locus of the #9/#10 direction) and explicitly caveated that "a different layer could surface a
representation this analysis misses." We test that caveat directly. By the arc's own "the lever is late"
finding (knowledge consolidates ~30 layers before the action), a semantic authorization representation, if
it exists, is more likely in **mid layers** (where the model interprets the user's intent) than at the late
commit point (where form/scaffold dominate). We may have looked too late.

## Design
Reuse the structure-matched 2×2 counterfactual (granted/felt × lexical families A/B), n=12/cell. For each
commit, capture the residual at **two positions** in **all 11 SAE layers** (one forward per scenario):
- **preact** = the last prompt token (the model has just read the authorizing user turn, before generating);
- **commit** = the `<function=` decision token (what the #9/#10 monitor reads).
For each (layer, position): (a) the SAE cross-lexical-family generalization (select best feature on family A,
fix polarity, evaluate held-out on B; and B→A) — the selection-free semantic test; (b) the supervised
granted−felt direction trained on A, tested held-out on B. Name the transferring feature where cross-family
is high.

## Hypotheses (both outcomes are results)
- **H_a-LOCUS (authorization is represented, just not at the commit):** at some (layer, position) — predicted
  a mid layer at *preact* — the cross-lexical SAE/supervised AUROC stays high (≥ ~0.8 held-out) AND the
  transferring feature names to authorization/permission/user-instruction. → the concept IS native; the #9/#10
  monitor fails because it reads the late commit locus where the representation has given way to form. A
  richer, positive result that *revises* 'Form, Not Granted'.
- **H_0-DEPTH (no native authorization concept anywhere):** cross-family AUROC is at chance across all 11
  layers and both positions (the only transfers being scaffold/format features by naming). → the H_0 of
  'Form, Not Granted' strengthens from "not at L59" to "not anywhere the SAE covers."

## Output / honest scope
A cross-family-AUROC-vs-depth profile (11 layers × 2 positions) for SAE features and the supervised
direction; naming of any high-transfer feature. If H_a-LOCUS, the published paper gets an honest Zenodo
new-version with the layer result. One model, synthetic scenarios, the SAE's learned dictionary per layer
(FVE varies by layer); absence at a layer is still weaker than absence of any representation. Ledger on HF.
