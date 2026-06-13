"""
The AgentGuard firewall: runs the four layers as independent signals and combines them.

    fw = Firewall()
    verdict = fw.check(action_context)   # -> FirewallVerdict
    if verdict.caught: ...               # block / redirect_to / escalate

Defense-in-depth: a harmful action is caught if ANY layer flags it. Because the layers
are independent, each covers the others' blind spots — and only the model-internal layer
(L2) covers MODEL-ORIGIN harm. Set include_text_guard=True to additionally run the
incumbent text-classifier baseline (off by default; used by the benchmark for comparison).
"""
from __future__ import annotations

from typing import Optional
from .types import ActionContext, FirewallVerdict
from .policy import PolicyConfig, policy_layer
from .provenance import provenance_layer
from .intent import IntentConfig, intent_layer
from .baselines import text_guard
from .actuate import actuate


class FirewallConfig:
    def __init__(self,
                 policy: Optional[PolicyConfig] = None,
                 intent: Optional[IntentConfig] = None,
                 use_policy: bool = True,
                 use_provenance: bool = True,
                 use_intent: bool = True,
                 include_text_guard: bool = False,
                 escalate_on_block: bool = True):
        self.policy = policy or PolicyConfig()
        self.intent = intent or IntentConfig()
        self.use_policy = use_policy
        self.use_provenance = use_provenance
        self.use_intent = use_intent
        self.include_text_guard = include_text_guard
        self.escalate_on_block = escalate_on_block


class Firewall:
    def __init__(self, config: Optional[FirewallConfig] = None):
        self.config = config or FirewallConfig()

    def layer_verdicts(self, ctx: ActionContext):
        c = self.config
        out = []
        if c.include_text_guard:
            out.append(text_guard(ctx))
        if c.use_policy:
            out.append(policy_layer(ctx, c.policy))
        if c.use_provenance:
            out.append(provenance_layer(ctx))
        if c.use_intent:
            out.append(intent_layer(ctx, c.intent))
        return out

    def check(self, ctx: ActionContext) -> FirewallVerdict:
        return actuate(self.layer_verdicts(ctx), escalate_on_block=self.config.escalate_on_block)
