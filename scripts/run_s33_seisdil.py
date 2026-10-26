#!/usr/bin/env python3
"""S33-SEISDIL: strain-seismicity corridor gate. Prereg: knowledge/13_s33_seisdil_preregistration_20261026.md
Reuses shared SegmentHoldout evaluator, CELF emission, submission writer (no forks). No upload."""
from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"))
from gemsdoe33 import analog_invariant, csht_transfer, grid  # noqa
from submission_writer import write_pair  # noqa
from validate_submission import audit as audit_submission  # noqa
from vendor.gems24_template.holdout import SegmentHoldout  # noqa
from vendor.gems24_template.validator import sha256_file  # noqa

MANIFEST = ROOT/"registry/focus_rasters_20261026_r3.json"
DATE="20261026"; BUDGET=37654
def jw(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,allow_nan=False)+"\n")
def pct(a,dom): return analog_invariant.percentile_surface(np.nan_to_num(a).astype(np.float32), dom)
def gradmag(name):
    a=np.asarray(np.load(ROOT/".cache/features"/f"{name}.npy"),dtype=np.float32)
    s=gaussian_filter(np.nan_to_num(a),2.0); gy,gx=np.gradient(s); return np.hypot(gx,gy).astype(np.float32)

def main():
    t0=time.monotonic(); footprint=grid.template_footprint(); catalogue=grid.load_labels()&footprint
    arrays=analog_invariant.load_feature_arrays()
    gate_raw={"geod_dilaterate_grad":gradmag("geod_dilaterate"),"geod_shearrate_grad":gradmag("geod_shearrate"),
              "ieq_ridge":np.asarray(np.load(ROOT/".cache/features/ieq_n100a15_ridge.npy"),dtype=np.float32)}
    gate=np.mean([pct(v,footprint) for v in gate_raw.values()],axis=0).astype(np.float32)
    screen=SegmentHoldout(footprint,catalogue,buffer_px=15); confirm=csht_transfer.DiagonalSegmentHoldout(footprint,catalogue,buffer_px=20)
    canary=screen.canary({**gate_raw,"seisdil_gate":gate})
    rows=[{"feature":k,"max_fold_auc":float(max(max(d["auc"],1-d["auc"]) for d in v["folds"])),"pooled_auc":float(max(v["pooled_auc"],1-v["pooled_auc"])),"leakage_suspect":bool(v["leakage_suspected"])} for k,v in canary["features"].items()]
    print("canary",rows,flush=True)
    if not canary["passed"]: raise SystemExit("CANARY TRIPPED")
    nfp=int(footprint.sum())
    def run(ho,tag,seed0):
        preds={"B1":[],"SEISDIL":[]}; reps=[]
        for fold in ho.folds:
            valid,train,visible=fold["valid"],fold["train"],fold["visible"]; fid=int(fold["id"])
            dvis=distance_transform_edt(~visible); elig=valid&(dvis>2.0); bud=int(round(BUDGET*int(valid.sum())/nfp))
            m=analog_invariant.fit_regional_expert(arrays,train,visible,dvis,seed=seed0+100*fid+1)
            s=analog_invariant.predict(m,arrays,valid); sp=pct(s,valid)
            cand=(sp*(0.2+0.8*gate)).astype(np.float32)
            for name,surf in [("B1",s),("SEISDIL",cand)]:
                dots=csht_transfer.celf_emit_300m(surf,elig,bud,min_self_spacing_px=2.5)
                assert int(dots.sum())==bud; preds[name].append(dots.astype(np.uint8))
            reps.append({"fold":fold["name"],"budget":bud,"withheld":int(fold["truth"].sum())})
            print(tag,fold["name"],bud,flush=True)
        res={k:ho.summarize(v,ci_draws=1999) for k,v in preds.items()}
        cmp_=ho.compare_paired(preds["SEISDIL"],preds["B1"],ci_draws=1999,seed=seed0)
        return res,cmp_,reps
    sres,scmp,srep=run(screen,"screen",20261040); print("SCREEN",sres["SEISDIL"]["dti"],sres["B1"]["dti"],scmp,flush=True)
    cres,ccmp,crep=run(confirm,"confirm",20261050); print("CONFIRM",cres["SEISDIL"]["dti"],cres["B1"]["dti"],ccmp,flush=True)
    # full deployment
    dcat=distance_transform_edt(~catalogue); elig=footprint&(dcat>2.0)
    m=analog_invariant.fit_regional_expert(arrays,footprint,catalogue,dcat,seed=20261060)
    s=analog_invariant.predict(m,arrays,footprint); surf=(pct(s,footprint)*(0.2+0.8*gate)).astype(np.float32)
    flat=np.flatnonzero(elig); top=flat[np.argsort(-surf.ravel()[flat],kind="mergesort")[:BUDGET]]
    prev=np.zeros(footprint.shape,bool); prev.ravel()[top]=True
    dots=csht_transfer.celf_emit_300m(surf,elig,BUDGET,min_self_spacing_px=2.5); assert int(dots.sum())==BUDGET
    uniq=csht_transfer.audit_uniqueness_against_manifest(surf,prev,dots,footprint,MANIFEST,root=ROOT)
    print("UNIQ surface",uniq["surface"]["passed"],uniq["surface"].get("max_abs_spearman"),uniq["surface"].get("max_overlap_fraction"),flush=True)
    print("UNIQ dots",uniq["final_dots"]["passed"],uniq["final_dots"].get("max_abs_spearman"),uniq["final_dots"].get("max_overlap_fraction"),flush=True)
    promote=(sres["SEISDIL"]["dti"]>sres["B1"]["dti"] and scmp["ci95_strictly_positive"] and scmp["fold_wins"]>=3
             and cres["SEISDIL"]["dti"]>cres["B1"]["dti"] and ccmp["ci95_strictly_positive"] and ccmp["fold_wins"]>=3
             and uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    verdict="promote" if promote else ("duplicate" if not(uniq["surface"]["passed"] and uniq["final_dots"]["passed"]) else "negative")
    note_t=f"GEMS33 S33-SEISDIL strain-seismicity gate 37654d | gate {verdict.upper()} | "+"{cid}"
    receipt=write_pair(dots.astype(np.float32),template=ROOT/"data/sample_submission.tif",catalogue=catalogue,footprint=footprint,
                       outdir=ROOT/"docs/downloads",family="gemsdoe33",hypothesis="s33-seisdil-strain-seismicity-37654",date=DATE,
                       note_template=note_t,scientific_verdict=verdict)
    zero=ROOT/"docs/downloads"/receipt["primary_zero_outside"]["file"]; fmt=audit_submission(zero,ROOT/"data/sample_submission.tif")
    arr_ok=True
    import rasterio
    with rasterio.open(zero) as ds: a=ds.read(1); arr_ok=bool(np.isfinite(a).all() and a.min()>=0 and a.max()<=1)
    card={"schema":1,"campaign":"S33-SEISDIL","date_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "hypothesis":"Geodetic dilatation/shear strain-rate gradient corridors + earthquake-intensity ridges mark actively extending, permeable fault zones absent from USGS/INGENIOUS catalogue; gating catalogue-trained prior by this corridor recovers hidden faults.",
      "mechanism":"surface=pct(B1 regional HGB)*(0.2+0.8*mean pct(dil-grad, shear-grad, ieq ridge)); CELF 300m triangular emission, 37654 dots, >2px off catalogue",
      "named_non_fault_process_that_could_mimic_it":"Caldera/aquifer deformation and volcanic seismic swarms producing strain/seismicity without a throughgoing fault",
      "holdout_dti":{"label":"HOLDOUT-DTI","evaluator_version":sres["SEISDIL"]["evaluator_version"],"withheld_positives":int(sres["SEISDIL"]["n_withheld_positive_pixels"]),
        "screen_candidate":float(sres["SEISDIL"]["dti"]),"screen_candidate_ci95":sres["SEISDIL"].get("dti_ci95"),"screen_B1":float(sres["B1"]["dti"]),"screen_paired":scmp,
        "confirm_candidate":float(cres["SEISDIL"]["dti"]),"confirm_candidate_ci95":cres["SEISDIL"].get("dti_ci95"),"confirm_B1":float(cres["B1"]["dti"]),"confirm_paired":ccmp,
        "note":"HOLDOUT-DTI is an estimate only; NOT organizer-confirmed and NOT a leaderboard projection (prior lanes: holdout ~0.13 corresponded to no confirmed score)."},
      "feature_canaries":rows,
      "correlation_overlap_vs_registry":{"n_rasters":len(uniq["surface"]["rows"]) if "rows" in uniq.get("surface",{}) else 22,"surface":uniq["surface"],"final_dots":uniq["final_dots"]},
      "raster_sha256":receipt["primary_zero_outside"]["sha256"],
      "validator_output":{"format_audit":fmt,"all_cells_finite_in_0_1_saved_bytes":arr_ok,"receipt_validator":receipt["primary_zero_outside"].get("validator")},
      "submission_name":zero.stem,"submission_note":receipt["note"],"verdict":verdict,
      "ok_to_submit":bool(promote and fmt.get("pass",fmt.get("format_valid",False)) and arr_ok),
      "elapsed_seconds":round(time.monotonic()-t0,1)}
    # audit() return shape check
    print("FMT",fmt,flush=True)
    jw(ROOT/"evidence/s33_seisdil_run_card_20261026.json",card); jw(ROOT/"docs/data/s33_seisdil_run_card_20261026.json",card)
    jw(ROOT/"evidence/s33_seisdil_uniqueness_20261026.json",uniq)
    print(json.dumps({k:card[k] for k in ["verdict","ok_to_submit","submission_name","submission_note","raster_sha256"]},indent=1))
if __name__=="__main__": main()
