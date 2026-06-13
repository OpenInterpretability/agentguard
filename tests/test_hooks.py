"""Unit test for the live-hook logit-lens commit-gap computation."""
from agentguard.hooks import commit_gap


def test_commit_gap_high_when_committed():
    # hidden aligns with the commit token's unembed row -> positive gap
    hidden = [1.0, 0.0, 0.0]
    unembed = {10: [5.0, 0.0, 0.0],   # commit ("send")
               20: [0.0, 1.0, 0.0]}   # safe ("get")
    g = commit_gap(hidden, unembed, commit_token_ids=[10], safe_token_ids=[20])
    assert g == 5.0


def test_commit_gap_negative_when_safe():
    hidden = [0.0, 1.0, 0.0]
    unembed = {10: [5.0, 0.0, 0.0], 20: [0.0, 4.0, 0.0]}
    g = commit_gap(hidden, unembed, commit_token_ids=[10], safe_token_ids=[20])
    assert g == -4.0


def test_commit_gap_takes_max_over_token_sets():
    hidden = [1.0, 1.0]
    unembed = {1: [1.0, 0.0], 2: [0.0, 3.0], 3: [2.0, 0.0]}
    # commit = max(1*1, 0*1+3*1)=3 over {1,2}; safe = 2 over {3}
    assert commit_gap(hidden, unembed, [1, 2], [3]) == 1.0
