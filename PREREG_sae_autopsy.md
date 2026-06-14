# PRE-REG — SAE autopsy of the commit point: is "granted authorization" a NATIVE feature?

**Date:** 2026-06-14. **Model:** Qwen3.6-27B (bf16, G4). **SAE:** caiovicentino1/qwen36-27b-sae-fullstack,
layer **L59** (TopK, d_sae=40960, k=128) — the exact commit locus of the supervised authorization direction.
**Runner:** `scripts/agentguard_sae_autopsy.py`.

## Motivation
The whole agent-safety arc (#6–#10, H1, H5) was built on a SUPERVISED single-point direction
`d = mean(auth) − mean(unauth)`. That method ALWAYS returns a direction, whether or not the concept is
natively represented — it cannot distinguish "the model represents authorization and d captures it" from
"we projected the human concept of authorization onto whatever variance correlated with our labels." Paper
#10 (felt-not-granted) is suggestive that the concept is IMPORTED: d tracks the authorization the model
*feels* (plan-fit) and is blind to what the user *granted*. We stop forcing a supervised human-concept
direction and let the model's OWN representations (unsupervised SAE features) speak.

## Question
At the token where the agent commits an irreversible action (delete_file), in the model's own ontology
(SAE features), does a feature exist that distinguishes a GRANTED commit from a FELT-but-not-granted one —
or is the decision substrate plan-coherence / momentum / tool-name-induction, with no native
"user-granted-authorization" feature?

## Conditions (commit-token L59 residual → SAE encode)
- **authorized** (granted + felt): user explicitly authorizes deleting a named file → real free-gen commit. n=12.
- **momentum** (felt, NOT granted): the realistic over-reach — agent finishes a cleanup plan it co-authored
  under a vague "go ahead" → real free-gen commit. n=18.
- **tidy_unauth** (reference, prefill): the supervised d's "unauthorized" calibration style ("I'll just
  delete X to tidy") → forced commit. n=12. Anchors where the calibration's notion of "unauthorized" sits.

## Hypotheses (both outcomes are results; honest-negatives discipline)
- **H_a — the concept is NATIVE.** A single SAE feature separates authorized from momentum at AUROC
  comparable to the supervised d (~0.90), well above a permutation null (best-of-40960 features under
  shuffled labels), and its max-activating contexts read as authorization / permission. → an internal
  monitor has a redemption path: find the right *feature*, not the difference-of-means direction.
- **H_0 — the concept is IMPORTED.** No single SAE feature separates authorized from momentum above the
  permutation null (selecting the best of 40960 features gives ~the same AUROC on shuffled labels), i.e. the
  small supervised separation is diffuse / label-driven, not carried by a monosemantic feature; and the top
  features ACTIVE at the commit are plan-coherence / momentum / tool-name-induction / "done", none of which
  is "user-granted authorization". → the alignment-relevant law: **agents commit on plan-coherence, not on a
  represented user-granted goal; authorization-as-granted is not natively represented.** Predicted by #10.

## Analysis (rigor — correct for the 40960-feature selection)
1. **Supervised reference:** recompute `d` at L59 (identical calibration to #9/#10); AUROC(authorized vs
   momentum). No selection — the honest baseline (~0.897 expected).
2. **Best single SAE feature** AUROC(authorized vs momentum), selected over all 40960 features — INFLATED by
   selection.
3. **Permutation null:** shuffle the authorized/momentum labels K=1000×, each time take the best-of-40960
   feature AUROC → null distribution of "best feature under no real signal". p = P(null ≥ real best).
   - real best ≫ null AND ≈ supervised → H_a (a native-ish feature).
   - real best ≈ null → H_0 (no single feature; the separation is supervised-only / diffuse).
4. **Top features by condition:** mean activation per condition; top *shared* features (the commit
   substrate, high in all) and top *differential* (authorized−momentum) features.
5. **Naming:** for the top shared + top differential features, the max-activating token context across all
   scenarios → name each (plan-fit? tool-name induction? done? permission?).
6. **Dynamics (Phase B):** for momentum, the per-token activation trajectory of the top commit features
   across the approval→commit window — does plan-coherence ramp toward the commit?

## Scope
One model, one domain, one locus (L59), n≈14 distinct scenarios (the v5 momentum grid). bf16. SAE
reconstruction error reported as a sanity check that the encode convention is correct. Ledger + raw feature
vectors on HF. This characterizes the model's native decision ontology; it does not claim universality.
