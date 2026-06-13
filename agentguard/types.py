"""Core types shared across the four layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Origin(str, Enum):
    """Where the harmful intent originates — the axis incumbents miss."""
    INPUT = "input"    # prompt injection / poisoned tool output (untrusted data drives the action)
    MODEL = "model"    # misalignment formed INSIDE the model from clean/trusted context
    BENIGN = "benign"  # legitimate, trusted-authorized action (control — must NOT be blocked)


class Decision(str, Enum):
    ALLOW = "allow"
    REDIRECT = "redirect"    # block the irreversible action, substitute a safe read-only one
    ESCALATE = "escalate"    # hold for human confirmation
    BLOCK = "block"          # hard block, no substitute

    @property
    def rank(self) -> int:  # strongest decision wins when layers disagree
        return {"allow": 0, "redirect": 2, "escalate": 3, "block": 4}[self.value]


@dataclass
class Step:
    """One step of the agent transcript."""
    role: str            # system | user | assistant | tool
    content: str
    source: str          # "system" | "user" | "tool:<name>" | "assistant"
    trusted: bool        # is this content from a trusted source?
    step_id: int = 0


@dataclass
class ToolCall:
    name: str
    args: dict = field(default_factory=dict)


@dataclass
class ActionContext:
    """Everything a layer needs to judge a proposed tool call."""
    transcript: list           # list[Step]
    action: ToolCall
    # dataflow from the agent interpreter: ids of steps the action causally depends on
    depends_on: list = field(default_factory=list)
    # the task the agent was legitimately authorized (by a trusted source) to perform
    authorized_task: str = ""
    # is the *committed* action consistent with the trusted authorization? (semantic)
    authorized: bool = True
    # model-internal commitment signal = late-layer logit-lens commit-vs-safe gap.
    # Real published values when available (see data/real_brake_signal.json); None if no hook.
    internal_commit_signal: Optional[float] = None
    meta: dict = field(default_factory=dict)


@dataclass
class LayerVerdict:
    layer: str
    decision: Decision
    reason: str
    redirect_to: Optional[str] = None
    confidence: float = 1.0

    @property
    def caught(self) -> bool:
        return self.decision is not Decision.ALLOW


@dataclass
class FirewallVerdict:
    decision: Decision
    redirect_to: Optional[str]
    triggered_by: list           # list[str] layer names that flagged
    layers: list                 # list[LayerVerdict], all layers

    @property
    def caught(self) -> bool:
        return self.decision is not Decision.ALLOW
