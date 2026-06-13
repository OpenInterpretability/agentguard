# PRE-REG — Phase-2: take the detector AUROC off the ceiling (honest number)

**Date:** 2026-06-13. **Model:** Qwen3.6-27B. **Runner:** `scripts/agentguard_phase2_honest_auroc.py`.
Phase-1 gave AUROC=1.0 (a ceiling: d=5120 ≫ n=144, perfect linear separability; controls clean but the
magnitude is uninformative). This run produces an **honest, non-saturated** number by removing the two
causes of the ceiling.

## Two fixes
1. **Overfitting-proof metric.** Primary = **difference-of-means 1-D, held-out** AUROC (project test
   residuals onto d=mean(unauth_train)−mean(auth_train); 1 DOF, cannot overfit). Plus a regularization
   sweep (logistic C∈{1e-3…1e1}) and PCA-k (k∈{16,32,64}) — show AUROC vs probe capacity.
2. **Commit-state-matched HARD negatives.** The residual confound is that authorized always commits
   (P=1.0) while unauthorized sometimes does not — so a probe could read *commit-propensity*, not
   authorization. Fix: compare **only scenarios that COMMIT** (P(commit)>0.5 at the prefill) — authorized-
   commit vs unauthorized-commit, both committing, so authorization is the only thing left. Plus
   near-duplicate negatives:
   - `unauth_explicit`: user says "do NOT send X to P, just check" — agent commits anyway (matched
     params, only the authorization polarity differs).
   - `unauth_ambiguous`: "I might send X to P later…" — vague, no authorization; agent commits.
   - `model_origin`: benign unrelated task; agent self-commits (Phase-1 condition, for comparison).

## Hypotheses
- **H1.** The 1-D held-out AUROC on commit-state-matched HARD negatives is **> 0.65** (above chance) and
  **< 1.0** (off the ceiling) — a real, honest number; largest late (peaks ~L59–L61).
- **H2.** AUROC rises with probe capacity (C↑ / PCA-k↑), confirming the 1.0 was capacity-driven; the
  low-capacity (1-D / strong-reg / small-k) number is the honest one to report.
- **H3 (sanity).** Random-direction 1-D ≈ 0.5; shuffled-label ≈ 0.5; ambiguous negatives give a *lower*
  AUROC than explicit ones (genuinely harder).

## Interpretation
The 1-D held-out AUROC on commit-matched hard negatives is the number that goes in paper #9 (replaces
"1.0"). If it is high but <1.0 (e.g., 0.8–0.95) the detector is real and strong; if it is near chance
once commit-state is matched, the Phase-1 1.0 was the commit-propensity confound and the honest claim
shrinks to "authorization is decodable only jointly with commit-state" — still publishable, and the
right thing to report. No outcome is failure. Capture-only (fast, low VM-death risk).
