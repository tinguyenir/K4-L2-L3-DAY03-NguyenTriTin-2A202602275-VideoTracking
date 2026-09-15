"""Recompute report evidence without changing annotations or reference files."""
import hashlib
import json
from pathlib import Path

from motlib import EPS, by_frame, by_track, clear_mot, hota, identity, iou, maximise, parse_mot
from evaluate_tracking import diagnose

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    'gold': 'data/gold/gold/clip01/gt.txt',
    'pre': 'evidence/pre-gold/clip_01/gt.txt',
    'me': 'annotations/clip_01/gt.txt',
    'warmup': 'annotations/clip_02/gt.txt',
    'bt': 'outputs/model_bytetrack_clip_01.txt',
    'reid': 'outputs/model_reid_clip_01.txt',
}


def assignments(gt, pred):
    gf, pf = by_frame(gt), by_frame(pred)
    previous, result = {}, {}
    for frame in sorted(set(gf) | set(pf)):
        gs, ps = gf.get(frame, []), pf.get(frame, [])
        score = [[(1000 if previous.get(g.track_id) == p.track_id else 0) + iou(g, p)
                  if iou(g, p) >= 0.5 - EPS else 0 for p in ps] for g in gs]
        pairs = [(i, j) for i, j in maximise(score) if score[i][j] > EPS]
        previous = {gs[i].track_id: ps[j].track_id for i, j in pairs}
        for g in gs:
            best = max(ps, key=lambda p: iou(g, p), default=None)
            matched = next((ps[j] for i, j in pairs if gs[i] == g), None)
            result[frame, g.track_id] = {
                'matched_id': matched.track_id if matched else None,
                'matched_iou': round(iou(g, matched), 6) if matched else None,
                'best_id': best.track_id if best else None,
                'best_iou': round(iou(g, best), 6) if best else 0,
            }
    return result


def main():
    ds = {k: parse_mot(ROOT / v) for k, v in PATHS.items()}
    summary = {k: {'path': PATHS[k], 'sha256': hashlib.sha256((ROOT / PATHS[k]).read_bytes()).hexdigest(),
                   'rows': len(v), 'frames': len(by_frame(v)), 'tracks': len(by_track(v)),
                   'track_spans': {tid: [dets[0].frame, dets[-1].frame] for tid, dets in by_track(v).items()}}
               for k, v in ds.items()}
    manifest = json.loads((ROOT / 'evidence/pre-gold/clip_01/manifest.json').read_text(encoding='utf-8'))
    assert summary['pre']['sha256'] == manifest['sha256']
    evaluations = {}
    for name, pred, gt in [('pre_gold', 'pre', 'gold'), ('vs_gold', 'me', 'gold'),
                           ('bytetrack_vs_gold', 'bt', 'gold'), ('reid_vs_gold', 'reid', 'gold'),
                           ('reid_vs_me', 'reid', 'me')]:
        stored = json.loads((ROOT / f'outputs/eval_{name}.json').read_text(encoding='utf-8'))
        clear = clear_mot(ds[gt], ds[pred])
        metrics = {**hota(ds[gt], ds[pred]), **identity(ds[gt], ds[pred]),
                   **{k: v for k, v in clear.items() if k not in ('switches', 'matched_per_gt_track')}}
        metrics = {k: round(v, 4) if isinstance(v, float) else v for k, v in metrics.items()}
        assert metrics == stored['metrics'], name
        assert json.loads(json.dumps(diagnose(ds[gt], ds[pred], clear, 0.5))) == stored['diagnostics'], name
        evaluations[name] = 'all metrics and diagnostics match recomputation'
    maps = {k: assignments(ds['gold'], ds[k]) for k in ['pre', 'me', 'bt', 'reid']}
    frames = sorted(set(range(78, 114)) | set(range(137, 141)) | set(range(167, 172)) | set(range(55, 61)))
    records = [{'frame': f, 'gold_track': tid, **{k: m[f, tid] for k, m in maps.items()}}
               for f, tid in maps['me'] if f in frames]
    pre = {(d.frame, d.track_id): d for d in ds['pre']}
    changes = [{'frame': d.frame, 'annotation_id': d.track_id,
                'before_bbox_xywh': [pre[d.frame, d.track_id].x, pre[d.frame, d.track_id].y,
                                     pre[d.frame, d.track_id].w, pre[d.frame, d.track_id].h],
                'after_bbox_xywh': [d.x, d.y, d.w, d.h]}
               for d in ds['me'] if d != pre[d.frame, d.track_id]]
    result = {'method': 'CLEAR temporal one-to-one matching; IoU >= 0.5; MOT frames start at 1',
              'inputs': summary, 'verification': evaluations, 'changed_rows': changes, 'frame_evidence': records}
    (ROOT / 'reports/report_evidence.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Verified five evaluations, locked hash, and temporal frame assignments.')


if __name__ == '__main__':
    main()
