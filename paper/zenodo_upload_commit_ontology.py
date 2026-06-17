#!/usr/bin/env python3
"""Zenodo upload for arc paper #11 'Form, Not Granted' (bylined Caio Vicentino).
USAGE: ZENODO_TOKEN='<paste>' python3 paper/zenodo_upload_commit_ontology.py [--publish]
Never logs the token. Default = draft. State in paper/.zenodo_commit_ontology.json."""
import argparse, json, os, sys
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".zenodo_commit_ontology.json"
BASE = "https://zenodo.org/api/deposit/depositions"
GH = "https://github.com/OpenInterpretability/agentguard"
PDF = ROOT / "commit_ontology.pdf"
CREATOR = {"name": "Vicentino, Caio", "affiliation": "OpenInterpretability", "orcid": "0009-0003-4331-6259"}
ARC_DOIS = ["10.5281/zenodo.20368601","10.5281/zenodo.20490278","10.5281/zenodo.20490284",
            "10.5281/zenodo.20490286","10.5281/zenodo.20532769","10.5281/zenodo.20500053",
            "10.5281/zenodo.20534219","10.5281/zenodo.20634838","10.5281/zenodo.20679287",
            "10.5281/zenodo.20683623","10.5281/zenodo.20685264"]
TITLE = ("Form, Not Granted: A Sparse-Autoencoder Autopsy Shows the Agent's Commit-Locus 'Authorization "
         "Direction' Is a Surface-Form Artifact --- and an All-Layer Sweep Leaves the Deeper Question Open (v2)")
DESCRIPTION = (
    "A late-layer 'authorization direction' was reported to detect and steer a tool-using agent's "
    "commitment to unauthorized irreversible actions (DOI 10.5281/zenodo.20683623), and a follow-up found it "
    "tracks the authorization the model FEELS rather than the one the user GRANTED (DOI 10.5281/zenodo.20685264). "
    "Both were built on a SUPERVISED difference-of-means direction -- a method that returns a direction whether "
    "or not the concept is natively represented. We stop using the ruler and point the microscope: we encode "
    "the residual at the delete-commit token (layer 59 of Qwen3.6-27B) through a trained TopK sparse autoencoder "
    "(40,960 features) and ask, unsupervised, whether a feature distinguishes a GRANTED commit from a "
    "FELT-but-not-granted one. "
    "(1) The supervised direction INVERTS under a structure-matched control: applying the same frozen direction, "
    "AUROC(granted vs felt) goes from 0.838 to 0.08 when both conditions share one multi-turn scaffold and only "
    "the final user turn varies -- selection-free and SAE-independent. A direction measuring authorization would "
    "not flip when only the conversation FORMAT changes. "
    "(2) The SAE's separating features are SURFACE FORM: every top feature that separates granted from felt is, "
    "by its max-activating context, a tool-call scaffold, a JSON tool-schema token, or the file-listing output "
    "-- never a semantic 'user granted this' feature. "
    "(3) A cross-lexical-family test isolates this: a feature selected on one paraphrase family does NOT transfer "
    "to a disjoint family (held-out AUROC 0.50, chance), and the one feature that does transfer (0.993, pooled "
    "0.998) max-activates on tool-call FORMAT BOILERPLATE, not authorization. "
    "The agent's commit-point representation is dominated by surface form and plan-coherence; "
    "authorization-as-granted is not a native monosemantic feature AT THIS LOCUS (see the v2 revision below: an "
    "all-layer sweep complicates any stronger claim). The robust lesson: the commit-locus difference-of-means "
    "direction reads form, not a clean grant. "
    "HONEST SCOPE: one model, one locus (L59), one domain (file deletion), synthetic structure-matched "
    "scenarios, an SAE explaining ~66% of residual variance; 'no native authorization feature' is strictly "
    "'no monosemantic separating feature in this SAE's learned dictionary at this locus' (absence of a "
    "separating feature is weaker than evidence of absence of any representation); this QUALIFIES, not refutes, "
    "the prior arc, and steering-control is not re-tested. Every number is recomputed from five public per-run "
    "ledgers (an evaluation script, 34/34) and citations are web-verified (0 fabrications); the decisive "
    "counterfactual run reproduced bit-for-bit across two GPU sessions. Runners, ledgers, figures, and the "
    "evaluation are released. REVISION (v2): the first version concluded 'no native authorization concept'. A subsequent sweep across ALL 11 SAE layers (two positions) revealed a paraphrase-invariant granted-vs-felt linear signal at most layers that this conclusion did not account for; but the signal carries residual surface confounds (an em-dash present in both granted phrasings and neither felt; referent specificity; it is already near-ceiling at layer 15, too early for semantics), so we cannot call it authorization either. This version WITHDRAWS the unqualified no-concept claim, scopes the result to the commit locus, and states the deeper question as OPEN (needs a confound-balanced re-run with feature naming). The robust findings (the structural flip 0.838->0.08, the L59 surface-form naming) are unchanged.")
KEYWORDS = ["mechanistic interpretability","sparse autoencoder","LLM agents","agent safety","authorization",
            "linear probe","difference-of-means","control tasks","shortcut learning","surface form",
            "plan coherence","commit ontology","Qwen3.6-27B","superposition"]
def metadata():
    rel = [{"identifier": GH, "relation": "isSupplementedBy", "scheme": "url"}]
    rel += [{"identifier": d, "relation": "references", "scheme": "doi"} for d in ARC_DOIS]
    return {"metadata": {"upload_type":"publication","publication_type":"other","title":TITLE,
        "creators":[CREATOR],"description":DESCRIPTION,"access_right":"open","license":"cc-by-4.0",
        "keywords":KEYWORDS,"related_identifiers":rel}}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); ap.add_argument("--force", action="store_true"); ap.add_argument("--newversion", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN","").strip()
    if not token: sys.exit("ERROR: set ZENODO_TOKEN")
    if not PDF.exists(): sys.exit(f"ERROR: missing {PDF}")
    auth = {"access_token": token}
    if args.newversion:
        orig = json.loads(STATE.read_text()).get("deposition_id")
        rv = requests.post(f"{BASE}/{orig}/actions/newversion", params=auth, timeout=60)
        if rv.status_code>=300: sys.exit(f"newversion error {rv.status_code}: {rv.text[:300]}")
        draft_url = rv.json()["links"]["latest_draft"]
        dep = requests.get(draft_url, params=auth, timeout=60).json(); dep_id=dep["id"]
        for fobj in dep.get("files",[]):
            requests.delete(f"{BASE}/{dep_id}/files/{fobj['id']}", params=auth, timeout=60)
        bucket = dep["links"]["bucket"]
        with open(PDF,"rb") as fh: requests.put(f"{bucket}/{PDF.name}", data=fh, params=auth, timeout=300).raise_for_status()
        rm = requests.put(f"{BASE}/{dep_id}", params=auth, json=metadata(), headers={"Content-Type":"application/json"}, timeout=60)
        if rm.status_code>=300: sys.exit(f"metadata error {rm.status_code}: {rm.text[:300]}")
        print("v2 draft", dep_id, "| files:", [f.get("filename") for f in rm.json().get("files",[])], "| related:", len(metadata()["metadata"]["related_identifiers"]))
        if args.publish:
            rp = requests.post(f"{BASE}/{dep_id}/actions/publish", params=auth, timeout=120)
            if rp.status_code>=300: sys.exit(f"publish error {rp.status_code}: {rp.text[:300]}")
            pub=rp.json(); print("PUBLISHED v2. DOI:", pub.get("doi"), "|", pub.get("links",{}).get("record_html"))
            st=json.loads(STATE.read_text()); st["v2_deposition_id"]=dep_id; st["v2_doi"]=pub.get("doi"); STATE.write_text(json.dumps(st,indent=2))
        return
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
    print("DRAFT ready. Pre-reserved DOI:", state["doi"]); print("title:", (dep.get("metadata",{}).get("title") or "")[:64])
    print("files:", [f.get("filename") for f in dep.get("files",[])]); print("related_ids:", len(metadata()["metadata"]["related_identifiers"]))
    if args.publish:
        rp = requests.post(f"{BASE}/{dep_id}/actions/publish", params=auth, timeout=120)
        if rp.status_code>=300: sys.exit(f"publish error {rp.status_code}: {rp.text[:300]}")
        pub = rp.json(); print("PUBLISHED. DOI:", pub.get("doi"), "|", pub.get("links",{}).get("record_html"))
        state["published_doi"]=pub.get("doi"); STATE.write_text(json.dumps(state,indent=2))
if __name__ == "__main__": main()
