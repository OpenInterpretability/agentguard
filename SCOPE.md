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

## Pending (the next live validations — NOT claimed as done)
1. **Model-origin detection AUROC (live GPU).** The brake's *suppress+redirect* is published-real;
   what a live run adds is the **detector's discrimination** between (a) a legitimately authorized
   irreversible commit and (b) a model-origin / injected unauthorized commit, on fresh Qwen
   activations — i.e., does the late-layer signal separate "authorized" from "self-committed
   unauthorized" with high AUROC? This is the Phase-0 wedge experiment. Harness is ready
   (`hooks.LiveCommitProbe`); only the GPU run is pending.
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
