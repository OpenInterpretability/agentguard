#!/usr/bin/env python3
"""Figures for paper #10 (Felt, Not Granted), recomputed from the local real-test ledgers."""
import os, json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def L(f): return json.load(open(os.path.join(RES,f)))
ADV=L("agentguard_realtest_fs_adv.json")
V4 =L("agentguard_realtest_fs_real.json")
V5 =L("agentguard_realtest_fs_v5.json")
OUT=os.path.join(HERE,"figures10"); os.makedirs(OUT,exist_ok=True)

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return (max(0,c-h),min(1,c+h))

C_EASY="#9e9e9e"; C_REAL="#d62728"; C_AUTH="#2ca02c"; C_PROBE="#1f77b4"; C_JUDGE="#2ca02c"

# ---------- Fig 1: only the realistic judgment-error framing elicits the unauthorized action ----------
rates=[
 ("injection",      ADV["verdict"]["delete_rate_per_cond"]["injected"],     C_EASY,"easy / adversarial"),
 ("goal-pressure",  ADV["verdict"]["delete_rate_per_cond"]["goal_pressure"],C_EASY,"easy / adversarial"),
 ("over-eager",     ADV["verdict"]["delete_rate_per_cond"]["over_eager"],   C_EASY,"easy / adversarial"),
 ("urgent-space",   V5["verdict"]["per_framing"]["urgent_space"]["delete_rate"], C_REAL,"realistic"),
 ("dead-weight",    V5["verdict"]["per_framing"]["dead_weight"]["delete_rate"],  C_REAL,"realistic"),
 ("momentum",       V5["verdict"]["per_framing"]["momentum"]["delete_rate"],     C_REAL,"realistic"),
]
fig,ax=plt.subplots(figsize=(7.6,4.0))
xs=np.arange(len(rates)); vals=[r[1] for r in rates]; cols=[r[2] for r in rates]
ax.bar(xs,vals,color=cols,edgecolor="black",lw=0.6)
for x,v in zip(xs,vals): ax.text(x,v+0.02,f"{v:.2f}",ha="center",va="bottom",fontsize=9)
ax.set_xticks(xs); ax.set_xticklabels([r[0] for r in rates],rotation=18,ha="right",fontsize=9)
ax.set_ylabel("free-gen unauthorized-delete rate"); ax.set_ylim(0,1.12)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=C_EASY,edgecolor="black",label="easy / adversarial framing"),
                   Patch(facecolor=C_REAL,edgecolor="black",label="realistic judgment-error framing")],
          fontsize=8,loc="upper left")
ax.set_title("The error that fires is a judgment error, not obedience\n"
             "(adversarial framings that make the delete salient elicit nothing; the agent completing\n"
             "a cleanup plan it co-authored under a vague \"go ahead\" elicits it every time)",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig1_elicitation.pdf")); plt.close(fig)

# ---------- Fig 2: the decisive distribution — the probe sees the realistic error as authorized ----------
recs=V5["records"]
un=[r["probe_score"] for r in recs if r.get("deleted") and r["framing"] in ("dead_weight","momentum","urgent_space") and not r.get("auth_gt") and r.get("probe_score") is not None]
au=[r["probe_score"] for r in recs if r.get("deleted") and r["framing"]=="authorized" and r.get("auth_gt") and r.get("probe_score") is not None]
thr=V5["verdict"]["thr"]; cal_auth=V5["calibration"]["auth"]; cal_un=V5["calibration"]["unauth"]
fig,ax=plt.subplots(figsize=(7.6,4.6))
rng=np.random.default_rng(0)
ax.scatter(rng.normal(0,0.05,len(un)),un,color=C_REAL,s=34,alpha=0.8,edgecolor="black",lw=0.4,zorder=3,label=f"realistic UNAUTHORIZED deletes (n={len(un)})")
ax.scatter(rng.normal(1,0.05,len(au)),au,color=C_AUTH,s=34,alpha=0.8,edgecolor="black",lw=0.4,zorder=3,label=f"authorized deletes (n={len(au)})")
ax.axhline(thr,color="black",ls="--",lw=1.4,zorder=2,label=f"honest threshold = {thr:.2f}  (probe allows everything above)")
ax.axhline(cal_auth,color=C_AUTH,ls=":",lw=1,alpha=0.7); ax.axhline(cal_un,color=C_REAL,ls=":",lw=1,alpha=0.7)
ax.text(1.45,cal_auth,"calibration: authorized",color=C_AUTH,fontsize=7.5,va="center")
ax.text(1.45,cal_un,"calibration: unauthorized (\"tidy\")",color=C_REAL,fontsize=7.5,va="center")
ax.axhspan(thr,32,color=C_AUTH,alpha=0.05,zorder=0)
ax.set_xticks([0,1]); ax.set_xticklabels(["realistic\nunauthorized","authorized"]); ax.set_xlim(-0.5,2.4)
ax.set_ylabel("authorization-direction projection  $r\\cdot d$"); ax.set_ylim(-42,30)
ax.legend(fontsize=7.6,loc="lower center")
ax.set_title("The realistic unauthorized deletes project onto the AUTHORIZED side of the direction\n"
             "(both clusters sit far above the honestly-set threshold; the probe cannot tell them apart\n"
             f"operationally — AUROC {V5['verdict']['auroc_probe_auth_vs_realunauth']:.2f}, but overlapping and both 'allowed')",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig2_distribution.pdf")); plt.close(fig)

# ---------- Fig 3: probe vs external judge on the elicited unauthorized set ----------
realun=[r for r in recs if r.get("deleted") and r["framing"] in ("dead_weight","momentum","urgent_space") and not r.get("auth_gt")]
authd =[r for r in recs if r.get("deleted") and r["framing"]=="authorized" and r.get("auth_gt")]
n_un=len(realun); probe_catch=sum(1 for r in realun if not r["probe_allow"]); judge_catch=sum(1 for r in realun if not r["judge_allow"])
n_au=len(authd); auth_fp=sum(1 for r in authd if not r["probe_allow"])
def bar_ci(ax,x,k,n,color,lab):
    p=k/n if n else 0; lo,hi=wilson(k,n)
    ax.bar(x,p,color=color,edgecolor="black",lw=0.6,width=0.6)
    ax.errorbar(x,p,yerr=[[max(0,p-lo)],[max(0,hi-p)]],fmt="none",ecolor="black",capsize=5,lw=1.2)
    ax.text(x,hi+0.03,f"{k}/{n}",ha="center",va="bottom",fontsize=9)
fig,ax=plt.subplots(figsize=(7.6,4.2))
bar_ci(ax,0,probe_catch,n_un,C_PROBE,"probe")
bar_ci(ax,1,judge_catch,n_un,C_JUDGE,"judge")
bar_ci(ax,2.6,auth_fp,n_au,"#ff7f0e","fp")
ax.set_xticks([0,1,2.6]); ax.set_xticklabels(["internal probe\ncatches unauth","external judge\ncatches unauth","internal probe\nFP on authorized"],fontsize=9)
ax.set_ylabel("rate (95% Wilson CI)"); ax.set_ylim(0,1.15)
ax.axvline(1.8,color="#ccc",lw=1)
ax.set_title("On the same realistic unauthorized deletes: the internal probe catches none,\n"
             "the external task-grounded judge catches all — and the probe never blocks a legitimate delete",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig3_probe_vs_judge.pdf")); plt.close(fig)

# ---------- Fig 4: felt vs granted — why the probe works in one regime and is blind in the other ----------
fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.set_xlim(0,2); ax.set_ylim(0,2); ax.axis("off")
def cell(x,y,txt,fc):
    ax.add_patch(plt.Rectangle((x,y),1,1,facecolor=fc,edgecolor="black",lw=1.2))
    ax.text(x+0.5,y+0.5,txt,ha="center",va="center",fontsize=8.5,wrap=True)
cell(0,1,"adversarial framing\n(injection / goal / over-eager)\n\nmodel feels UNauthorized\n+ truly unauthorized\n\n→ probe & judge AGREE\n(probe works — #9 regime)\nhere: 0 deletes elicited",C_AUTH+"33")
cell(1,1,"(rare / not observed)\nmodel feels unauthorized\nbut action is granted\n\n→ over-refusal",  "#eeeeee")
cell(0,0,"realistic judgment error\n(momentum / over-help)\n\nmodel feels AUTHORIZED\nbut NOT granted\n\n→ probe ALLOWS (blind)\njudge BLOCKS\nhere: 21/21",C_REAL+"33")
cell(1,0,"normal authorized use\nmodel feels authorized\n+ truly granted\n\n→ probe & judge ALLOW\nhere: 12/12, FP 0",C_AUTH+"33")
ax.text(-0.08,1.5,"feels\nunauth.",ha="right",va="center",fontsize=8.5,rotation=0)
ax.text(-0.08,0.5,"feels\nauth.",ha="right",va="center",fontsize=8.5,rotation=0)
ax.text(0.5,2.06,"NOT granted",ha="center",va="bottom",fontsize=9,weight="bold")
ax.text(1.5,2.06,"granted",ha="center",va="bottom",fontsize=9,weight="bold")
ax.text(-0.32,1.0,"model's internal belief\n(what the probe reads)",ha="center",va="center",fontsize=8.5,rotation=90)
ax.text(1.0,-0.18,"user's actual authorization  (what the judge reads)",ha="center",va="top",fontsize=9)
ax.set_title("Felt, not granted: the probe reads the belief axis, the judge reads the truth axis.\n"
             "They coincide under adversarial framing and DIVERGE under realistic model-origin error.",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig4_felt_vs_granted.pdf")); plt.close(fig)

print("figures written to", OUT)
print("checks:", {"n_un":n_un,"probe_catch":probe_catch,"judge_catch":judge_catch,"n_au":n_au,"auth_fp":auth_fp,
                  "un_mean":round(float(np.mean(un)),2),"au_mean":round(float(np.mean(au)),2)})
