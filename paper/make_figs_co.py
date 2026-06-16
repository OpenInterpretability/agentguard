#!/usr/bin/env python3
"""Figures for 'Form, Not Granted' (the SAE commit-ontology autopsy), from the verified ledgers."""
import os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def L(f): return json.load(open(os.path.join(RES,f)))
V1=L("agentguard_sae_autopsy_v1.json")["verdict"]
MM=L("agentguard_sae_autopsy_matched.json")["verdict"]
CF=L("agentguard_sae_counterfactual.json")["verdict"]
OUT=os.path.join(HERE,"figures_co"); os.makedirs(OUT,exist_ok=True)
C1="#1f77b4"; C2="#d62728"; CH="#888"

# ---------- Fig 1: the flip — supervised "authorization direction" inverts under structure-matching ----------
fig,ax=plt.subplots(figsize=(6.6,4.2))
vals=[V1["supervised_d_auroc_auth_vs_mom"], MM["supervised_d_auroc_auth_vs_mom"]]
bars=ax.bar([0,1],vals,color=[C1,C2],edgecolor="black",lw=0.7,width=0.55)
for x,v in zip([0,1],vals): ax.text(x,v+0.02,f"{v:.3f}",ha="center",va="bottom",fontsize=12,fontweight="bold")
ax.axhline(0.5,color=CH,ls="--",lw=1.2); ax.text(1.45,0.5,"chance",color=CH,fontsize=8,va="center")
ax.annotate("", xy=(1,0.13), xytext=(0,0.80), arrowprops=dict(arrowstyle="->",color="#555",lw=1.4,connectionstyle="arc3,rad=-0.25"))
ax.text(0.5,0.52,"same direction,\nstructure matched", ha="center", fontsize=8.5, color="#555")
ax.set_xticks([0,1]); ax.set_xticklabels(["unmatched\n(v1)","structure-matched"]); ax.set_ylim(0,1.05)
ax.set_ylabel("supervised $d$ AUROC (granted vs felt)")
ax.set_title("The #9/#10 \"authorization direction\" INVERTS under structure-matching\n"
             "A direction that measured granted-authorization would not flip when only the\n"
             "conversation format changes — it reads structure, not authorization",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig1_flip.pdf")); plt.close(fig)

# ---------- Fig 2: cross-lexical generalization (selection-free held-out test) ----------
fig,ax=plt.subplots(figsize=(7.4,4.2))
groups=["SAE feature","supervised $d$"]
within=[(CF["sae_within_A"]+CF["sae_within_B"])/2, (CF["supervised_within_A"]+CF["supervised_within_B"])/2]
crossA=[CF["sae_cross_A2B"], CF["supervised_cross_A2B"]]
crossB=[CF["sae_cross_B2A"], CF["supervised_cross_B2A"]]
x=np.arange(2); w=0.25
ax.bar(x-w, within, w, label="within-family (selection-inflated)", color="#bbbbbb", edgecolor="black", lw=0.5)
ax.bar(x,    crossA, w, label="cross A→B (held out)", color=C2, edgecolor="black", lw=0.5)
ax.bar(x+w,  crossB, w, label="cross B→A (held out)", color=C1, edgecolor="black", lw=0.5)
for xi,(a,b) in enumerate(zip(crossA,crossB)):
    ax.text(xi,a+0.02,f"{a:.2f}",ha="center",fontsize=8.5); ax.text(xi+w,b+0.02,f"{b:.2f}",ha="center",fontsize=8.5)
ax.axhline(0.5,color=CH,ls="--",lw=1.2); ax.text(1.55,0.5,"chance",color=CH,fontsize=8,va="center")
ax.set_xticks(x); ax.set_xticklabels(groups); ax.set_ylim(0,1.12); ax.set_ylabel("AUROC (granted vs felt)")
ax.legend(fontsize=7.6,loc="lower center")
ax.set_title("Cross-lexical generalization: the lexical shortcut (A→B) collapses to chance.\n"
             "A feature transfers B→A — but naming shows it is tool-call scaffold, not authorization (Fig.3)",fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig2_crosslexical.pdf")); plt.close(fig)

# ---------- Fig 3: feature naming — every separator is surface form ----------
rows=[
 ("#3127 (v1 best)",        "…<think></think>\\n<tool_call>\\n<function",        "tool-call scaffold"),
 ("#4244 (matched best)",   "Files: cache_tmp.dat, backup_201…",                "file-listing output"),
 ("#6201 (top, both runs)", '…-only).", "parameters": {"type": "object',        "JSON tool schema"),
 ("#9407 (top, matched)",   '…": "string"}}, "required": ["path"]',              "JSON tool schema"),
 ("#34355 (pooled, AUROC .998)", "function=example_function_name><parameter=…", "format boilerplate"),
 ("#10017 (transfers B→A)", "…<tool_call>\\n<function=",                         "tool-call scaffold"),
]
fig,ax=plt.subplots(figsize=(8.0,3.4)); ax.axis("off")
ax.text(0.5,1.02,"What the separating SAE features actually read (max-activating context)",
        ha="center",va="bottom",fontsize=10,fontweight="bold",transform=ax.transAxes)
tbl=ax.table(cellText=rows, colLabels=["SAE feature","max-activating token context","reads"],
             colWidths=[0.27,0.50,0.23], loc="center", cellLoc="left")
tbl.auto_set_font_size(False); tbl.set_fontsize(8.2); tbl.scale(1,1.5)
for (r,c),cell in tbl.get_celld().items():
    cell.set_edgecolor("#cccccc")
    if r==0: cell.set_facecolor("#1f77b4"); cell.set_text_props(color="white",fontweight="bold")
    elif c==2: cell.set_facecolor("#fde0e0")
ax.text(0.5,-0.08,"None is a semantic \"user-granted authorization\" feature — every separator is surface form.",
        ha="center",fontsize=8.5,style="italic",color="#b00",transform=ax.transAxes)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig3_naming.pdf"),bbox_inches="tight"); plt.close(fig)
print("figures written to",OUT)
print("check:",{"flip":(V1['supervised_d_auroc_auth_vs_mom'],MM['supervised_d_auroc_auth_vs_mom']),
                "crossA2B":CF['sae_cross_A2B'],"crossB2A":CF['sae_cross_B2A'],"pooled":CF['pooled_best_auroc']})
