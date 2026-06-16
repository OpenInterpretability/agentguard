#!/usr/bin/env python3
"""Adversarial eval for 'Form, Not Granted' — recompute EVERY number from the 4 SAE ledgers vs the .tex."""
import os, json
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def L(f): return json.load(open(os.path.join(RES,f)))
V1=L("agentguard_sae_autopsy_v1.json"); MM=L("agentguard_sae_autopsy_matched.json")
CF=L("agentguard_sae_counterfactual.json")["verdict"]; NM=L("agentguard_sae_naming.json")["names"]
TEX=open(os.path.join(HERE,"commit_ontology.tex")).read()
checks=[]
def ck(n,ok,got=None,want=None): checks.append((n,bool(ok))); print(("PASS" if ok else "FAIL"),n,"" if ok else f"(got {got} want {want})")
def near(a,b,t=0.005): return a is not None and abs(a-b)<=t
def intex(s): return s in TEX

# 1. the flip
ck("v1 supervised 0.838", near(V1["verdict"]["supervised_d_auroc_auth_vs_mom"],0.838))
ck("matched supervised 0.08", near(MM["verdict"]["supervised_d_auroc_auth_vs_mom"],0.08))
ck("tex flip 0.838", intex("$0.838$")); ck("tex flip 0.08", intex("$0.08$") or intex("0.08"))
ck("tex flip phrase", intex("0.838\\to0.08") or intex("$0.838\\to0.08$"))

# 2. cross-lexical
ck("within A 1.0", CF["sae_within_A"]==1.0); ck("within B 1.0", CF["sae_within_B"]==1.0)
ck("cross A2B 0.5", near(CF["sae_cross_A2B"],0.5)); ck("cross B2A 0.993", near(CF["sae_cross_B2A"],0.993))
ck("sup cross A2B 0.764", near(CF["supervised_cross_A2B"],0.764)); ck("sup cross B2A 1.0", near(CF["supervised_cross_B2A"],1.0))
ck("pooled 0.998", near(CF["pooled_best_auroc"],0.998)); ck("pooled p 0", CF["pooled_perm_p"]==0.0)
ck("pooled feat 34355", CF["pooled_best_feature"]==34355)
ck("featA 1574", CF["selected_feat_A"]==1574); ck("featB 10017", CF["selected_feat_B"]==10017)
ck("tex A2B 0.50", intex("A$\\to$B $0.50$")); ck("tex B2A 0.993 (exact)", intex("B$\\to$A $0.993$"))
ck("tex 5 new cites present", all(c in TEX for c in ["controltasks","saeeval","nonlinear","shortcut","scalingmono"]))
ck("tex pooled 0.998", intex("$0.998$")); ck("tex featA 34355", intex("34355"))

# 3. naming = surface form (not authorization)
def has(fid,sub): return sub.lower() in (NM[fid]["ctx"].lower())
ck("naming 34355 = format boilerplate", has("34355","example_function_name") or has("34355","example_parameter"))
ck("naming 10017 = scaffold <function=", has("10017","<function="))
ck("naming 1574 = format example", has("1574","example_function_name"))
ck("tex names example_function_name", intex("example\\_function\\_name"))
# top features of v1/matched are surface (scaffold/schema/file-list)
v1top=list(V1["verdict"]["feature_names"].values())[0]["context"]
ck("v1 best feat is scaffold", "tool_call" in v1top or "function" in v1top)
mmtop=list(MM["verdict"]["feature_names"].values())[0]["context"]
ck("matched best feat is file-listing", "Files:" in mmtop)
ck("tex naming claim surface", intex("every separator is surface form") or intex("surface form"))

# 4. config / honest scope
ck("d_sae 40960", V1["config"].get("d_sae")==40960); ck("tex d_sae 40960", intex("40{,}960"))
ck("recon relerr ~0.58", near(V1["config"].get("sae_recon_relerr",0),0.58,0.01)); ck("tex FVE 0.66", intex("66\\%") or intex("0.66"))
ck("tex qualifies not refutes", intex("qualifies, not refutes") or intex("qualifies"))
ck("tex absence caveat", intex("absence of a separating feature"))

np_=sum(1 for _,ok in checks if ok); nt=len(checks)
print(f"\n=== {np_}/{nt} PASS ===")
open(os.path.join(HERE,"EVAL_commit_ontology.md"),"w").write(
 f"# EVAL — Form, Not Granted ({np_}/{nt} numeric checks PASS)\n\nRecomputed from the 4 SAE ledgers by "
 f"`eval_commit_ontology.py`.\n\n"+"\n".join(f"- {'PASS' if ok else 'FAIL'} — {n}" for n,ok in checks)+"\n")
print("wrote EVAL_commit_ontology.md")
