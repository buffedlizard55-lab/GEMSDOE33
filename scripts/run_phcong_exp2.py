#!/usr/bin/env python3
"""Exp 2: A33-R7-PHCONG with dot_thin (d=2.8) emission — emission-operator isolation.
Preregistered in knowledge/28_phcong_exp2_emission_preregistration_20261028.md.
Same frozen PHCONG surface as Exp 1; only the emission operator changes.
"""
from __future__ import annotations
import hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path = [str(ROOT/"scripts"), str(ROOT), str(ROOT/"src")] + [p for p in sys.path if p not in (str(ROOT), str(ROOT/"scripts"), str(ROOT/"src"))]
from gemsdoe33 import csht_transfer, emission, grid  # noqa: E402
from gemsdoe33.phcong import build_phcong_surface  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402

DATE="20261028"; HYPOTHESIS="a33-r7-phcongdt-37654"; FULL=37654; FRAC=0.025; EXCL=2.0
REC_B1_S=0.112418; REC_B1_C=0.115122
MANIFEST=ROOT/"registry"/"focus_rasters_20261026.json"
def jw(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,allow_nan=False)+"\n")
def sha(p): 
    h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()

def emit(surface, holdout, random=False, seed=20261028):
    preds=[]
    for i,fold in enumerate(holdout.folds):
        valid,visible=fold["valid"],fold["visible"]
        d=distance_transform_edt(~visible); elig=valid&(d>EXCL)
        budget=int(round(FRAC*int(valid.sum())))
        rng=np.random.default_rng(seed+i)
        pri=rng.random(surface.shape,dtype=np.float32) if random else surface
        preds.append(emission.dot_thin(elig,2.8,priority=pri,max_dots=budget).astype(np.uint8))
    return preds

def main():
    t0=time.monotonic()
    fp=grid.template_footprint(); cat=grid.load_labels()&fp
    surface,parts=build_phcong_surface()
    hold=SegmentHoldout(fp,cat,buffer_px=15)
    canary=hold.canary(parts); max_auc=max(max(f["pooled_auc"],1-f["pooled_auc"]) for f in canary["features"].values())
    print(f"canary max2sAUC={max_auc:.4f} pass={canary['passed']}",flush=True)
    if not canary["passed"]: raise SystemExit("CANARY TRIPPED")
    preds=emit(surface,hold); ctrl=emit(surface,hold,random=True)
    screen=hold.summarize(preds,ci_draws=1999); vs=hold.compare_paired(preds,ctrl,ci_draws=1999,seed=20261028)
    print(f"screen DTI={screen['dti']:.6f} vs random delta={vs['paired_delta_dti']:+.6f} {vs['paired_delta_ci95']} wins={vs['fold_wins']}/4",flush=True)
    ch=csht_transfer.DiagonalSegmentHoldout(fp,cat,buffer_px=20)
    cpreds=emit(surface,ch); cctrl=emit(surface,ch,random=True,seed=20261029)
    confirm=ch.summarize(cpreds,ci_draws=1999); cvs=ch.compare_paired(cpreds,cctrl,ci_draws=1999,seed=20261029)
    print(f"confirm DTI={confirm['dti']:.6f} vs random delta={cvs['paired_delta_dti']:+.6f} wins={cvs['fold_wins']}/4",flush=True)
    # full emission
    dcat=distance_transform_edt(~cat); elig=fp&(dcat>EXCL)
    final=emission.dot_thin(elig,2.8,priority=surface,max_dots=FULL)
    print(f"final dots={int(final.sum())}",flush=True)
    elig_flat=np.flatnonzero(elig); scores=surface.ravel()[elig_flat]
    top=elig_flat[np.argsort(-scores,kind="mergesort")[:FULL]]; prev=np.zeros(fp.shape,bool); prev.ravel()[top]=True
    uniq=csht_transfer.audit_uniqueness_against_manifest(surface,prev,final,fp,MANIFEST,root=ROOT)
    jw(ROOT/"evidence/a33_r7_phcongdt_uniqueness_20261028.json",uniq)
    receipt=write_pair(final.astype(np.float32),template=ROOT/"data"/"sample_submission.tif",catalogue=cat,footprint=fp,outdir=ROOT/"docs"/"downloads",family="gemsdoe33",hypothesis=HYPOTHESIS,date=DATE,note_template="GEMS33 A33-R7-PHCONGDT: phase-congruency edges dotthin d2.8 37654d | gate pending | {cid}",scientific_verdict="pending")
    zp=ROOT/"docs"/"downloads"/receipt["primary_zero_outside"]["file"]; fmt=audit_submission(zp,ROOT/"data"/"sample_submission.tif",strict_zero_outside=True)
    sg=bool(screen["dti"]>REC_B1_S and screen["ci95"]["interval"][0]>REC_B1_S)
    cg=bool(confirm["dti"]>REC_B1_C and confirm["ci95"]["interval"][0]>REC_B1_C)
    rg=bool(vs["paired_delta_dti"]>0 and vs["paired_delta_ci95"][0]>0)
    uq=bool(uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    promote=bool(sg and cg and rg and uq and fmt["pass"] and canary["passed"])
    verdict="promote" if promote else "negative"
    receipt=write_pair(final.astype(np.float32),template=ROOT/"data"/"sample_submission.tif",catalogue=cat,footprint=fp,outdir=ROOT/"docs"/"downloads",family="gemsdoe33",hypothesis=HYPOTHESIS,date=DATE,note_template=f"GEMS33 A33-R7-PHCONGDT: phase-congruency edges dotthin d2.8 37654d | gate {verdict} | {{cid}}",scientific_verdict=verdict)
    (ROOT/"docs"/"downloads"/f"receipt-{receipt['submission_name']}.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    exp={"schema":1,"campaign":"A33-R7-PHCONGDT","date":DATE,"preregistration":str((ROOT/'knowledge/28_phcong_exp2_emission_preregistration_20261028.md').relative_to(ROOT)),"preregistration_sha256":sha(ROOT/"knowledge/28_phcong_exp2_emission_preregistration_20261028.md"),"verdict":verdict,"screen":screen,"confirmation":confirm,"vs_dotthin_random_screen":vs,"vs_dotthin_random_confirmation":cvs,"leakage_canary":{"passed":bool(canary["passed"]),"max_two_sided_auc":float(max_auc),"features":canary["features"]},"uniqueness":uniq,"format_audit":fmt,"raster_sha256":receipt["primary_zero_outside"]["sha256"],"nan_twin_sha256":receipt["official_text_nan_outside_twin"]["sha256"]}
    jw(ROOT/"evidence/a33_r7_phcongdt_experiment_20261028.json",exp)
    card={"schema":1,"campaign":"A33-R7-PHCONGDT","date":DATE,
      "hypothesis":"PHCONG surface (Exp 1) emitted by historical d=2.8 dot-thinning instead of CELF, isolating surface value from the CELF coverage operator.",
      "mechanism":"Amplitude-invariant phase-coherent mag/grav step edges mark buried basement faults; d=2.8 dotted emission matches the B2-family operator without copying its dots.",
      "named_non_fault_mimic":"Intrusive plutonic contacts, caldera ring margins and airborne survey line seams.",
      "verdict":verdict,
      "holdout_dti":{"label":"HOLDOUT-DTI","evaluator_version":csht_transfer.MTR_EVALUATOR_VERSION,"withheld_positives":int(screen["n_withheld_positive_pixels"]),
        "screen":{"split_id":"quadrant-buffered-15px-v1","candidate":screen["dti"],"ci95":screen["ci95"]["interval"],"paired_delta_vs_matched_random":vs["paired_delta_dti"],"paired_delta_ci95":vs["paired_delta_ci95"],"fold_wins":vs["fold_wins"]},
        "confirmation":{"split_id":"diagonal-wedge-buffered-20px-confirm-v1","candidate":confirm["dti"],"ci95":confirm["ci95"]["interval"],"paired_delta_vs_matched_random":cvs["paired_delta_dti"],"paired_delta_ci95":cvs["paired_delta_ci95"],"fold_wins":cvs["fold_wins"]},
        "recorded_context_unpaired":{"B1_regional_screen":REC_B1_S,"B1_regional_confirm":REC_B1_C},
        "exp1_celf_context":{"screen":0.16931590667916066,"confirmation":0.17058841899235586,"note":"same surface/splits, CELF operator; CELF-random control 0.181-class — see IR-33-CELF-RANDOM-01"},
        "qualification":"Catalogue hide-and-recover proxy. NOT private organizer truth, NOT a competition score or projection."},
      "correlation_overlap_vs_registry":{"surface_max_abs_spearman":uniq["surface"]["max_abs_spearman_rho"],"surface_max_3px_overlap":uniq["surface"]["max_preview_fraction_within_3px"],"surface_passed":bool(uniq["surface"]["passed"]),"final_dots_max_abs_spearman":uniq["final_dots"]["max_abs_spearman_rho"],"final_dots_max_3px_overlap":uniq["final_dots"]["max_candidate_fraction_within_3px"],"final_dots_passed":bool(uniq["final_dots"]["passed"]),"scope":"21 pinned rasters"},
      "leakage_canary":{"passed":bool(canary["passed"]),"max_two_sided_auc":float(max_auc)},
      "raster_sha256":receipt["primary_zero_outside"]["sha256"],"nan_twin_sha256":receipt["official_text_nan_outside_twin"]["sha256"],
      "submission":{"file":receipt["primary_zero_outside"]["file"],"zip":receipt["primary_zero_outside"]["zip"],"note":receipt["note"],"name":receipt["submission_name"],"ok_to_submit":promote},
      "promotion_assessment":{"eligible_for_selector":promote,"verdict":verdict,"gates":{"screen_beats_recorded_b1_with_positive_ci":sg,"confirm_beats_recorded_b1_with_positive_ci":cg,"screen_beats_dotthin_random_positive_ci":rg,"surface_not_duplicate":bool(uniq["surface"]["passed"]),"final_dots_not_duplicate":bool(uniq["final_dots"]["passed"]),"format_audit_pass":bool(fmt["pass"]),"canary_pass":bool(canary["passed"])},"failed_gates":[k for k,v in {"screen":sg,"confirm":cg,"random":rg,"uniq":uq,"format":bool(fmt["pass"])}.items() if not v]},
      "runtime_seconds":round(time.monotonic()-t0,2)}
    jw(ROOT/"evidence/a33_r7_phcongdt_run_card_20261028.json",card); jw(ROOT/"docs/data/a33_r7_phcongdt_run_card_20261028.json",card)
    print(json.dumps({"verdict":verdict,"screen":screen["dti"],"confirm":confirm["dti"],"promote":promote},indent=2))
if __name__=="__main__": raise SystemExit(main())
