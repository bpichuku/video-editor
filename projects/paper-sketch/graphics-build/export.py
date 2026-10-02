#!/usr/bin/env python3
"""Export for this job. Dry run unless --apply is passed after reading the plan.
Promote: outputs/finished.mp4 -> outputs/<job>.mp4 (+ copy to ~/Downloads).
Retire: superseded drafts in outputs/ (graphics.mp4). Keep: base-cut.mp4, remapped transcript, transcript/, graphics-build source.
Reclaim (separate, --reclaim): graphics-build/renders/*.mov and parts/ (regenerable by build.py). Never raw/, broll/, audio/ or outputs/."""
import sys, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
JOB = H.parent
NAME = JOB.name
OUT = JOB / 'outputs'
SRC = OUT / 'finished.mp4'
FINAL = OUT / f'{NAME}.mp4'
DL = Path.home() / 'Downloads' / f'{NAME}.mp4'
apply = '--apply' in sys.argv
reclaim = '--reclaim' in sys.argv

if not SRC.exists() and not FINAL.exists(): sys.exit('no render to promote')
deliverable = SRC if SRC.exists() else FINAL
newest = deliverable.stat().st_mtime

def safe_to_delete(p):
    # guard lives here on purpose: never delete anything newer than the deliverable
    return p.stat().st_mtime <= newest

retire = [OUT / 'graphics.mp4']
keep = [OUT / 'base-cut.mp4', OUT / 'transcript-remapped.json', JOB / 'transcript', H]
reclaim_targets = list((H / 'renders').glob('*.mov')) + ([H / 'parts'] if (H / 'parts').exists() else [])

plan = []
if SRC.exists(): plan.append(f'PROMOTE  {SRC.name} -> {FINAL.name}')
plan.append(f'COPY     {FINAL.name} -> {DL}')
for p in retire:
    if p.exists(): plan.append(('RETIRE   ' if safe_to_delete(p) else 'SKIP (newer than deliverable)  ') + str(p.relative_to(JOB)))
for p in keep: plan.append(f'KEEP     {p.relative_to(JOB)}')
if reclaim:
    for p in reclaim_targets:
        plan.append(('RECLAIM  ' if safe_to_delete(p) else 'SKIP (newer than deliverable)  ') + str(p.relative_to(JOB)))
print('\n'.join(plan))
if not apply:
    print('\nDRY RUN: nothing changed. Re-run with --apply after reading the plan.'); sys.exit(0)

if SRC.exists(): SRC.rename(FINAL)
DL.parent.mkdir(exist_ok=True); shutil.copy2(FINAL, DL)
for p in retire:
    if p.exists() and safe_to_delete(p): p.unlink()
if reclaim:
    for p in reclaim_targets:
        if p.exists() and safe_to_delete(p): shutil.rmtree(p) if p.is_dir() else p.unlink()
print('applied')
