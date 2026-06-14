# RESULTS — H1: steering-control does NOT survive the felt-authorized error (bf16/G4)

**Date:** 2026-06-14. **Model:** Qwen3.6-27B (bf16, G4). Always-on steering at late layers {55,57,59,61,63}
during free generation on the momentum scenarios (baseline unauthorized-delete ≈ 100%). Frozen direction
`d` identical to #9/#10 (||d||=66.3; residual norm ≈ 220). Pre-reg: `PREREG_steer_felt.md`. Ledger: HF
`results/agentguard_steer_felt.json`.

## Result (n=12 momentum scenarios per condition)
| Condition | unauthorized delete | redirect to safe | incoherent |
|---|---|---|---|
| baseline (coef 0) | 12/12 | 0 | 0 |
| brake −d̂ @10 | **12/12** | 0 | 0 |
| brake −d̂ @20 | **12/12** | 0 | 0 |
| brake −d̂ @40 | **0/12** | **0** | **12** |
| boost +d̂ @20 | 12/12 | 0 | 0 |
| random @20 (matched) | 12/12 | 0 | 0 |
| random @40 (matched) | **12/12** | 0 | **0** |

## Verdict: B (refined) — the direction provides NO usable control in the felt-authorized regime
- **No clean redirect at any strength** (`redirect_safe = 0` everywhere): outcome A (control survives)
  is **falsified**. The brake never makes the agent choose a safe action.
- **Inert at usable strength.** At coef 10 and 20 the brake leaves the unauthorized delete at 12/12,
  identical to baseline. The direction does not move the felt-authorized commit.
- **At high strength it suppresses only by destroying coherence — and that is d-specific.** brake −d̂ @40
  drops the delete to 0 but via 12/12 **incoherent** generations (no parseable tool call), not redirection.
  The matched **random** direction at the same norm (@40) leaves the model fully coherent and still deleting
  12/12 — so the collapse is specific to `d` (rules out generic degradation, outcome C), but **destruction
  is not control**. Pushing hard along −d̂ derails coherent generation rather than steering the action.
- **boost +d̂ sanity:** keeps the delete at 12/12 (the sign/magnitude act as expected on the commit it can
  reach).

## What this means (the combined #9 / #10 / H1 picture)
The authorization direction is a detection-AND-control lever **exactly where the model registers the
authorization conflict** (the adversarial/explicit regime of #9: −d cleanly suppresses and redirects). In
the **felt-authorized** regime (realistic model-origin over-reach), the same direction is **both blind and
inert**:
- **Detection fails** (#10): the probe allows 21/21 unauthorized deletes at the honest threshold.
- **Control fails** (H1): no coefficient steers the commit away cleanly; the brake is inert at usable
  strength and only destroys coherent generation at high strength.

So the realistic error escapes the **entire internal-direction toolkit** — neither the detector nor the
actuator built on `d` catches or redirects it. The only layer that does is the **external, task-grounded
check** (the judge / policy against the explicit user request), which caught 21/21 in #10. This is the
strongest possible empirical case for defense-in-depth: the internal and external monitors do not merely
add coverage, they cover a **regime the internal direction cannot reach at all**.

## Caveats
One model, one domain (file deletion), bf16, one steering recipe (always-on add at five late layers, three
brake magnitudes). A different injection point, a learned steering vector, or layer-by-layer dosing might
behave differently; we tested the natural extension of the #9 recipe. n=12 momentum scenarios (the robust
elicitor). The d-specificity of the high-coef collapse shows `d` is entangled with coherent generation,
not orthogonal to it — itself a minor finding. Honest scope unchanged: this concerns the direction's use as
a control lever in this regime, not a claim that no internal intervention could ever work.

## Bottom line
The open question #10 left — does control survive where detection fails? — is answered: **no.** The
felt-authorized error is invisible to the probe and unreachable by the brake; only an external
task-grounded check covers it. #9 + #10 + H1 together delimit the authorization direction precisely: it
detects and controls where the model knows there is a conflict, and does neither where the model is sincerely
mistaken. Empirical core for a paper #11 on the limits of single-direction agent safety.
