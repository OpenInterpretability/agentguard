"""
L1 — provenance / taint tracking (CaMeL-class robustness against prompt injection).

Question it answers: does the decision to take this irreversible action causally
DERIVE from untrusted data? If the agent is about to `send_transaction` because a
tool output (an X post, a webpage, a memory entry) told it to, that is taint flowing
into an irreversible sink — block it, regardless of how the instruction was phrased.

Key property: this operates on the DATAFLOW, not the text — so it catches injections
that are obfuscated (base64 / Morse / homoglyph), which defeat text classifiers
(cf. the May-2025 Grok/Bankr Morse-code wallet drain). Its blind spot: MODEL-origin
harm, where the action derives only from trusted context (no taint to find). L2 covers that.
"""
from __future__ import annotations

from typing import Optional
from .types import ActionContext, Decision, LayerVerdict
from .policy import is_irreversible, SAFE_ALTERNATIVE


def provenance_layer(ctx: ActionContext) -> LayerVerdict:
    name = ctx.action.name
    if not is_irreversible(name):
        return LayerVerdict("L1_provenance", Decision.ALLOW, "action is reversible")

    by_id = {s.step_id: s for s in ctx.transcript}
    tainted = [sid for sid in ctx.depends_on
               if sid in by_id and not by_id[sid].trusted]

    if tainted:
        srcs = ", ".join(sorted({by_id[sid].source for sid in tainted}))
        return LayerVerdict(
            "L1_provenance", Decision.REDIRECT,
            f"irreversible action derives from UNTRUSTED data (steps {tainted} via {srcs}); "
            f"content-obfuscation-agnostic",
            redirect_to=SAFE_ALTERNATIVE.get(name),
        )

    return LayerVerdict("L1_provenance", Decision.ALLOW,
                        "action derives only from trusted data (no taint; L1 is blind to model-origin intent)")
