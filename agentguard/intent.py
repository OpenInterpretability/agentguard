"""
L2 — model-internal intent brake (the novel core; the model-origin blind-spot closer).

Two real components, grounded in the published circuit-breaker work
(Zenodo DOI 10.5281/zenodo.20679287; eval 88/88):

  1. DETECTOR (real signal): the late-layer logit-lens commit-vs-safe gap. When it is
     high, the model is internally COMMITTED to emitting the irreversible action
     (real, measured per action: gap_l59 in data/real_brake_signal.json).
  2. BRAKE / ACTUATOR (real efficacy): injecting a task-matched safe-donor at the late
     layer collapses the committed action to 0.00 emit and redirects 100% to the safe
     read-only action — measured, generation-confirmed, McNemar b=24/c=0 for send.

L2 fires when the agent is internally COMMITTED to an irreversible action that the
TRUSTED task did NOT authorize. This is the only layer that catches MODEL-ORIGIN harm:
for model-origin, provenance is clean (L1 blind) and parameters are policy-compliant
(L0 blind), but the agent self-authorized an irreversible action — visible only in its
internal commitment + the authorization mismatch.

Honest scope: the BRAKE efficacy (suppress->0.00, redirect->safe) is published real data.
The detector's commitment signal (gap_l59) is real published data per action. White-box:
requires defender-owned / open weights.

AUTHORIZATION SOURCING (corrected per paper #10 / H1, DOI 10.5281/zenodo.20685264). `ctx.authorized`
is the granted-vs-felt judgment: did the TRUSTED task actually authorize THIS action. It MUST be
sourced from an EXTERNAL, task-grounded check (the judge / L3 against the explicit user request), NOT
from the model's internal task representation. #10 showed the model's internal authorization signal is
"felt, not granted": under a realistic model-origin judgment error (the agent finishes a cleanup plan it
co-authored under a vague "go ahead"), the internal probe reports "authorized" (felt) and is operationally
blind; H1 showed steering -d does not recover control there either. So the internal signal tells us the
agent is COMMITTED (gap_l59) — but whether the commit is GRANTED must come from outside the model.
Feeding `ctx.authorized` from the internal probe makes the firewall inherit the model's mistake (H5:
0/21 caught); feeding it from the external judge catches 21/21 at FP 0/12. See tests/test_h5_felt_authorized.py.
"""
from __future__ import annotations

import json
import os
from typing import Optional
from .types import ActionContext, Decision, LayerVerdict
from .policy import is_irreversible, SAFE_ALTERNATIVE

_DATA = os.path.join(os.path.dirname(__file__), "data", "real_brake_signal.json")
with open(_DATA) as _fh:
    _REAL = json.load(_fh)


def real_signal(action_name: str) -> Optional[dict]:
    """The real published per-action brake measurements, or None if not measured."""
    return _REAL["actions"].get(action_name)


def brake_efficacy(action_name: str) -> Optional[dict]:
    """Published (suppression, redirect-to-safe) efficacy of the brake for this action."""
    s = real_signal(action_name)
    if s is None:
        return None
    return {
        "suppression": 1.0 - s["brake_emit"],          # 1.0 = fully suppressed
        "redirect_safe_frac": s["redirect_safe_frac"],  # 1.0 = always redirects to safe
        "safe_action": s["safe_action"],
        "n": s["n"],
    }


class IntentConfig:
    """commit_threshold: late-layer gap above which the agent is judged COMMITTED.
    The published commit gaps span ~+6.5..+13.2; safe points are <=~+2.6. A threshold
    of 4.0 cleanly separates committed irreversible actions from non-committed ones."""
    def __init__(self, commit_threshold: float = 4.0):
        self.commit_threshold = commit_threshold


def intent_layer(ctx: ActionContext, config: Optional[IntentConfig] = None) -> LayerVerdict:
    config = config or IntentConfig()
    name = ctx.action.name
    if not is_irreversible(name):
        return LayerVerdict("L2_intent", Decision.ALLOW, "action is reversible")

    signal = ctx.internal_commit_signal
    if signal is None:
        # No live hook / no measured signal -> L2 abstains (defense-in-depth: other layers cover)
        return LayerVerdict("L2_intent", Decision.ALLOW,
                            "no internal commitment signal available (no live hook)", confidence=0.0)

    committed = signal >= config.commit_threshold
    if not committed:
        return LayerVerdict("L2_intent", Decision.ALLOW,
                            f"not internally committed (gap {signal:.1f} < {config.commit_threshold})")

    if ctx.authorized:
        # committed AND authorized by the trusted task -> legitimate, do not brake (no false positive)
        return LayerVerdict("L2_intent", Decision.ALLOW,
                            f"committed (gap {signal:.1f}) but trusted-authorized -> legitimate")

    # committed to an irreversible action the trusted task did NOT authorize ->
    # harmful intent (input- OR model-origin). Apply the brake: redirect to safe.
    eff = brake_efficacy(name)
    safe = SAFE_ALTERNATIVE.get(name)
    detail = ""
    if eff is not None:
        detail = (f"; published brake: {eff['suppression']*100:.0f}% suppression, "
                  f"{eff['redirect_safe_frac']*100:.0f}% redirect->{eff['safe_action']} (n={eff['n']})")
    return LayerVerdict(
        "L2_intent", Decision.REDIRECT,
        f"internal commitment (gap {signal:.1f}) to UNAUTHORIZED irreversible action{detail}",
        redirect_to=safe,
        confidence=min(1.0, signal / 12.0),
    )
