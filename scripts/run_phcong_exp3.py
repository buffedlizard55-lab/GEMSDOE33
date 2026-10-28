#!/usr/bin/env python3
"""Exp 3: A33-R7-PCSUP — supervised subsurface-only HGB on PHCONG+potential-field channels.
Preregistered knowledge/29_phcong_exp3_pcsup_preregistration_20261028.md.
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path = [str(ROOT/"scripts"), str(ROOT), str(ROOT/"src")] + [p for p in sys.path if p not in (str(ROOT), str(ROOT/"scripts"), str(ROOT/"src"))]
from gemsdoe33 import csht_transfer, grid  # noqa: E402
from gemsdoe33.paths import CACHE_FEATURES  # noqa: E402
from gemsdoe33.phcong import build_phcong_surface  # noqa: E402
from submission_writer import write_pair  # noqa: E402
from validate_submission import audit as audit_submission  # noqa: E402
from vendor.gems24_template.holdout import SegmentHoldout  # noqa: E402

DATE="20261028"; HYPOTHESIS="a33-r7-pcsup-37654"; FULL=37654; FRAC=0.025; EXCL=2.0
REC_B1_S=0.112418; REC_B1_C=0.115122
MANIFEST=ROOT/"registry"/"focus_rasters_20261026.json"
CACHE_NAMES=["tmi","ext_TMI_up150","iso_grav_anom","iso_grav_anom_hg","iso_grav_anom_vg","cond_surf","depth_to_base_surf","geod_2ndinv","geod_shearrate","geod_dilaterate","tc","tmi_hg","tmi_vg"]
def jw(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,allow_nan=False)+"\n")
def sha(p):
    h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()

def load_arrays(parts):
    arrays={}
    for n in CACHE_NAMES: arrays[n]=np.load(CACHE_FEATURES/f"{n}.npy",mmap_mode="r")
    arrays["pc_tmi"]=parts["pc_tmi"]; arrays["pc_ext_TMI_up150"]=parts["pc_ext_TMI_up150"]; arrays["pc_iso_grav_anom"]=parts["pc_iso_grav_anom"]
    arrays["orientation_agreement"]=parts["orientation_agreement"]; arrays["phcong_surface"]=parts["phcong_surface"]
    return arrays
NAMES=tuple(["pc_tmi","pc_ext_TMI_up150","pc_iso_grav_anom","orientation_agreement","phcong_surface"]+CACHE_NAMES)

def extract(arrays,ids):
    out=np.empty((ids.size,len(NAMES)),dtype=np.float32)
    for j,n in enumerate(NAMES):
        v=np.asarray(arrays[n]).ravel()[ids].astype(np.float32,copy=True); v[np.isinf(v)]=np.nan; out[:,j]=np.nan_to_num(v,nan=0.0)
    return out

def fit_predict(arrays,train,visible,domain,seed):
    dvis=distance_transform_edt(~visible)
    pos_mask=train&visible; neg_mask=train&~visible&(dvis>8.0)
    rng=np.random.default_rng(seed)
    pos=csht_transfer._sample_ids(pos_mask,30000,rng); neg=csht_transfer._sample_ids(neg_mask,min(60000,int(neg_mask.sum())),rng)
    ids=np.concatenate([pos,neg]); y=np.concatenate([np.ones(pos.size,np.uint8),np.zeros(neg.size,np.uint8)])
    w=np.concatenate([np.ones(pos.size,np.float32),np.full(neg.size,pos.size/max(neg.size,1),np.float32)])
    m=HistGradientBoostingClassifier(max_iter=160,learning_rate=0.06,max_leaf_nodes=31,min_samples_leaf=60,l2_regularization=3.0,early_stopping=False,random_state=seed)
    m.fit(extract(arrays,ids),y,sample_weight=w)
    out=np.zeros(domain.shape,dtype=np.float32); did=np.flatnonzero(domain)
    for s in range(0,did.size,350000):
        b=did[s:s+350000]; out.ravel()[b]=m.predict_proba(extract(arrays,b))[:,1].astype(np.float32)
    return out

def emit(surface,holdout):
    preds=[]
    for fold in holdout.folds:
        valid,visible=fold["valid"],fold["visible"]; d=distance_transform_edt(~visible); elig=valid&(d>EXCL)
        budget=int(round(FRAC*int(valid.sum())))
        preds.append(csht_transfer.celf_emit_300m(surface,elig,budget,min_self_spacing_px=2.5).astype(np.uint8))
    return preds
def emit_random(holdout,shape,seed=20261028):
    preds=[]
    for i,fold in enumerate(holdout.folds):
        valid,visible=fold["valid"],fold["visible"]; d=distance_transform_edt(~visible); elig=valid&(d>EXCL)
        budget=int(round(FRAC*int(valid.sum()))); rng=np.random.default_rng(seed+i)
        preds.append(csht_transfer.celf_emit_300m(rng.random(shape,dtype=np.float32),elig,budget,min_self_spacing_px=2.5).astype(np.uint8))
    return preds

def main():
    t0=time.monotonic(); fp=grid.template_footprint(); cat=grid.load_labels()&fp
    phcong,parts=build_phcong_surface(); arrays=load_arrays(parts)
    hold=SegmentHoldout(fp,cat,buffer_px=15)
    # canaries on all input features
    canary=hold.canary({n:np.asarray(arrays[n],dtype=np.float32) for n in NAMES})
    max_auc=max(max(f["pooled_auc"],1-f["pooled_auc"]) for f in canary["features"].values())
    print(f"canary {len(NAMES)} feats max2sAUC={max_auc:.4f} pass={canary['passed']}",flush=True)
    if not canary["passed"]: raise SystemExit("CANARY TRIPPED")
    # screen: fit per fold
    preds=[]; phcong_preds=[]
    for i,fold in enumerate(hold.folds):
        surf=fit_predict(arrays,fold["train"],fold["visible"],fold["valid"],seed=20261028+i)
        d=distance_transform_edt(~fold["visible"]); elig=fold["valid"]&(d>EXCL); budget=int(round(FRAC*int(fold["valid"].sum())))
        preds.append(csht_transfer.celf_emit_300m(surf,elig,budget,min_self_spacing_px=2.5).astype(np.uint8))
        phcong_preds.append(csht_transfer.celf_emit_300m(phcong,elig,budget,min_self_spacing_px=2.5).astype(np.uint8))
        print(f"fold {fold['name']} done",flush=True)
    screen=hold.summarize(preds,ci_draws=1999)
    ctrl=emit_random(hold,fp.shape); vs_r=hold.compare_paired(preds,ctrl,ci_draws=1999,seed=20261028); vs_p=hold.compare_paired(preds,phcong_preds,ci_draws=1999,seed=20261028)
    print(f"screen DTI={screen['dti']:.6f} vsCELFrand {vs_r['paired_delta_dti']:+.6f} {vs_r['paired_delta_ci95']} vsPHCONG {vs_p['paired_delta_dti']:+.6f} {vs_p['paired_delta_ci95']}",flush=True)
    ch=csht_transfer.DiagonalSegmentHoldout(fp,cat,buffer_px=20)
    cpreds=[]
    for i,fold in enumerate(ch.folds):
        # DiagonalSegmentHoldout folds use same dict keys? inspect fallback
        train=fold.get("train", fp & ~fold["valid"]); visible=fold["visible"]
        surf=fit_predict(arrays,train,visible,fold["valid"],seed=20261038+i)
        d=distance_transform_edt(~visible); elig=fold["valid"]&(d>EXCL); budget=int(round(FRAC*int(fold["valid"].sum())))
        cpreds.append(csht_transfer.celf_emit_300m(surf,elig,budget,min_self_spacing_px=2.5).astype(np.uint8))
        print(f"confirm fold {fold.get('name',i)} done",flush=True)
    confirm=ch.summarize(cpreds,ci_draws=1999)
    print(f"confirm DTI={confirm['dti']:.6f}",flush=True)
    # full model
    dcat=distance_transform_edt(~cat); full_surf=fit_predict(arrays,fp,cat,fp,seed=20261099)
    elig_full=fp&(dcat>EXCL); final=csht_transfer.celf_emit_300m(full_surf,elig_full,FULL,min_self_spacing_px=2.5)
    ef=np.flatnonzero(elig_full); sc=full_surf.ravel()[ef]; top=ef[np.argsort(-sc,kind="mergesort")[:FULL]]; prev=np.zeros(fp.shape,bool); prev.ravel()[top]=True
    uniq=csht_transfer.audit_uniqueness_against_manifest(full_surf,prev,final,fp,MANIFEST,root=ROOT); jw(ROOT/"evidence/a33_r7_pcsup_uniqueness_20261028.json",uniq)
    receipt=write_pair(final.astype(np.float32),template=ROOT/"data"/"sample_submission.tif",catalogue=cat,footprint=fp,outdir=ROOT/"docs"/"downloads",family="gemsdoe33",hypothesis=HYPOTHESIS,date=DATE,note_template="GEMS33 A33-R7-PCSUP: supervised subsurface PHCONG HGB CELF 37654d | gate pending | {cid}",scientific_verdict="pending")
    zp=ROOT/"docs"/"downloads"/receipt["primary_zero_outside"]["file"]; fmt=audit_submission(zp,ROOT/"data"/"sample_submission.tif",strict_zero_outside=True)
    sg=bool(screen["dti"]>REC_B1_S and screen["ci95"]["interval"][0]>REC_B1_S); cg=bool(confirm["dti"]>REC_B1_C and confirm["ci95"]["interval"][0]>REC_B1_C)
    rg=bool(vs_r["paired_delta_ci95"][0]>0); pg=bool(vs_p["paired_delta_ci95"][0]>0); uq=bool(uniq["surface"]["passed"] and uniq["final_dots"]["passed"])
    promote=bool(sg and cg and rg and pg and uq and fmt["pass"] and canary["passed"]); verdict="promote" if promote else "negative"
    receipt=write_pair(final.astype(np.float32),template=ROOT/"data"/"sample_submission.tif",catalogue=cat,footprint=fp,outdir=ROOT/"docs"/"downloads",family="gemsdoe33",hypothesis=HYPOTHESIS,date=DATE,note_template=f"GEMS33 A33-R7-PCSUP: supervised subsurface PHCONG HGB CELF 37654d | gate {verdict} | {{cid}}",scientific_verdict=verdict)
    (ROOT/"docs"/"downloads"/f"receipt-{receipt['submission_name']}.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    exp={"schema":1,"campaign":"A33-R7-PCSUP","date":DATE,"preregistration_sha256":sha(ROOT/"knowledge/29_phcong_exp3_pcsup_preregistration_20261028.md"),"verdict":verdict,"screen":screen,"confirmation":confirm,"vs_celf_random_screen":vs_r,"vs_phcong_celf_screen":vs_p,"leakage_canary":{"passed":bool(canary["passed"]),"max_two_sided_auc":float(max_auc),"features":canary["features"]},"uniqueness":uniq,"format_audit":fmt,"raster_sha256":receipt["primary_zero_outside"]["sha256"],"nan_twin_sha256":receipt["official_text_nan_outside_twin"]["sha256"]}
    jw(ROOT/"evidence/a33_r7_pcsup_experiment_20261028.json",exp)
    card={"schema":1,"campaign":"A33-R7-PCSUP","date":DATE,"hypothesis":"Fold-safe HGB supervised only on PHCONG + potential-field/subsurface channels (no topo/LiDAR/radiometric) + CELF emission.","mechanism":"Learned fault-vs-intrusive weighting of amplitude-invariant basement edges under cover, targeting catalogue-missing blind faults.","named_non_fault_mimic":"Intrusive plutonic contacts and caldera margins learned as faults.","verdict":verdict,
      "holdout_dti":{"label":"HOLDOUT-DTI","evaluator_version":csht_transfer.MTR_EVALUATOR_VERSION,"withheld_positives":int(screen["n_withheld_positive_pixels"]),"screen":{"split_id":"quadrant-buffered-15px-v1","candidate":screen["dti"],"ci95":screen["ci95"]["interval"],"paired_delta_vs_matched_random":vs_r["paired_delta_dti"],"paired_delta_ci95":vs_r["paired_delta_ci95"],"fold_wins":vs_r["fold_wins"],"paired_delta_vs_phcong":vs_p["paired_delta_dti"],"paired_delta_vs_phcong_ci95":vs_p["paired_delta_ci95"]},"confirmation":{"split_id":"diagonal-wedge-buffered-20px-confirm-v1","candidate":confirm["dti"],"ci95":confirm["ci95"]["interval"]},"recorded_context_unpaired":{"B1_regional_screen":REC_B1_S,"B1_regional_confirm":REC_B1_C},"qualification":"Catalogue hide-and-recover proxy. NOT private organizer truth, NOT a competition score or projection."},
      "correlation_overlap_vs_registry":{"surface_max_abs_spearman":uniq["surface"]["max_abs_spearman_rho"],"surface_max_3px_overlap":uniq["surface"]["max_preview_fraction_within_3px"],"surface_passed":bool(uniq["surface"]["passed"]),"final_dots_max_abs_spearman":uniq["final_dots"]["max_abs_spearman_rho"],"final_dots_max_3px_overlap":uniq["final_dots"]["max_candidate_fraction_within_3px"],"final_dots_passed":bool(uniq["final_dots"]["passed"]),"scope":"21 pinned rasters"},
      "leakage_canary":{"passed":bool(canary["passed"]),"max_two_sided_auc":float(max_auc)},"raster_sha256":receipt["primary_zero_outside"]["sha256"],"nan_twin_sha256":receipt["official_text_nan_outside_twin"]["sha256"],
      "submission":{"file":receipt["primary_zero_outside"]["file"],"zip":receipt["primary_zero_outside"]["zip"],"note":receipt["note"],"name":receipt["submission_name"],"ok_to_submit":promote},
      "promotion_assessment":{"eligible_for_selector":promote,"verdict":verdict,"gates":{"screen_beats_recorded_b1_with_positive_ci":sg,"confirm_beats_recorded_b1_with_positive_ci":cg,"screen_beats_celf_random_positive_ci":rg,"screen_beats_phcong_positive_ci":pg,"surface_not_duplicate":bool(uniq["surface"]["passed"]),"final_dots_not_duplicate":bool(uniq["final_dots"]["passed"]),"format_audit_pass":bool(fmt["pass"]),"canary_pass":bool(canary["passed"])},"failed_gates":[k for k,v in {"screen_b1":sg,"confirm_b1":cg,"celf_random":rg,"phcong":pg,"uniqueness":uq,"format":bool(fmt["pass"])}.items() if not v]},"runtime_seconds":round(time.monotonic()-t0,2)}
    jw(ROOT/"evidence/a33_r7_pcsup_run_card_20261028.json",card); jw(ROOT/"docs/data/a33_r7_pcsup_run_card_20261028.json",card)
    print(json.dumps({"verdict":verdict,"screen":screen["dti"],"confirm":confirm["dti"],"promote":promote},indent=2))
if __name__=="__main__": raise SystemExit(main())
