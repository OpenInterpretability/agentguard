#!/usr/bin/env python3
"""Zenodo upload for arc paper #9 'The Authorization Direction' (bylined Caio Vicentino).
USAGE: ZENODO_TOKEN='<paste>' python3 paper/zenodo_upload_paper9.py [--publish]
Never logs the token. Default = draft. State in paper/.zenodo_paper9.json."""
import argparse, json, os, sys
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".zenodo_paper9.json"
BASE = "https://zenodo.org/api/deposit/depositions"
GH = "https://github.com/OpenInterpretability/agentguard"
PDF = ROOT / "authorization_direction.pdf"
CREATOR = {"name": "Vicentino, Caio", "affiliation": "OpenInterpretability", "orcid": "0009-0003-4331-6259"}
ARC_DOIS = ["10.5281/zenodo.20368601","10.5281/zenodo.20490278","10.5281/zenodo.20490284",
            "10.5281/zenodo.20490286","10.5281/zenodo.20532769","10.5281/zenodo.20500053",
            "10.5281/zenodo.20534219","10.5281/zenodo.20634838","10.5281/zenodo.20679287"]
TITLE = ("The Authorization Direction: A Late-Layer Direction that Detects and Controls an Agent's "
         "Commitment to Unauthorized Irreversible Actions, Across Architectures")
DESCRIPTION = (
    "A safety circuit-breaker for a tool-using agent must, at the moment the agent is about to emit an "
    "irreversible action, answer two questions: is the action authorized by the trusted task, and can we "
    "stop it if not. We show both live in a single linear direction at a late layer of the residual stream. "
    "(1) DETECTION: a linear probe separates authorized from unauthorized irreversible-action commits at "
    "AUROC ~1.0 on Qwen3.6-27B; we rule out the capacity confound four ways (one-dimensional difference-of-"
    "means, regularization sweep, PCA to 32 dims, and commit-state matching), a random direction is at chance "
    "at the clean late locus, and the direction is domain-general (train on five actions, detect the held-out "
    "sixth at 1.0) and origin-robust (train on injection, detect held-out model-internal at 0.89). "
    "(2) CONTROL: steering along d = mean(authorized) - mean(unauthorized) monotonically moves the commit "
    "(emit range 0.67 vs 0.03 for a random direction) -- the SAME direction detects and controls. "
    "(3) ACROSS ARCHITECTURES: the full result replicates on gpt-oss-20b (a different-family MoE model): "
    "detection AUROC 1.0 (random at chance), cross-action transfer 1.0, steering range 0.65 vs -0.25. "
    "(4) A BEHAVIORAL FINDING: both models OBEY explicit prohibition (commit 0.00 when told 'do not') but "
    "SELF-COMMIT irreversible actions from a benign task -- the residual risk is unprompted over-eagerness, "
    "not defiance, and it is the model-origin failure no input-provenance or text filter can see. This "
    "sharpens the WANDERING arc's detect != control refrain: at the late action-commitment locus they "
    "coincide, contrasting the mid-layer verdict feature that predicts but does not cause termination. "
    "HONEST SCOPE: AUROC=1.0 is a ceiling whose capacity origin is ruled out but whose surface-lexical "
    "component is not fully isolated; actions are simulated; the method is white-box (defender-owned weights); "
    "Llama/Mistral are gated and were run for the actuator in the prior safety paper. Pre-registrations, "
    "per-run data, figures, the model-agnostic runner, and an adversarial evaluation that recomputes every "
    "number (35/35) from the public data are released.")
KEYWORDS = ["mechanistic interpretability","LLM agents","agent safety","AI control","authorization",
            "linear probe","activation steering","detect vs control","irreversible actions","circuit breaker",
            "cross-architecture","Qwen3.6-27B","gpt-oss","corrigibility"]
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
    print("DRAFT ready. Pre-reserved DOI:", state["doi"]); print("title:", dep.get("metadata",{}).get("title")[:60])
    print("files:", [f.get("filename") for f in dep.get("files",[])])
    if args.publish:
        rp = requests.post(f"{BASE}/{dep_id}/actions/publish", params=auth, timeout=120)
        if rp.status_code>=300: sys.exit(f"publish error {rp.status_code}: {rp.text[:300]}")
        pub = rp.json(); print("PUBLISHED. DOI:", pub.get("doi"), "|", pub.get("links",{}).get("record_html"))
        state["published_doi"]=pub.get("doi"); STATE.write_text(json.dumps(state,indent=2))
if __name__ == "__main__": main()
