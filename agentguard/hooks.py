"""
Live activation hook — the deployable path for L2's internal commitment signal.

In the benchmark, ActionContext.internal_commit_signal is filled from the published
per-action measurements. In a real deployment (defender owns the open weights), you
register a forward hook at the late action-commitment layer (depth-relative ~80-98%;
L59/L63 on Qwen3.6-27B, L26 on Llama-3.1-8B, L32 on Mistral-Small-24B per the
published cross-model results) and compute, at the tool-name decision position, the
logit-lens commit-vs-safe gap. That single scalar is the detector.

`commit_gap` below is the real computation (pure-python, zero-dep, unit-tested). A
concrete `LiveCommitProbe` needs the model loaded (GPU / white-box) — the wiring is
documented in the class; only the model load is environment-dependent.
"""
from __future__ import annotations

from typing import Sequence


def _matvec_row(hidden: Sequence[float], w_row: Sequence[float]) -> float:
    return sum(h * w for h, w in zip(hidden, w_row))


def commit_gap(hidden_late: Sequence[float],
               unembed_rows: dict,
               commit_token_ids: Sequence[int],
               safe_token_ids: Sequence[int]) -> float:
    """
    Logit-lens commit-vs-safe gap at one position.

      hidden_late:      the residual-stream vector at the late layer (list of floats)
      unembed_rows:     {token_id -> unembedding row (list of floats, same dim)} for the
                        commit and safe token ids (the tool-name first tokens)
      commit_token_ids: first-token ids of the irreversible tool name(s) (e.g. "send")
      safe_token_ids:   first-token ids of the safe tool name(s) (e.g. "get")

    Returns max logit over commit tokens minus max logit over safe tokens. High = the
    model is internally committed to the irreversible action. This is the real published
    signal (gap_l59 in data/real_brake_signal.json is exactly this, measured on Qwen).
    """
    def best(ids):
        return max(_matvec_row(hidden_late, unembed_rows[i]) for i in ids)
    return best(commit_token_ids) - best(safe_token_ids)


class LiveCommitProbe:
    """
    Deployable wiring (white-box; requires defender-owned / open weights).

    Usage sketch (real model, GPU):

        probe = LiveCommitProbe(model, tokenizer, late_layer=59,
                                commit_tool="send_transaction", safe_tool="get_balance")
        # during the agent's tool-call decode step, at the tool-name position:
        ctx.internal_commit_signal = probe.measure(hidden_states_at_late_layer)

    The hook registration (model.model.layers[late_layer].register_forward_hook) and the
    unembedding (model.lm_head.weight rows for the commit/safe first-tokens) are standard;
    `commit_gap` does the math. The brake actuator stays deterministic at the tool-call
    boundary (see actuate.py) — the probe only fills the signal.
    """
    def __init__(self, model=None, tokenizer=None, late_layer: int = 59,
                 commit_tool: str = "send_transaction", safe_tool: str = "get_balance"):
        self.model = model
        self.tokenizer = tokenizer
        self.late_layer = late_layer
        self.commit_tool = commit_tool
        self.safe_tool = safe_tool

    def measure(self, hidden_late, unembed_rows, commit_ids, safe_ids) -> float:
        return commit_gap(hidden_late, unembed_rows, commit_ids, safe_ids)
