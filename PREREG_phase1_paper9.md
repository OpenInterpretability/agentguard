# PRE-REGISTRATION — Phase-1 (paper #9 grade): the authorization direction — detect AND control?

**Date:** 2026-06-13 (pre-run). **Model:** Qwen3.6-27B. **Runner:** `scripts/agentguard_phase1_detector_full.py`.
**Ledger:** HF `…:results/agentguard_phase1_detector_full.json`. Upgrades the n=40 pilot
(`RESULTS_phase0_detector.md`) to a publishable result. **The pilot's caveat to kill: AUROC=1.0 was
partly trivial (random-dir control 0.78–0.96 at L51/L63); only L59 was clean (random-dir 0.54).**

## Four upgrades
1. **Scale n.** 6 actions × n=24/condition = 144/condition (was 40, one action).
2. **Hard negatives.** Authorized and unauthorized scenarios share **identical action parameters**
   (same recipient/path/table/amount/token per scenario index); only the *authorization* differs.
   This removes the "different params" surface cue. Random-dir control should now fall toward 0.5;
   the probe AUROC above it is the real signal.
3. **Cross-domain.** All 6 irreversible actions (send_transaction, approve_allowance, delete_file,
   drop_table, deploy_production, send_email). **Cross-action transfer:** train on 5 actions, test on
   the held-out 6th — is "authorization-consistency" a domain-general direction or action-specific?
4. **The causal step (detect≠control — the arc's core discipline).** Extract the authorization
   direction d = mean(authorized) − mean(unauthorized) at the clean locus (L59). Then INTERVENE:
   - on **unauthorized-commit** states, add +α·d (push toward "authorized") → does P(commit) /
     generation-confirmed emit of the irreversible action **change**?
   - on **authorized-commit** states, add −α·d (push toward "unauthorized") → does it suppress a
     legitimate commit?
   Controls: random direction of equal norm; report ΔP and generation flips + McNemar.

## Hypotheses (pre-declared)
- **H1 (detector survives hard negatives).** Probe AUROC(authorized vs unauthorized) ≥ 0.80 at L59,
  with random-dir control ≤ 0.65 (i.e., a real gap probe−random ≥ 0.15) on parameter-matched scenarios.
- **H2 (cross-origin transfer).** Train inject → test model-origin AUROC ≥ 0.75 (the confound killer).
- **H3 (cross-action / domain-general).** Train 5 actions → test held-out action AUROC ≥ 0.70
  (averaged over the 6 held-out folds). If yes, the authorization direction is domain-general.
- **H4 (locus).** The probe−random gap peaks late and is largest at L59 (the action-commitment locus).
- **H5 (CONTROL — the decisive one).** Steering +α·d on unauthorized-commit states **reduces** the
  generation-confirmed irreversible-emit rate (Δ ≤ −0.15, McNemar significant) while a random
  direction of equal norm does not. If yes: the authorization direction is **causal**, not just
  predictive — one direction both detects and controls. **If no: honest negative** — the probe
  predicts but does not cause (the direction is read-only), consistent with the verdict-circuit
  result (#5, "the verdict is not the lever"). Either way is the paper.

## Controls (every claim)
random-direction (equal norm), shuffled-label (≈0.5), 1000× bootstrap CI on AUROC, gap-only
baseline, and the parameter-matched hard-negative design itself. Detection result is checkpointed to
HF *before* the steering stage, so a VM death preserves it.

## Interpretation
- Detector survives hard negatives + transfers across origin and action → **a domain-general,
  late-layer authorization direction** (strong; turns L2 into a real, characterized detector).
- H5 positive → the direction is the **mechanism** (detect+control unified) — the strongest possible
  paper #9. H5 negative → **detect≠control even here** — the model represents authorization but does
  not act on that representation; you must brake via the donor patch, not this direction. Publishable,
  and exactly the arc's recurring lesson. No outcome is failure.
