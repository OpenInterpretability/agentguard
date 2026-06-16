# RESULTS — SAE autopsy of the commit point: "granted authorization" is not a native feature

**Date:** 2026-06-16. **Model:** Qwen3.6-27B (bf16, G4). **SAE:** caiovicentino1/qwen36-27b-sae-fullstack,
L59 (TopK, d_sae=40960, k=128; recon relerr 0.58, FVE ~0.66). Prereg: `PREREG_sae_autopsy.md`. We stopped
using the supervised difference-of-means direction and let the model's own SAE features speak. Two runs:
v1 (`agentguard_sae_autopsy.py`) and a structure-matched control (`agentguard_sae_autopsy_matched.py`).
Ledgers: `results/agentguard_sae_autopsy_v1.json`, `results/agentguard_sae_autopsy_matched.json`.

## The automated flag lied; the naming and the matched control tell the truth
Both runs returned `verdict_native: True` (a single SAE feature separates authorized from momentum at
AUROC 1.0, p<0.001 vs a 1000× permutation null). **This flag is misleading** — it only asks "does some
feature separate?", and the **feature-naming** (max-activating context, pre-registered for exactly this)
shows every top separating feature is **surface form**, not semantics:

| run | best feature | what it reads (max-activating context) |
|---|---|---|
| v1 | #3127 | `<\|im_start\|>assistant…<tool_call><function=` — tool-call **scaffold** |
| matched | #4244 | `Files: cache_tmp.dat, backup_201…` — the **file-listing** tool output |

Every other top feature in both runs is likewise surface: tool-call scaffold, JSON schema tokens
(`"parameters": {"type":"object"`, `"required":["path"]`), the `<parameter=…>` format example, turn
layout (`<\|im_end\|>\n<\|im_start\|>user`). **No semantic "user-granted authorization" feature appears
among the top separators in either run.**

## The decisive number: the supervised "authorization direction" FLIPS under structure-matching
The v1 conditions were confounded by conversation structure (authorized = single-turn explicit auth;
momentum = multi-turn tidy→list→flag→"go ahead"). The matched control makes both conditions the **same**
multi-turn scaffold and varies **only the final user turn**: GRANTED (names + authorizes the specific file)
vs FELT (vague "go ahead"). Applying the **same** frozen supervised direction `d` from #9/#10 (no selection,
no fitting):

| setting | supervised `d` AUROC (authorized vs momentum) |
|---|---|
| v1 (structure NOT matched) | **0.838** |
| matched (structure matched) | **0.08** — it does not weaken, it **inverts** |

The same direction gives near-opposite answers depending on prompt structure. A direction that measured
*granted authorization* would not flip when you hold authorization fixed-in-meaning and only change the
conversation format. **The "authorization direction" of #9/#10 is substantially a surface-structure
artifact.**

## Conclusion (H_0 supported)
Unsupervised, the model's commit-point dictionary is dominated by **surface-form features**
(scaffold / schema / file-list / turn-layout); there is **no native monosemantic "granted-authorization"
feature** among the top separators, and the supervised direction that appeared to measure authorization is
structure-confounded (flips 0.84→0.08 under matching). This **deepens paper #10's "felt, not granted"**:
the internal signal does not merely track *felt* authorization — it substantially tracks *surface form*,
and the apparent granted/felt distinction was a structural confound. The commit substrate is
surface-form + plan-coherence, not a represented concept of user-granted authorization.

## Honest scope / what does NOT yet fully close
The granted vs felt conditions still differ in the **text** of the final user turn, so any method (supervised
or SAE) can exploit a **lexical** difference; the permutation null controls for chance, not for this genuine
lexical difference — which is why the best-feature AUROC stays 1.0 even matched (it reads surface/lexical
tokens). The robust, selection-free result is the **supervised-direction flip** (0.84→0.08), plus the
qualitative naming (no semantic feature). To fully isolate *semantics* from *surface/lexical*, the next step
is **lexically-matched counterfactual pairs** (granted vs felt phrased near-identically) and/or
**interchange interventions** — pre-registered as the follow-up. One model, one locus (L59), one domain;
SAE FVE ~0.66 (a mediocre late-layer SAE — a stronger SAE could surface features this one misses).

## Bottom line
Pointing the microscope (the SAE) instead of the ruler (the supervised direction) overturns the clean
reading of the authorization direction: it is structure-confounded, and the model has no native
monosemantic feature for "the user granted this." The result is positive and novel — it reframes the arc's
agent-safety findings as a fact about the model's *representational ontology* (surface-form + plan-coherence
at the commit), not about a faulty monitor.

---

## Counterfactual cross-lexical test + feature naming — H_0 confirmed (2026-06-16)
The matched run left a caveat: granted/felt still differed in the user-turn TEXT, so a separator could be
lexical. We ran a 2×2 (authorization × two disjoint lexical families A/B, structure-matched) and the
selection-free **cross-lexical-family generalization** test (`agentguard_sae_counterfactual.py`):

| | within (selection-inflated) | **cross-family (held-out)** |
|---|---|---|
| best SAE feature | A 1.0 · B 1.0 | **A→B 0.50** (lexical shortcut of A does not transfer) · **B→A 0.99** |
| supervised d (trained on cells) | A 1.0 · B 0.99 | A→B 0.76 · B→A 1.0 |
| pooled best feature (granted A+B vs felt A+B) | — | AUROC 0.998, perm-p < 0.001 |

The asymmetry (A→B collapses, B→A + pooled transfer) suggested a paraphrase-invariant feature. **Naming it
settled the question** (`agentguard_sae_name.py`): the "invariant" features are **tool-call format/scaffold**,
not authorization:
- feat 34355 (pooled): max-activates on `function=example_function_name><parameter=example_parameter_` (the
  tool-call format boilerplate in the system prompt).
- feat 10017 (transfers B→A): `<tool_call>\n<function=` (scaffold).
- feat 1574 (A-only): `<tool_call>\n<function=example_function_name>` (format boilerplate).

(Our specific worry that the invariant signal was an em-dash punctuation confound was **wrong** — it is
scaffold/format, not punctuation. The conclusion held for a different reason.)

**Verdict — H_0, robust.** Across all framings, every separator of granted vs felt is **surface form** —
conversation structure (matched control), user-turn lexicon (A→B collapse), or tool-call-scaffold activation
modulated by context (the pooled "invariant" feature). **No native monosemantic "user-granted authorization"
feature exists at L59.** The supervised #9/#10 direction is a structural artifact (flips 0.84→0.08 under
matching). The model commits on surface form + plan-coherence; *authorization-as-granted is not a represented
concept.* This deepens paper #10: the internal signal does not even track *felt* authorization semantically —
it tracks form. Ledgers: `agentguard_sae_counterfactual.json`, `agentguard_sae_naming.json`.
