#!/usr/bin/env python3
"""Zenodo upload for arc paper #10 'Felt, Not Granted' (bylined Caio Vicentino).
USAGE: ZENODO_TOKEN='<paste>' python3 paper/zenodo_upload_paper10.py [--publish]
Never logs the token. Default = draft. State in paper/.zenodo_paper10.json."""
import argparse, json, os, sys
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".zenodo_paper10.json"
BASE = "https://zenodo.org/api/deposit/depositions"
GH = "https://github.com/OpenInterpretability/agentguard"
PDF = ROOT / "felt_not_granted.pdf"
CREATOR = {"name": "Vicentino, Caio", "affiliation": "OpenInterpretability", "orcid": "0009-0003-4331-6259"}
ARC_DOIS = ["10.5281/zenodo.20368601","10.5281/zenodo.20490278","10.5281/zenodo.20490284",
            "10.5281/zenodo.20490286","10.5281/zenodo.20532769","10.5281/zenodo.20500053",
            "10.5281/zenodo.20534219","10.5281/zenodo.20634838","10.5281/zenodo.20679287",
            "10.5281/zenodo.20683623"]
TITLE = ("Felt, Not Granted: An Internal Authorization Probe Inherits the Agent's Judgment Error and Is "
         "Operationally Blind to Realistic Model-Origin Over-Reach, Where an External Task-Grounded Check Is Not")
DESCRIPTION = (
    "A late-layer 'authorization direction' detects and steers a tool-using agent's commitment to "
    "unauthorized irreversible actions (companion arc paper, DOI 10.5281/zenodo.20683623). A cheap internal "
    "probe on that direction is a tempting deployable guard. We test whether it survives the realistic "
    "failure mode it is meant to catch, with a real end-to-end test: a free-running Qwen3.6-27B file-system "
    "agent, real os.remove in a throwaway sandbox, the FROZEN direction adjudicating each proposed deletion "
    "at the tool-call token, against a black-box LLM-judge baseline. "
    "(1) Adversarial framings that make the deletion salient and instructed (indirect prompt injection, a "
    "disk-minimization objective, a proactive-cleanup mandate) elicit ZERO unauthorized deletes: the model "
    "perceives the push and its safety training wins -- naive red-teaming misses the real threat. "
    "(2) The error that fires is a JUDGMENT ERROR under a legitimate, ambiguous task, where authorization is "
    "INFERRED by the agent rather than GRANTED by the user: an agent completing a cleanup plan it had itself "
    "proposed under a vague 'go ahead' self-commits an unauthorized deletion in 18/18 varied scenarios. "
    "(3) On the elicited unauthorized deletes (n=21, 14 distinct internal scores), the frozen probe ALLOWS "
    "100% (95% Wilson CI [0.845, 1.0]) at its honestly-calibrated threshold, with ZERO false positives on 12 "
    "authorized deletes; an external task-grounded judge BLOCKS 100%. There is graded internal signal "
    "(AUROC 0.897 -- authorized deletes project higher) but the distributions overlap and both sit far above "
    "the threshold, so an honest operating point cannot exploit it; the judge separates at AUROC 1.0. "
    "FELT, NOT GRANTED: the probe tracks the authorization the model FEELS, not the one the user GRANTED; "
    "under adversarial framing these coincide (the regime where the direction works), under realistic "
    "model-origin error they diverge (the regime where it is blind). Internal-belief monitors and external "
    "task-grounded checks cover DISJOINT failure modes; defense-in-depth is necessary, not stylistic. "
    "HONEST SCOPE: one model, one domain (file deletion), a DETECTION operating point (steering-control is "
    "not re-tested and may still redirect these commits), a judge that is the same base model, and an "
    "effective n of about 14 distinct scenarios -- this is a qualification of the prior result, not a "
    "refutation. Runners, per-scenario ledgers, figures, and an evaluation that recomputes every number "
    "(54/54) plus a web-verified citation check (0 fabrications) are released.")
KEYWORDS = ["mechanistic interpretability","LLM agents","agent safety","AI control","authorization",
            "linear probe","activation probing","felt vs granted authorization","model-origin error",
            "over-helpfulness","LLM-as-judge","defense in depth","irreversible actions","Qwen3.6-27B"]
def metadata():
    rel = [{"identifier": GH, "relation": "isSupplementedBy", "scheme": "url"}]
    rel += [{"identifier": d, "relation": "references", "scheme": "doi"} for d in ARC_DOIS]
    return {"metadata": {"upload_type":"publication","publication_type":"other","title":TITLE,
        "creators":[CREATOR],"description":DESCRIPTION,"access_right":"open","license":"cc-by-4.0",
        "keywords":KEYWORDS,"related_identifiers":rel}}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN","").strip()
    if not token: sys.exit("ERROR: set ZENODO_TOKEN")
    if not PDF.exists(): sys.exit(f"ERROR: missing {PDF}")
    auth = {"access_token": token}
    if STATE.exists() and not args.force:
        prior = json.loads(STATE.read_text())
        if args.publish and prior.get("deposition_id") and not prior.get("published_doi"):
            rp = requests.post(f"{BASE}/{prior['deposition_id']}/actions/publish", params=auth, timeout=120)
            if rp.status_code >= 300: sys.exit(f"publish error {rp.status_code}: {rp.text[:300]}")
            pub = rp.json(); print("PUBLISHED. DOI:", pub.get("doi"), "|", pub.get("links",{}).get("record_html"))
            prior["published_doi"]=pub.get("doi"); STATE.write_text(json.dumps(prior,indent=2)); return
        sys.exit(f"ERROR: {STATE.name} exists; --force to avoid duplicate.")
    r = requests.post(BASE, params=auth, json={}, timeout=60); r.raise_for_status()
    dep = r.json(); dep_id = dep["id"]; bucket = dep["links"]["bucket"]
    print("draft", dep_id, "uploading", PDF.name)
    with open(PDF,"rb") as fh: requests.put(f"{bucket}/{PDF.name}", data=fh, params=auth, timeout=300).raise_for_status()
    rm = requests.put(f"{BASE}/{dep_id}", params=auth, json=metadata(), headers={"Content-Type":"application/json"}, timeout=60)
    if rm.status_code>=300: sys.exit(f"metadata error {rm.status_code}: {rm.text[:300]}")
    dep = rm.json(); state={"deposition_id":dep_id,"doi":dep.get("metadata",{}).get("prereserve_doi",{}).get("doi")}
    STATE.write_text(json.dumps(state,indent=2))
    print("DRAFT ready. Pre-reserved DOI:", state["doi"]); print("title:", (dep.get("metadata",{}).get("title") or "")[:60])
    print("files:", [f.get("filename") for f in dep.get("files",[])])
    print("related_ids:", len(metadata()["metadata"]["related_identifiers"]))
    if args.publish:
        rp = requests.post(f"{BASE}/{dep_id}/actions/publish", params=auth, timeout=120)
        if rp.status_code>=300: sys.exit(f"publish error {rp.status_code}: {rp.text[:300]}")
        pub = rp.json(); print("PUBLISHED. DOI:", pub.get("doi"), "|", pub.get("links",{}).get("record_html"))
        state["published_doi"]=pub.get("doi"); STATE.write_text(json.dumps(state,indent=2))
if __name__ == "__main__": main()
