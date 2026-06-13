"""
L0 — deterministic policy gate (the load-bearing outer layer; table stakes).

This is what every production stack already ships (Turnkey / Coinbase AgentKit /
MetaMask+Blockaid / LangGraph interrupt_on): allowlists, spend limits, irreversibility.
It is robust against adaptive adversaries BUT cannot see *intent* — it passes any
irreversible action whose parameters look policy-compliant (allowlisted recipient,
amount under limit). That blind spot is what L1 and L2 cover.
"""
from __future__ import annotations

from typing import Optional
from .types import ActionContext, Decision, LayerVerdict

# Irreversible / hard-to-undo actions across domains (crypto, fs, db, devops, comms).
IRREVERSIBLE = {
    "send_transaction", "transfer", "approve_allowance", "approve",
    "delete_file", "drop_table", "deploy_production", "deploy", "send_email",
}

# The task-matched safe, read-only substitute for each irreversible action
# (matches the published circuit-breaker redirect targets).
SAFE_ALTERNATIVE = {
    "send_transaction": "get_balance",
    "transfer": "get_balance",
    "approve_allowance": "get_balance",
    "approve": "get_balance",
    "delete_file": "list_files",
    "drop_table": "describe_table",
    "deploy_production": "run_tests",
    "deploy": "run_tests",
    "send_email": "save_draft",
}

# arg keys that name the "destination" of an action, for allowlist checks
_TARGET_KEYS = ("to", "recipient", "contract", "spender", "address", "path", "table", "target")


def is_irreversible(name: str) -> bool:
    return name in IRREVERSIBLE


def _target(action) -> Optional[str]:
    for k in _TARGET_KEYS:
        if k in action.args:
            return str(action.args[k])
    return None


class PolicyConfig:
    """allowlist=None disables the allowlist check; spend_limit=None disables it."""
    def __init__(self, allowlist=None, spend_limit=None):
        self.allowlist = set(allowlist) if allowlist is not None else None
        self.spend_limit = spend_limit


def policy_layer(ctx: ActionContext, config: Optional[PolicyConfig] = None) -> LayerVerdict:
    config = config or PolicyConfig()
    name = ctx.action.name
    if not is_irreversible(name):
        return LayerVerdict("L0_policy", Decision.ALLOW, "action is reversible")

    target = _target(ctx.action)
    if config.allowlist is not None and target is not None and target not in config.allowlist:
        return LayerVerdict("L0_policy", Decision.BLOCK,
                            f"target {target!r} not in allowlist")

    amount = ctx.action.args.get("amount")
    if config.spend_limit is not None and isinstance(amount, (int, float)) and amount > config.spend_limit:
        return LayerVerdict("L0_policy", Decision.ESCALATE,
                            f"amount {amount} exceeds spend limit {config.spend_limit}")

    # policy-compliant parameters -> L0 cannot see intent, so it allows
    return LayerVerdict("L0_policy", Decision.ALLOW,
                        "parameters are policy-compliant (L0 cannot inspect intent)")
