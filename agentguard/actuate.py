"""
L3 — actuation. Given the per-layer verdicts, decide what to actually do at the
tool-call boundary. The strongest decision wins; for an irreversible action that any
layer flags, the default is a deterministic redirect-to-safe (soft) escalating to a
human hold (hard). The actuation is deterministic — it does not depend on the brittle
steering vector — so it survives at the action boundary even if the detector is noisy.
"""
from __future__ import annotations

from typing import Optional
from .types import Decision, LayerVerdict, FirewallVerdict


def actuate(layer_verdicts, escalate_on_block: bool = True) -> FirewallVerdict:
    triggered = [v for v in layer_verdicts if v.caught]
    if not triggered:
        return FirewallVerdict(Decision.ALLOW, None, [], list(layer_verdicts))

    strongest = max(triggered, key=lambda v: v.decision.rank)
    # pick a redirect target from whichever flagging layer proposed one
    redirect_to: Optional[str] = next((v.redirect_to for v in triggered if v.redirect_to), None)

    decision = strongest.decision
    # A hard BLOCK on an irreversible action is upgraded to ESCALATE if a safe redirect
    # exists (prefer routing the agent somewhere safe / to a human over a dead stop),
    # unless caller wants a hard stop.
    if decision is Decision.BLOCK and redirect_to and not escalate_on_block:
        decision = Decision.REDIRECT

    return FirewallVerdict(
        decision=decision,
        redirect_to=redirect_to if decision is Decision.REDIRECT else redirect_to,
        triggered_by=[v.layer for v in triggered],
        layers=list(layer_verdicts),
    )
