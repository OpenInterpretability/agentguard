# EVAL — paper #9 (the authorization direction), pre-publication gate
Date: 2026-06-13. **0 blockers.**
- **Numeric:** `paper/eval_paper9.py` recomputes every number in `authorization_direction.tex` from the
  3 public HF ledgers (phase1 detector, phase2 honest-AUROC, xmodel gpt-oss) → **35/35 PASS**.
- **Citations:** 8 refs web-verified (adversarial). 3 fixed: ASA title → "ASA: Training-Free
  Representation Engineering for Tool-Calling Agents"; task-drift title → "Get My Drift? Catching LLM
  Task Drift with Activation Deltas"; corrigibility author order. ActAdd keeps the original (widely-cited)
  title. 0 remaining blockers.
- **Overclaim audit:** AUROC=1.0 is reported as a ceiling with capacity ruled out and the lexical
  caveat stated; steering claim scoped to headroom actions; cross-model on 2 families (Llama/Mistral
  gated, noted); simulated/white-box stated.
