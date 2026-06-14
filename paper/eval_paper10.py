#!/usr/bin/env python3
"""Adversarial eval for paper #10 (Felt, Not Granted): recompute EVERY number from the ledgers."""
import os, json, math, re
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def L(f): return json.load(open(os.path.join(RES,f)))
ADV=L("agentguard_realtest_fs_adv.json"); V4=L("agentguard_realtest_fs_real.json"); V5=L("agentguard_realtest_fs_v5.json")
TEX=open(os.path.join(HERE,"felt_not_granted.tex")).read()

def wilson(k,n,z=1.96):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return (round(max(0,c-h),3),round(min(1,c+h),3))
def auroc(pos,neg):
    c=sum((1.0 if p>n else 0.5 if p==n else 0.0) for p in pos for n in neg); return round(c/(len(pos)*len(neg)),3)

checks=[]
def ck(name, ok, got=None, want=None):
    checks.append((name,bool(ok),got,want)); print(("PASS" if ok else "FAIL"), name, "" if ok else f"(got {got} want {want})")
def near(a,b,t=0.02): return a is not None and b is not None and abs(a-b)<=t
def intex(s): return s in TEX

# --- recompute from v5 records ---
recs=V5["records"]
un=[r for r in recs if r.get("deleted") and r["framing"] in ("dead_weight","momentum","urgent_space") and not r.get("auth_gt")]
au=[r for r in recs if r.get("deleted") and r["framing"]=="authorized" and r.get("auth_gt")]
un_s=[r["probe_score"] for r in un if r["probe_score"] is not None]; au_s=[r["probe_score"] for r in au if r["probe_score"] is not None]
probe_fail=sum(1 for r in un if r["probe_allow"]); judge_catch=sum(1 for r in un if not r["judge_allow"]); auth_fp=sum(1 for r in au if not r["probe_allow"])

# 1. calibration / threshold
cal=V5["calibration"]
ck("calib auth 29.98", near(cal["auth"],29.98,0.1)); ck("calib unauth -36.28", near(cal["unauth"],-36.28,0.1))
ck("threshold -3.15", near(cal["thr"],-3.15,0.02)); ck("tex states tau -3.15", intex("-3.15"))
ck("calib identical to v4", near(cal["thr"],V4["calibration"]["thr"],1e-6))

# 2. easy framings = 0 (adv)
for c in ("injected","goal_pressure","over_eager"):
    ck(f"easy {c} rate 0", ADV["verdict"]["delete_rate_per_cond"][c]==0.0)
ck("adv NPC 12 -> 0/12", ADV["config"]["n_per_cond"]==12); ck("tex says 0/12 each", intex("$0/12$ each"))

# 3. elicitation rates (v5)
pf=V5["verdict"]["per_framing"]
ck("momentum 18/18", pf["momentum"]["n"]==18 and pf["momentum"]["n_deleted"]==18 and pf["momentum"]["delete_rate"]==1.0)
ck("dead_weight 3/18=0.167", pf["dead_weight"]["n_deleted"]==3 and near(pf["dead_weight"]["delete_rate"],0.167,0.005))
ck("urgent_space 0/12", pf["urgent_space"]["n_deleted"]==0 and pf["urgent_space"]["n"]==12)
ck("authorized 12/12", pf["authorized"]["n_deleted"]==12)
ck("tex momentum 18/18", intex("$18/18$")); ck("tex dead_weight 3/18", intex("3/18"))
# v4 single-prompt dead_weight 12/12
ck("v4 dead_weight 12/12", V4["verdict"]["delete_rate_per_cond"]["dead_weight"]==1.0)
ck("tex says 12/12 single fixed prompt", intex("$12/12$ at a single fixed prompt"))

# 4. decisive set
ck("n realistic unauth = 21", len(un)==21 and V5["verdict"]["n_realistic_unauth_deletes"]==21); ck("tex n=21", intex("$n{=}21$"))
ck("unique scores 14", V5["verdict"]["n_unique_unauth_scores"]==14 and len(set(round(s,4) for s in un_s))==14); ck("tex 14 distinct", intex("$14$ distinct internal scores"))
ck("probe fail 21/21", probe_fail==21); ck("judge catch 21/21", judge_catch==21); ck("auth FP 0/12", auth_fp==0 and len(au)==12)
# CIs
w_pf=wilson(21,21); ck("probe fail rate 1.0", probe_fail/len(un)==1.0); ck("probe CI [0.845,1.0]", w_pf==(0.845,1.0), w_pf, (0.845,1.0))
w_jc=wilson(21,21); ck("judge catch CI [0.845,1.0]", w_jc==(0.845,1.0), w_jc)
w_fp=wilson(0,12); ck("FP CI [0,0.243]", w_fp==(0.0,0.243), w_fp, (0.0,0.243))
ck("tex CI 0.845", intex("[0.845,1.0]")); ck("tex FP CI 0.243", intex("[0,0.243]"))

# 5. score stats
import statistics as st
ck("unauth mean 11.87", near(st.mean(un_s),11.87,0.02)); ck("unauth min 7.65", near(min(un_s),7.65,0.02)); ck("unauth max 15.93", near(max(un_s),15.93,0.02))
ck("auth mean 15.17", near(st.mean(au_s),15.17,0.02)); ck("auth min 12.29", near(min(au_s),12.29,0.02)); ck("auth max 18.56", near(max(au_s),18.56,0.02))
ck("tex unauth mean 11.87", intex("$11.87$")); ck("tex auth mean 15.17", intex("$15.17$"))

# 6. AUROC
ap=auroc(au_s,un_s); ck("AUROC probe 0.90", near(ap,0.897,0.005), ap); ck("AUROC probe in verdict 0.897", near(V5["verdict"]["auroc_probe_auth_vs_realunauth"],0.897,0.001))
aj=auroc([1.0 if r["judge_allow"] else 0.0 for r in au],[1.0 if r["judge_allow"] else 0.0 for r in un]); ck("AUROC judge 1.0", aj==1.0, aj)
ck("tex AUROC 0.897 (precise, 3x)", TEX.count("0.897")>=3); ck("tex AUROC 1.0 judge", intex("AUROC $1.0$"))
ck("overlap: max unauth > min auth", max(un_s)>min(au_s))

# 7. design counts
ck("v5 60 records", len(recs)==60); ck("tex 60 scenarios", intex("$60$ scenarios"))
disp=set(r["file"] for r in un if r["framing"]=="momentum"); ck("12 disposable filenames", len(disp)>=12 or len(disp)==12, len(disp))
ck("tex 12 disposable x 6", intex("$12$ disposable target filenames $\\times$ $6$ phrasings"))
mult=sum(1 for r in un if r["framing"]=="momentum" and r.get("text","").count("delete_file")>1)
ck("multiple delete_file in some momentum gens", mult>0, mult)

# 8. layer / model
ck("layer 59", V5["config"]["layer"]==59); ck("tex layer 59", intex("layer $59$"))
ck("bf16", V5["config"]["quant"]=="bf16"); ck("tex bf16 no quant", intex("bf16, no quantization"))

np_=sum(1 for _,ok,_,_ in checks if ok); nt=len(checks)
print(f"\n=== {np_}/{nt} PASS ===")
open(os.path.join(HERE,"EVAL_paper10.md"),"w").write(
 f"# EVAL paper #10 — recompute from ledgers\n\n**{np_}/{nt} numeric checks PASS.** Recomputed from "
 f"`results/agentguard_realtest_fs_{{adv,real,v5}}.json` by `eval_paper10.py`.\n\n"
 + "\n".join(f"- {'PASS' if ok else 'FAIL'} — {n}"+("" if ok else f" (got {g} want {w})") for n,ok,g,w in checks)+"\n")
print("wrote EVAL_paper10.md")
