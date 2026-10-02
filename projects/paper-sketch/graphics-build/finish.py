#!/usr/bin/env python3
"""Audio pass from audio-plan.json: copy video, mix footage ambient + looped music bed + optional sample SFX + optional real footage sounds. Audio encoded once."""
import json, subprocess
from pathlib import Path
H = Path(__file__).resolve().parent
P = json.load(open(H / 'audio-plan.json'))
def dur_of(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], text=True))
src = (H / P['input']).resolve(); dur = dur_of(src)
music = (H / P['music']['file']).resolve(); m = P['music']
ins = ['-i', str(src), '-i', str(music)]
mute = ''.join(f",volume=0:enable='gte(t,{x['from']})'" for x in P.get('ambient_mute', []))
f = [f"[0:a]aresample=48000,aformat=channel_layouts=stereo{mute}[amb]"]
start = m.get('start_s', 0)
base = "[1:a]aresample=48000,aformat=channel_layouts=stereo"
if m.get('loop'):
    lp = m['loop']; L = dur_of(music); beat = 60.0 / lp['bpm']
    first_len = lp['first_play_beats'] * beat; xf = lp['crossfade_beats'] * beat; c = lp.get('curve', 'tri')
    ins += ['-i', str(music)]                      # second play as its own input (asplit + acrossfade truncates)
    f.append(f"{base},atrim=0:{first_len:.4f},asetpts=PTS-STARTPTS[m1]")
    f.append(f"[2:a]aresample=48000,aformat=channel_layouts=stereo[m2]")
    f.append(f"[m1][m2]acrossfade=d={xf:.4f}:c1={c}:c2={c}[ml]")
    src_lab = '[ml]'
    print(f'music loop: first play {first_len:.3f}s, crossfade {xf:.3f}s, seam at video {first_len - xf:.3f}s, total {first_len + L - xf:.1f}s')
else:
    f.append(f"{base}[ml]"); src_lab = '[ml]'
f.append(f"{src_lab}atrim={start}:{start + dur:.3f},asetpts=PTS-STARTPTS,volume={m['db']}dB,afade=t=out:st={dur - m['fade_out_s']:.3f}:d={m['fade_out_s']}[mus]")
labels = '[amb][mus]'; n = 3 if m.get('loop') else 2
for s in P.get('sfx', []):
    ins += ['-i', str((H / s['file']).resolve())]; ms = int(s['at'] * 1000)
    trim = f",atrim=0:{s['trim_s']},asetpts=PTS-STARTPTS,afade=t=out:st={s['trim_s'] - s['fade_out_s']}:d={s['fade_out_s']}" if 'trim_s' in s else ''
    f.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo{trim},volume={P['sfx_db']}dB,adelay={ms}|{ms}[x{n}]"); labels += f'[x{n}]'; n += 1
for c in P.get('footage_audio', []):
    ins += ['-ss', str(c['from_s']), '-t', str(c['dur_s']), '-i', str((H / c['source']).resolve())]; ms = int(c['at'] * 1000)
    f.append(f"[{n}:a:{c['audio_stream']}]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,afade=t=in:d={c['fade_in_s']},afade=t=out:st={c['dur_s'] - c['fade_out_s']}:d={c['fade_out_s']},volume={c['gain_db']}dB,adelay={ms}|{ms}[x{n}]"); labels += f'[x{n}]'; n += 1
f.append(f"{labels}amix=inputs={labels.count("[")}:duration=first:normalize=0:dropout_transition=0,alimiter=limit=0.95[a]")
out = (H / P['output']).resolve()
cmd = ['ffmpeg', '-y', '-v', 'error'] + ins + ['-filter_complex', ';'.join(f), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)]
subprocess.run(cmd, check=True)
print('wrote', out)
