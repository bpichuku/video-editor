#!/usr/bin/env python3
"""Graphics build for paper-sketch. Subcommands: validate | build | render [id...] | assemble
Reads brand.md for colour tokens, assets/fonts for fonts and assets/lib/gsap.min.js (GSAP 3.14.2) for animation. Run from anywhere."""
import json, re, subprocess, sys, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOB = HERE.parent
ROOT = JOB.parent.parent
HF = ['npx', 'hyperframes@0.8.107']
ALLOWED = {'stat', 'card', 'screenshot', 'takeover', 'zoom', 'diagram', 'broll-slot'}
TAIL = 0.5

def load_beats():
    return json.load(open(HERE / 'beats.json'))

def tokens():
    md = (ROOT / 'brand.md').read_text()
    return json.loads(re.search(r'```json\n(.*?)\n```', md, re.S).group(1))

def validate(beats):
    errs = []
    last_end = None
    for b in beats:
        for f in ('id', 'start', 'end', 'kind', 'direction'):
            if f not in b: errs.append(f"{b.get('id','?')}: missing {f}")
        if b.get('kind') not in ALLOWED: errs.append(f"{b['id']}: kind {b.get('kind')} not allowed")
        if b['start'] >= b['end']: errs.append(f"{b['id']}: start >= end")
        if b['end'] - b['start'] < 2.5 and b['kind'] == 'card': errs.append(f"{b['id']}: card shorter than 2.5 s")
        if last_end is not None:
            gap = b['start'] - last_end
            if gap < 0: errs.append(f"{b['id']}: overlaps/unsorted ({gap:.2f})")
            elif 0 < gap <= 1.0: errs.append(f"{b['id']}: gap {gap:.2f}s to previous (must abut or be >1s)")
        last_end = b['end']
    return errs

CSS = """
@font-face{font-family:Fredoka;src:url('fonts/Fredoka-Variable.ttf');font-weight:300 700}
@font-face{font-family:Nunito;src:url('fonts/Nunito-Variable.ttf');font-weight:200 1000}
:root{%(vars)s}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:transparent}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}
.panel{position:absolute;overflow:hidden;background:var(--bg);border:3px solid var(--rule);border-radius:36px;white-space:nowrap}
.inner{padding:44px 64px 52px 64px;position:relative}
.mask{overflow:hidden;display:block;padding-bottom:36px;margin-bottom:-36px}
.display{font-family:Fredoka,sans-serif;font-weight:600;color:var(--ink);line-height:1.04;display:block}
.label{font-family:Nunito,sans-serif;font-weight:900;color:var(--muted);letter-spacing:.14em;display:block}
.acc{color:var(--accent)}
.rule{height:6px;border-radius:3px;background:var(--rule);width:0}
.strip{position:absolute;left:0;top:0;bottom:0;width:22px;background:var(--accent-soft)}
.badge{display:inline-flex;align-items:center;justify-content:center;width:96px;height:96px;border-radius:48px;background:var(--accent);color:var(--bg);font-family:Fredoka,sans-serif;font-weight:600;font-size:56px;margin-right:36px;vertical-align:middle}
"""

def js_common(dur, beat_dur):
    return f"""
const tl=gsap.timeline({{paused:true}});
window.__timelines=window.__timelines||{{}};
function headline(t){{return t}}
"""

def accent(text, word):
    if word and word in text:
        return text.replace(word, f'<span class="acc">{word}</span>', 1)
    return text

def wrap(b, body, script, vars_css):
    dur = round(b['end'] - b['start'] + TAIL, 3)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="gsap.min.js"></script>
<style>{CSS % {'vars': vars_css}}</style></head>
<body><div id="root" data-composition-id="{b['id']}" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080" data-fps="24">
{body}
</div>
<script>
const tl=gsap.timeline({{paused:true}});
const D={round(b['end']-b['start'],3)};
{script}
// hard kill at the beat end, then stay clear through the tail margin
tl.fromTo('#root',{{opacity:1}},{{opacity:0,duration:0.2,ease:'none',immediateRender:false}},D-0.2);
window.__timelines=window.__timelines||{{}};window.__timelines['{b['id']}']=tl;
</script></body></html>"""

def card_entrance(W):
    return f"tl.fromTo('#panel',{{width:0,opacity:0}},{{width:{W},opacity:1,duration:0.45,ease:'power3.out'}},0.0);"

def card_exit(W):
    return f"tl.fromTo('#panel',{{width:{W}}},{{width:0,duration:0.4,ease:'power3.in',immediateRender:false}},D-0.4);"

# measured: Fredoka 600 is ~0.47em per character; widths below add padding and a safety margin
# Nunito Black labels with .14em tracking run ~0.68em per character
def text_w(text, px):
    return int(len(text) * px * 0.47) + 24

def check_safe(b, W):
    assert 192 + W <= 1728, f"{b['id']}: card would leave the title-safe zone ({192 + W}px)"

def build_hook(b, v):
    W = 84 + int(len(b['text']) * 120 * 0.5) + 24 + 64
    check_safe(b, W)
    body = f"""<div class="panel" id="panel" style="left:192px;bottom:108px;width:{W}px;height:268px"><div class="strip"></div><div class="inner" style="padding:30px 64px 30px 84px">
<span class="mask"><span class="display" id="l1" style="font-size:120px">Let's make {accent('something', b['accent_word'])}</span></span>
<span class="mask" style="margin-top:12px"><span class="label" id="sub" style="font-size:40px">{b['sub']}</span></span>
<div class="rule" id="rule" style="margin-top:14px"></div></div></div>"""
    s = f"""
{card_entrance(W)}
tl.fromTo('#l1',{{y:170}},{{y:0,duration:0.5,ease:'power3.out'}},0.4);
tl.fromTo('#sub',{{y:60}},{{y:0,duration:0.45,ease:'power3.out'}},0.8);
tl.fromTo('#rule',{{width:0}},{{width:760,duration:0.7,ease:'power2.inOut'}},1.2);
{card_exit(W)}
"""
    return body, s

def build_step(b, v):
    n = re.search(r'\d+', b['label']).group(0)
    W = 70 + 80 + 30 + text_w(b['text'], 60) + 64
    check_safe(b, W)
    body = f"""<div class="panel" id="panel" style="left:192px;bottom:108px;width:{W}px;height:176px"><div class="strip"></div><div class="inner" style="padding:20px 64px 20px 70px">
<div style="display:flex;align-items:center"><span class="badge" id="badge" style="width:80px;height:80px;border-radius:40px;font-size:46px;margin-right:30px">{n}</span>
<div><span class="mask"><span class="label" id="lab" style="font-size:28px">{b['label']}</span></span>
<span class="mask"><span class="display" id="txt" style="font-size:60px">{accent(b['text'], b['accent_word'])}</span></span></div></div>
<div class="rule" id="rule" style="margin-top:12px"></div></div></div>"""
    s = f"""
{card_entrance(W)}
tl.fromTo('#lab',{{y:60}},{{y:0,duration:0.4,ease:'power3.out'}},0.4);
tl.fromTo('#badge',{{scale:0}},{{scale:1,duration:0.4,ease:'back.out(1.6)'}},0.8);
tl.fromTo('#txt',{{y:110}},{{y:0,duration:0.45,ease:'power3.out'}},0.8);
tl.fromTo('#rule',{{width:0}},{{width:{int(W*0.6)},duration:0.7,ease:'power2.inOut'}},1.2);
{card_exit(W)}
"""
    return body, s

def build_stat(b, v):
    W = 900
    body = f"""<div class="panel" id="panel" style="left:192px;bottom:108px;width:{W}px;height:236px"><div class="strip"></div><div class="inner" style="padding:14px 64px 14px 80px">
<div style="display:flex;align-items:baseline"><span class="display acc" id="num" style="font-size:150px">0</span>
<span class="mask" style="margin-left:24px"><span class="display" id="unit" style="font-size:64px">{b['unit']}</span></span></div>
<span class="mask"><span class="label" id="sub" style="font-size:34px">{b['sub']}</span></span>
<div class="rule" id="rule" style="margin-top:12px"></div></div></div>"""
    s = f"""
const counter={{v:0}};
{card_entrance(W)}
tl.fromTo(counter,{{v:0}},{{v:{b['number']},duration:1.0,ease:'power2.out',onUpdate:()=>{{document.getElementById('num').textContent=String(Math.round(counter.v))}}}},0.4);
tl.fromTo('#unit',{{y:120}},{{y:0,duration:0.45,ease:'power3.out'}},0.8);
tl.fromTo('#sub',{{y:60}},{{y:0,duration:0.4,ease:'power3.out'}},1.2);
tl.fromTo('#rule',{{width:0}},{{width:520,duration:0.7,ease:'power2.inOut'}},1.4);
{card_exit(W)}
"""
    return body, s

def build_outro(b, v):
    W = 84 + max(text_w(b['text'], 112), int(len(b['sub']) * 36 * 0.68) + 24) + 64
    check_safe(b, W)
    body = f"""<div class="panel" id="panel" style="left:192px;bottom:108px;width:{W}px;height:236px"><div class="strip"></div><div class="inner" style="padding:20px 64px 20px 84px">
<span class="mask"><span class="display" id="l1" style="font-size:112px">{accent(b['text'], b['accent_word'])}</span></span>
<span class="mask" style="margin-top:6px"><span class="label" id="sub" style="font-size:36px">{b['sub']}</span></span>
<div class="rule" id="rule" style="margin-top:12px"></div></div></div>"""
    s = f"""
{card_entrance(W)}
tl.fromTo('#l1',{{y:190}},{{y:0,duration:0.5,ease:'power3.out'}},0.4);
tl.fromTo('#sub',{{y:60}},{{y:0,duration:0.45,ease:'power3.out'}},0.8);
tl.fromTo('#rule',{{width:0}},{{width:520,duration:0.7,ease:'power2.inOut'}},1.2);
{card_exit(W)}
"""
    return body, s

def build_all():
    cfg = load_beats(); beats = cfg['beats']
    errs = validate(beats)
    if errs: sys.exit('VALIDATION FAILED:\n' + '\n'.join(errs))
    v = tokens()
    vars_css = ';'.join(f'--{k}:{val}' for k, val in v.items())
    builders = {'hook': build_hook, 'step': build_step, 'stat': build_stat, 'outro': build_outro}
    shutil.rmtree(HERE / 'parts', ignore_errors=True)
    for b in beats:
        key = 'step' if b['id'].startswith('step') else b['id']
        body, script = builders[key](b, v)
        html = wrap(b, body, script, vars_css)
        d = HERE / 'parts' / b['id']; d.mkdir(parents=True)
        (d / 'index.html').write_text(html)
        (d / 'hyperframes.json').write_text('{}')
        (d / 'fonts').mkdir()
        for f in ('Fredoka-Variable.ttf', 'Nunito-Variable.ttf'): shutil.copy(ROOT / 'assets' / 'fonts' / f, d / 'fonts' / f)
        shutil.copy(ROOT / 'assets' / 'lib' / 'gsap.min.js', d / 'gsap.min.js')
        print('built', b['id'])

def render(ids):
    cfg = load_beats()
    for b in cfg['beats']:
        if ids and b['id'] not in ids: continue
        out = HERE / 'renders' / f"{b['id']}.mov"; out.parent.mkdir(exist_ok=True)
        subprocess.run(HF + ['render', str(HERE / 'parts' / b['id']), '--format', 'mov', '--fps', '24', '-o', str(out), '--quiet'], check=True)
        print('rendered', out.name)

def probe(path, entry):
    return subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', f'stream={entry}', '-of', 'csv=p=0', str(path)], text=True).strip()

def dup_pct(path):
    # frames mpdecimate would drop, as a share of all frames
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-vf', 'mpdecimate=hi=64*12:lo=64*5:frac=0.33,showinfo', '-f', 'null', '-'], capture_output=True, text=True)
    import re as _re
    kept = len(_re.findall(r'Parsed_showinfo\S* @ \S+\] n:\s*\d+', r.stderr)); total = int(probe(path, 'nb_frames') or 0)
    return 100.0 * (total - kept) / total if total else 0.0

def assemble():
    cfg = load_beats(); base = (HERE / cfg['base']).resolve()
    rate = probe(base, 'r_frame_rate')
    assert rate == '24/1', f'base is {rate}, expected 24/1'
    ins = ['-i', str(base)]; chain = []; prev = '[0:v]'
    for i, b in enumerate(cfg['beats'], 1):
        ins += ['-i', str(HERE / 'renders' / f"{b['id']}.mov")]
        chain.append(f"[{i}:v]format=yuva420p,setpts=PTS-STARTPTS+{b['start']}/TB[o{i}]")
        chain.append(f"{prev}[o{i}]overlay=eof_action=pass:format=auto[m{i}]")
        prev = f'[m{i}]'
    out = JOB / 'outputs' / 'graphics.mp4'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-stats'] + ins + ['-filter_complex', ';'.join(chain) + f';{prev}format=yuv420p[v]',
           '-map', '[v]', '-map', '0:a', '-c:v', 'h264_videotoolbox', '-b:v', '16M', '-c:a', 'copy', '-r', '24', '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)
    d_base, d_out = dup_pct(base), dup_pct(out)
    print(f'duplicate frames: base {d_base:.1f}%  graphics {d_out:.1f}%')
    if d_out > 8 or d_out - d_base > 5: sys.exit('FAIL: duplicate-frame check (overlay frame scheduler bug)')
    print('OK', out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'validate':
        e = validate(load_beats()['beats']); print('\n'.join(e) or 'beats valid'); sys.exit(1 if e else 0)
    elif cmd == 'build': build_all()
    elif cmd == 'render': render(sys.argv[2:])
    elif cmd == 'assemble': assemble()
    else: sys.exit(__doc__)
