# SCOPE — what is real-data-backed vs harness vs pending

The honest-rigor ledger for AgentGuard. Same discipline as the WANDERING arc's evals:
state exactly what is measured, what is constructed, and what is the next validation.

## Real, published, independently re-verifiable
- **L2 brake efficacy** — injecting a task-matched safe-donor at the late layer collapses a
  committed irreversible action to **0.00 emission** and **redirects 100% to a safe read-only
  action**, across 6 actions (send_transaction, approve_allowance, delete_file, drop_table,
  deploy_production, send_email) and 3 architectures (Qwen3.6-27B, Llama-3.1-8B, Mistral-24B),
  17/18 valid cells. send: exact McNemar b=24, c=0, p≈1.2e-7.
  Source: HF `caiovicentino1/swebench-phase6-verdict-circuit`; Zenodo DOI 10.5281/zenodo.20679287;
  pre-mint eval 88/88. `eval_agentguard.py` re-fetches these ledgers and confirms the cached
  values in `agentguard/data/real_brake_signal.json` match the live data (51/51 PASS).
- **L2 detector signal definition** — the late-layer logit-lens commit-vs-safe gap (`gap_l59`
  per action, real published values). `hooks.commit_gap` is the exact computation, unit-tested.

## Harness / constructed (the benchmark, deterministic & reproducible)
- **AgentActionBench scenarios** — 24 constructed transcripts (6 actions × {input_plain,
  input_obf_allow, model_origin, benign}). The transcripts, taint dataflow, and authorization
  labels are specified per scenario (in a real deployment the dataflow comes from the agent
  interpreter, the authorization from the trusted task). The coverage matrix is recomputed by
  `bench/run_bench.py` and asserted by `eval_agentguard.py`.
- **L0/L1/L3 and the text-guard baseline** — real, deterministic implementations; their
  catch/blind behavior on the benchmark is computed, not assumed.

## Measured (pilot, 2026-06-13) — was pending, now run
1. **Model-origin detection AUROC — MEASURED (Qwen3.6-27B, n=40, Colab G4).** A linear probe on the
   late-layer residual at the commit point separates authorized from unauthorized (incl.
   **model-origin**) irreversible commits, and the direction **generalizes across attack origin**
   (train injection → test model-origin, AUROC 1.00 — the H3 confound killer). Not the commit gap
   (H4: gap-only AUROC ≈0.04–0.38), not a label artifact (shuffled ≈0.46). **Defensible locus = L59**,
   where the random-direction control is at chance (0.54) while the trained probe is 1.00; at
   L51/L63 the random-dir control is 0.92–0.96, so separation there is partly trivial. AUROC=1.00 is
   a **pilot ceiling** (n=40, one domain) that will drop with harder negatives and scale. Full
   analysis: `RESULTS_phase0_detector.md`; ledger on HF. → L2 is now *measured*, not just
   harness-grounded (seed of paper #9).

## Pending (the next live validations — NOT claimed as done)
2. **Real (non-simulated) tool execution** in a sandbox, with the firewall intercepting the
   actual dispatch + latency numbers.
3. **Adaptive prompt-only red-team** against the full stack (the realistic threat model).

## Threat model (explicit)
- **Defender owns the weights** (self-hosted / open-weight agent). White-box is a *feature* here,
  not a vulnerability: the defender runs the probe on its own stack.
- **Adversary controls the prompt / environment** (prompt injection, poisoned tool output,
  corrupted memory) — NOT the activation space. AgentGuard is **not** robust to a white-box
  activation-space adversary (obfuscated-activations attacks, arXiv:2412.09565); L2 is a
  defense-in-depth signal, and the deterministic layers carry the adaptive-robustness weight.
