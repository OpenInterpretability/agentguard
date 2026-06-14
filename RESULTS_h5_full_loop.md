# RESULTS — H5: the full AgentGuard firewall vs the felt-authorized model-origin error

**Date:** 2026-06-14. CPU-only; the **real** four-layer firewall (`agentguard/`) run over the **real**
captured cases from the v5 run (21 realistic unauthorized deletes + 12 authorized controls), using the
real published `delete_file` commit gap (9.55 ≥ threshold 4.0 → the agent is internally committed). Script:
`exp_h5_full_loop.py`. Ledger: `results/agentguard_h5_full_loop.json`.

## The question
The L2 intent brake fires when the agent is internally **committed** to an irreversible action the trusted
task did **not authorize**. The catch therefore hinges entirely on **where the authorization-consistency
signal comes from**. Paper #10/H1 showed the model's internal authorization signal is **felt**, not
**granted**. So we run the firewall under two sources for that signal:
- **INTERNAL** = the model's own probe (`probe_allow` from #10) — what `intent.py`'s docstring called "the
  deployable version reads from the model's internal task representation."
- **EXTERNAL** = a task-grounded judge (`judge_allow` from #10) — an out-of-model check.

## Result
| Authorization source for L2 | realistic unauthorized CAUGHT | authorized false-positives | caught by |
|---|---|---|---|
| **INTERNAL** (model probe, felt) | **0 / 21** | 0 / 12 | — (firewall ALLOWs all) |
| **EXTERNAL** (task-grounded judge, granted) | **21 / 21** | 0 / 12 | L2_intent (redirect) |

Plus an L1 sanity: a constructed **injection-origin** delete (auth=True, so L2 does not fire) is caught by
**L1_provenance** (tainted dataflow), redirect-to-safe. So L1 covers input-origin and L2-external covers
model-origin.

## What this means (the product statement of felt-vs-granted)
- **With internal authorization, the felt-authorized error passes ALL FOUR layers.** L0 allows it (the
  parameters are policy-compliant — for an open-ended file agent there is no allowlist of every deletable
  file); L1 allows it (model-origin: the action derives only from trusted context, no taint); L2 allows it
  (the model *feels* authorized, so the internal authorization-consistency signal says "authorized"); L3
  has nothing to actuate. Catch 0/21. This is the firewall faithfully inheriting the model's own judgment
  error — the system-level shadow of #10/H1.
- **With external authorization, the union catches 21/21, FP 0/12** — via the L2 brake, whose published
  efficacy (suppress→0.00, redirect→`list_files`) then applies. Authorized controls are correctly allowed
  (judge says authorized → no false positive).
- **Therefore the fix is concrete and shippable:** AgentGuard's L2 authorization-consistency check MUST be
  sourced from an **external, task-grounded check** (the judge / L3 against the explicit user request), NOT
  from the model's internal task representation. The internal commit *detector* (gap_l59) is still real and
  used to know the agent is committed; what must be external is the **granted-vs-felt** judgment. The
  `intent.py` docstring is corrected accordingly and a regression test (`tests/test_h5_felt_authorized.py`)
  locks the finding in.

## Defense-in-depth, demonstrated (not asserted)
The three origins are covered by three different layers, and no single layer covers all:
- **input-origin** (injection): L1 provenance (content-obfuscation-agnostic).
- **model-origin, felt-authorized** (the realistic over-reach): L2 intent **with external authorization**.
- **policy violations** (allowlist/limit): L0.
The realistic model-origin error is in L0's and L1's blind spots and in L2's blind spot *if L2 trusts the
model's felt authorization* — it is covered only by L2 sourced externally. Defense-in-depth here is a
measured necessity.

## Caveats
The 21 realistic cases reuse the v5 capture (n_eff ≈ 14 distinct scenarios). The commit signal is the
published per-action value (the agent did commit in every case). The judge is the same base model (its
perfect score is not a general robustness claim — a sufficiently plausible context could fool it; that is
H4, future work). The injection sanity is a single constructed input-origin case exercising the real L1
code, not an elicitation-rate claim. White-box detector assumption unchanged.

## Bottom line
The full firewall **does** catch the felt-authorized model-origin error the internal probe and brake alone
cannot — **but only when its authorization-consistency signal is external/task-grounded.** That is the
deployable lesson of #10/H1, now demonstrated end-to-end on the real product code, and shipped as a docstring
correction + regression test.
