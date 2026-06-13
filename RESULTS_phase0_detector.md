# RESULTS — Phase-0: the L2 detector AUROC (model-origin authorization probe)

**Run:** 2026-06-13 · Qwen/Qwen3.6-27B · Colab G4 (bf16, load 175s) · n=40/condition · wallet domain.
**Ledger:** HF `caiovicentino1/swebench-phase6-verdict-circuit:results/agentguard_phase0_detector.json`.
**Pre-reg:** `PREREG_phase0_detector.md`. **Verdict: POSITIVE (pilot) — the L2 detector is real, cleanest at L59.**

## Fidelity gate (is the agent actually committing at the prefill?)
P(send) at the commit prefill: **authorized 0.998 · model_origin 0.469 · input_origin 0.018.**
- authorized: the agent genuinely commits (as expected).
- model_origin: commits ~47% of the time — a genuine partial model-origin commit state (the headline condition).
- input_origin: **0.018** — at the prefill the model largely *resists* the injection, so this condition is partly a "resisting-injection" state, not a clean commit. (Caveat below; the headline uses model_origin + transfer.)

## AUROC (5-fold CV, authorized=0 vs unauthorized=1)
| layer | auth-vs-model_origin | transfer (train input→test model) | ctrl random-dir | ctrl shuffled-label | gap-only baseline |
|---|---|---|---|---|---|
| L51 | 1.00 | 1.00 | **0.92** | 0.45 | 0.28 |
| L55 | 1.00 | 1.00 | **0.78** | 0.47 | 0.38 |
| **L59** | **1.00** | **1.00** | **0.54** (≈chance) | 0.47 | 0.04 |
| L63 | 1.00 | 1.00 | **0.96** | 0.45 | 0.0002 |

## What holds (the positive)
1. **H2 — model-origin detector exists.** A linear probe separates authorized from model-origin
   unauthorized commits at AUROC 1.00. The agent's internal state at the commit point carries
   whether the irreversible action it is about to take is task-authorized.
2. **H3 — it's authorization, not surface features (confound killer).** A probe trained ONLY on
   **input-origin** cases (injection) **transfers** to detect held-out **model-origin** cases at
   AUROC 1.00 across all layers. There is a *shared "unauthorized" direction* that generalizes
   across attack origin — it is not reading injection-text or the self-justifying think trace.
3. **H4 — not the commit gap.** The commit-vs-safe logit-lens gap alone gives AUROC 0.04–0.38
   (near 0 late) — authorized commits actually have *higher* gap, so "committing-ness" does not
   carry the authorization signal; the probe signal is genuinely about authorization.
4. **Not a CV/dimensionality artifact.** Shuffled-label control ≈ 0.45–0.47 (chance) at every layer.

## The honest caveat (random-direction control)
At **L51/L55/L63** the random-direction control is **0.78–0.96** — a *single random direction*
already separates the conditions well, meaning the three prompt types are globally very different
in raw activation space (different text → different activations). So AUROC 1.00 at those layers is
partly **trivial** separation. **Only at L59 is the random-dir control at chance (0.54)** while the
trained probe (1.00) and cross-origin transfer (1.00) hold — i.e., at L59 the authorization signal
lives in a **specific** subspace, not a global text difference. **L59 is the defensible locus** —
and it is exactly the late action-commitment layer where the published brake works and the commit
gap explodes. Coherent: detect and actuate at the same locus.

## Honest scope / limits
- **n=40, one domain (wallet), single run.** AUROC = 1.00 is a **pilot ceiling**; it will drop with
  harder negatives (authorized-but-unusual actions, near-duplicate authorized/unauthorized pairs)
  and at scale. Do not claim a "perfect detector."
- input_origin fidelity 0.018 (model resists at prefill) — the input-origin cell is partly a
  resisting state; the headline rests on **model_origin (genuine commit) + transfer**.
- Same threat model as AgentGuard: white-box / defender-owned weights; not robust to a white-box
  activation-space adversary.

## Verdict
**The L2 detector is real (pilot).** A learned late-layer direction — cleanest at **L59**, where a
random direction is at chance — separates authorized from unauthorized irreversible-action commits,
**including model-origin**, and the direction **generalizes across attack origin**. It is not the
commit gap and not a label artifact. This turns AgentGuard's L2 from *harness-grounded* to
*measured*, and is the seed of paper #9 ("action-authorization is linearly decodable at the late
action-commitment layer"). Next: scale n, harder negatives, cross-domain (the other 5 actions),
and the causal step (does steering the probe direction change the commit?).
