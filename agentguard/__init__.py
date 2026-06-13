"""
AgentGuard — a defense-in-depth action firewall for tool-using agents.

Four independent layers, each covering the others' blind spots:
  L0  policy        — deterministic allowlist / spend-limit / irreversibility   (policy.py)
  L1  provenance    — CaMeL-style taint: does the action derive from untrusted data? (provenance.py)
  L2  intent brake  — model-internal: is the agent committed to an UNAUTHORIZED      (intent.py)
                      irreversible action? grounded in the published circuit-breaker
                      data (Zenodo DOI 10.5281/zenodo.20679287, eval 88/88).
  L3  actuation     — block / redirect-to-safe / escalate-to-human                (actuate.py)

The thesis: L0/L1 + text classifiers are structurally BLIND to *model-origin* harm
(an agent that, from clean/trusted context, internally commits to an irreversible
action nobody authorized). Only the model-internal layer (L2) catches it. The union
of layers dominates any single incumbent. See bench/ (AgentActionBench).
"""
from .types import Origin, Decision, Step, ToolCall, ActionContext, LayerVerdict, FirewallVerdict
from .policy import PolicyConfig, policy_layer, IRREVERSIBLE, SAFE_ALTERNATIVE
from .provenance import provenance_layer
from .intent import IntentConfig, intent_layer, brake_efficacy, real_signal
from .actuate import actuate
from .firewall import Firewall, FirewallConfig

__all__ = [
    "Origin", "Decision", "Step", "ToolCall", "ActionContext", "LayerVerdict", "FirewallVerdict",
    "PolicyConfig", "policy_layer", "IRREVERSIBLE", "SAFE_ALTERNATIVE",
    "provenance_layer", "IntentConfig", "intent_layer", "brake_efficacy", "real_signal",
    "actuate", "Firewall", "FirewallConfig",
]
__version__ = "0.1.0"
