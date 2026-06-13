# AgentGuard

**A defense-in-depth action firewall for tool-using agents — with a model-internal intent brake that closes the *model-origin* blind spot every incumbent shares.**

[![tests](https://img.shields.io/badge/tests-20%20passing-brightgreen)](tests/) [![eval](https://img.shields.io/badge/eval-51%2F51-brightgreen)](eval_agentguard.py) [![brake paper](https://img.shields.io/badge/brake-Zenodo%2010.5281%2Fzenodo.20679287-blue)](https://doi.org/10.5281/zenodo.20679287) [![detector paper](https://img.shields.io/badge/detector-Zenodo%2010.5281%2Fzenodo.20683623-blue)](https://doi.org/10.5281/zenodo.20683623)

```python
from agentguard import Firewall, ActionContext, ToolCall, Step

fw = Firewall()
verdict = fw.check(action_context)      # before the agent executes a tool call
if verdict.caught:
    # verdict.decision in {redirect, escalate, block}; verdict.redirect_to -> a safe read-only action
    ...
```

## Why it exists

Every production agent guardrail — Llama Guard, NeMo, Lakera, Invariant, AEGIS, LangGraph HITL, and every crypto-agent wallet (Coinbase AgentKit, MetaMask+Blockaid, Turnkey, Fireblocks) — gates dangerous tool calls on **text, tool arguments, or deterministic policy**. None read the model's internal state. That leaves two gaps:

1. **Obfuscation** — a text classifier can't read a base64 / Morse / homoglyph injection (the May-2025 Grok/Bankr Morse-code wallet drain).
2. **Model-origin harm** — when an agent, from *clean, trusted context*, internally commits to an irreversible action **nobody authorized** (misalignment, reward-hacking, over-eager "to be safe I'll just delete it"), there is **no untrusted input to taint-track and no malicious argument to match**. The entire deterministic + text stack is structurally blind.

AgentGuard layers four **independent** signals so each covers the others' blind spots — and adds the one layer that catches model-origin harm: the **model-internal intent brake**.

## The four layers

| layer | question | catches | blind to |
|---|---|---|---|
| **L0 policy** (`policy.py`) | are the parameters policy-compliant? | unknown recipient, over-limit | intent |
| **L1 provenance** (`provenance.py`) | does the action derive from *untrusted data*? (CaMeL-style taint) | prompt injection, incl. **obfuscated** (it's dataflow, not text) | model-origin (no taint) |
| **L2 intent brake** (`intent.py`) | is the agent internally **committed** to an **unauthorized** irreversible action? | **model-origin harm**, laundered injection | needs white-box weights |
| **L3 actuation** (`actuate.py`) | what to do? | block · **redirect-to-safe** · escalate-to-human | — |

Both halves of L2 are **measured on real models**, not assumed:

- **The actuator (brake).** Injecting a task-matched safe-donor at a late layer collapses a committed irreversible action to **0.00 emission** and **redirects 100% to a safe read-only action** (`send_transaction → get_balance`), across 6 actions and 3 architectures — McNemar *b*=24/*c*=0 for send, eval 88/88. Paper: [Zenodo 10.5281/zenodo.20679287](https://doi.org/10.5281/zenodo.20679287).
- **The detector.** At the commit point, a single **late-layer authorization direction** separates *authorized* from *unauthorized* irreversible-action commits at **AUROC ≈ 1.0** — and the capacity confound is ruled out (1-D difference-of-means, regularization sweep, PCA-32, commit-state matched; a random direction is at chance at the locus). It is **domain-general** (train on 5 actions, detect the held-out 6th at 1.0), **origin-robust** (train on injection, detect held-out model-origin at 0.89), and the **same direction steered *controls* the commit** (emit range 0.67 vs 0.03 random). It replicates on a second architecture family (gpt-oss-20b MoE). Paper: [Zenodo 10.5281/zenodo.20683623](https://doi.org/10.5281/zenodo.20683623) (*The Authorization Direction*). The live-hook computation is in `hooks.py`.

A behavioral finding from the detector study, on both models: they **obey explicit prohibition** ("do not" → commit 0.00) but **self-commit irreversible actions from a benign task** — model-origin harm is unprompted over-eagerness, the exact gap L2 exists for.

## AgentActionBench — the coverage proof

`python3 bench/run_bench.py` runs 24 scenarios (6 irreversible actions × 4 origin classes):

![coverage](figures/agentactionbench_coverage.png)

```
origin class                         text_guard   L0_policy  L1_provenance  L2_intent   AgentGuard(union)
input-origin (plain)                    100%        100%        100%          100%          100%
input-origin (obfusc.+allowlisted)        0%          0%        100%          100%          100%
MODEL-origin (clean context)              0%          0%          0%          100%          100%   <-- only L2
benign (false-positive ctrl)              0%          0%          0%            0%            0%
```

- The whole deterministic + text stack is **0%** on model-origin harm; only the model-internal layer catches it.
- The union catches **100% of attacks at 0% false positives** on benign authorized actions.

## Install & test

```bash
pip install -e .
python3 -m pytest -q          # 20 passing
python3 eval_agentguard.py    # 51/51 — recomputes the thesis + verifies L2 efficacy vs the live HF ledgers
```

## Honest scope

AgentGuard is **defense-in-depth, not a single robust layer**. The deterministic layers (L0/L1) are load-bearing against adaptive adversaries; L2 is a cheap model-internal signal that uniquely covers model-origin harm. L2 requires **white-box / defender-owned (open) weights** and is not robust to a *white-box activation-space* adversary (obfuscated-activations attacks) — the threat model is a **prompt/environment adversary against a model the defender controls**. Both the brake's suppress/redirect efficacy *and* the detector's AUROC are now **measured on real models** (papers above); the detector's AUROC=1.0 is a ceiling whose *capacity* origin is ruled out but whose *surface-lexical* component is not fully isolated (a minimal-pair tightening remains). Actions in the benchmark are simulated. See `SCOPE.md` and `RESULTS_phase1/2/3` for exactly what is real-data-backed vs harness.

## Research behind L2 (papers + reproducible runs)

The model-internal layer rests on a four-phase study (pre-registered, every number recomputed by an eval from the public HF ledgers):

| phase | result | artifact |
|---|---|---|
| brake (actuator) | 0.00 emit, 100% redirect-to-safe, 6 actions × 3 archs | [Zenodo 20679287](https://doi.org/10.5281/zenodo.20679287) |
| detector measured | AUROC ≈ 1.0, capacity ruled out, cross-action 1.0, cross-origin 0.89 | `PREREG_phase1/2`, `RESULTS_phase1/2` |
| causal (detect=control) | steering range 0.67 vs 0.03 random, bidirectional | `RESULTS_phase1` |
| cross-architecture | gpt-oss-20b replicates (detect 1.0, steer 0.65 vs −0.25) | `RESULTS_phase3` |
| paper | *The Authorization Direction* | [Zenodo 20683623](https://doi.org/10.5281/zenodo.20683623) · `paper/` (eval 35/35) |

## Citation

- The actuator: *Mechanistic Circuit-Breakers Generalize Across Irreversible Agent Actions and Architectures* (Vicentino, 2026, [Zenodo 10.5281/zenodo.20679287](https://doi.org/10.5281/zenodo.20679287)).
- The detector: *The Authorization Direction: A Late-Layer Direction that Detects and Controls an Agent's Commitment to Unauthorized Irreversible Actions, Across Architectures* (Vicentino, 2026, [Zenodo 10.5281/zenodo.20683623](https://doi.org/10.5281/zenodo.20683623)).

Apache-2.0 · [openinterp.org/agentguard](https://openinterp.org/agentguard)
