#!/usr/bin/env python3
"""Splice the Short from transcript/cutsheet.json in one FFmpeg filtergraph. Ambient audio on real-time segments only."""
import json, subprocess
from pathlib import Path
JOB = Path(__file__).resolve().parent.parent
cs = json.load(open(JOB / 'transcript' / 'cutsheet.json'))
W, H = cs['size']; SW = cs['src_size'][0]
TM = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p'
cmd = ['ffmpeg', '-y', '-v', 'error', '-stats']; vf = []; af = []; cat = ''; total = 0
for i, s in enumerate(cs['segments']):
    d = s['end'] - s['start']; out = d / s['speed']; total += out
    cmd += ['-hwaccel', 'videotoolbox', '-ss', str(s['start']), '-t', str(d), '-i', str(JOB / s['source'])]
    c = s['crop']
    if 'path' in c:
        p = c['path']; expr = str(round(p[-1][1] * SW - c['w'] / 2))
        for (t0, x0), (t1, x1) in reversed(list(zip(p, p[1:]))):
            a = x0 * SW - c['w'] / 2; b = x1 * SW - c['w'] / 2
            expr = f"if(lt(t\\,{t1})\\,{a:.2f}+({b - a:.2f})*(t-{t0})/({t1 - t0:.4f})\\,{expr})"
        xe = f"x='clip({expr}\\,0\\,{SW - c['w']})'"
    else:
        xe = f"x={c['x']}"
    vf.append(f"[{i}:v:0]setpts=(PTS-STARTPTS)/{s['speed']},fps=24,crop=w={c['w']}:h={c['h']}:{xe}:y={c['y']},scale={W}:{H}:flags=lanczos,{TM}[v{i}]")
    if s['speed'] <= 1: af.append(f"[{i}:a:1]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
    else: af.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{out:.4f},asetpts=PTS-STARTPTS[a{i}]")
    cat += f'[v{i}][a{i}]'
fc = ';'.join(vf + af) + f";{cat}concat=n={len(cs['segments'])}:v=1:a=1[v][a]"
cmd += ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-map_chapters', '-1', '-c:v', 'h264_videotoolbox', '-b:v', '14M', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(JOB / 'outputs' / 'base-cut.mp4')]
print(f'expected duration {total:.2f}s', flush=True)
subprocess.run(cmd, check=True)
