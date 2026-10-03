#!/usr/bin/env python3
"""Short-form graphics build. Subcommands: validate | build | render | assemble
One hook card at 1080x1920. Reads brand.md for tokens, assets/fonts for fonts and assets/lib/gsap.min.js for animation."""
import json, re, subprocess, sys, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent; JOB = HERE.parent; ROOT = JOB.parent.parent
HF = ['npx', 'hyperframes@0.8.107']; TAIL = 0.0   # the card ends exactly at the cut (4.8 s), no exit animation
def cfg(): return json.load(open(HERE / 'beats.json'))
def tokens(): return json.loads(re.search(r'```json\n(.*?)\n```', (ROOT / 'brand.md').read_text(), re.S).group(1))
def validate(beats):
    e = []
    if len(beats) != 1: e.append('short form allows exactly one graphic (the hook card)')
    for b in beats:
        if b['kind'] != 'card': e.append(f"{b['id']}: only a card is allowed in the short style")
        if b['end'] - b['start'] < 2.5: e.append(f"{b['id']}: card shorter than 2.5 s")
    return e
CSS = """
@font-face{font-family:Fredoka;src:url('fonts/Fredoka-Variable.ttf');font-weight:300 700}
@font-face{font-family:Nunito;src:url('fonts/Nunito-Variable.ttf');font-weight:200 1000}
:root{%(vars)s}
*{box-sizing:border-box}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}
.panel{position:absolute;overflow:hidden;background:var(--bg);border:3px solid var(--rule);border-radius:36px;white-space:nowrap}
.inner{padding:30px 64px 34px 84px;position:relative}
.mask{overflow:hidden;display:block;padding-bottom:36px;margin-bottom:-36px;padding-right:16px;margin-right:-16px}
.display{font-family:Fredoka,sans-serif;font-weight:600;color:var(--ink);line-height:1.04;display:block}
.label{font-family:Nunito,sans-serif;font-weight:900;color:var(--muted);letter-spacing:.14em;display:block}
.acc{color:var(--accent)}
.rule{height:6px;border-radius:3px;background:var(--rule);width:0}
.strip{position:absolute;left:0;top:0;bottom:0;width:22px;background:var(--accent-soft)}
"""
def build():
    c = cfg(); errs = validate(c['beats'])
    if errs: sys.exit('VALIDATION FAILED:\n' + '\n'.join(errs))
    v = tokens(); vars_css = ';'.join(f'--{k}:{x}' for k, x in v.items())
    b = c['beats'][0]; D = round(b['end'] - b['start'], 3); dur = round(D + TAIL, 3)
    SUBW = 718   # measured: the sub-label at 36 px is 718 px wide
    W = 84 + max(int(len(b['line1']) * 110 * 0.5), SUBW) + 64
    assert 60 + W <= 1080 - 60, f'card leaves the 60 px side margins ({60 + W}px)'
    l2 = b['line2'].replace(b['accent_word'], f'<span class="acc">{b["accent_word"]}</span>', 1)
    body = f"""<div class="panel" id="panel" style="left:60px;bottom:330px;width:{W}px;height:380px"><div class="strip"></div><div class="inner">
<span class="mask"><span class="display" id="l1" style="font-size:110px">{b['line1']}</span></span>
<span class="mask"><span class="display" id="l2" style="font-size:110px">{l2}</span></span>
<span class="mask" style="margin-top:10px"><span class="label" id="sub" style="font-size:36px">{b['sub']}</span></span>
<div class="rule" id="rule" style="margin-top:14px"></div></div></div>"""
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="gsap.min.js"></script><style>{CSS % {'vars': vars_css}}</style></head>
<body><div id="root" data-composition-id="hook" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920" data-fps="24">
{body}
</div><script>
const tl=gsap.timeline({{paused:true}}); const D={D};
tl.fromTo('#panel',{{width:0}},{{width:{W},duration:0.45,ease:'power3.out'}},0.0);
tl.fromTo('#panel',{{opacity:0}},{{opacity:1,duration:0.06,ease:'none',immediateRender:true}},0.0);
tl.fromTo('#l1',{{y:170}},{{y:0,duration:0.5,ease:'power3.out'}},0.08);
tl.fromTo('#l2',{{y:170}},{{y:0,duration:0.5,ease:'power3.out'}},0.48);
tl.fromTo('#sub',{{y:120}},{{y:0,duration:0.45,ease:'power3.out'}},0.88);
tl.fromTo('#rule',{{width:0}},{{width:{SUBW},duration:0.7,ease:'power2.inOut'}},1.28);
window.__timelines=window.__timelines||{{}};window.__timelines['hook']=tl;
</script></body></html>"""
    shutil.rmtree(HERE / 'parts', ignore_errors=True); d = HERE / 'parts' / 'hook'; (d / 'fonts').mkdir(parents=True)
    (d / 'index.html').write_text(html); (d / 'hyperframes.json').write_text('{}')
    for f in ('Fredoka-Variable.ttf', 'Nunito-Variable.ttf'): shutil.copy(ROOT / 'assets' / 'fonts' / f, d / 'fonts' / f)
    shutil.copy(ROOT / 'assets' / 'lib' / 'gsap.min.js', d / 'gsap.min.js'); print('built hook, panel width', W)
def render():
    out = HERE / 'renders' / 'hook.mov'; out.parent.mkdir(exist_ok=True)
    subprocess.run(HF + ['render', str(HERE / 'parts' / 'hook'), '--format', 'mov', '--fps', '24', '-o', str(out), '--quiet'], check=True); print('rendered', out)
def probe(p, e): return subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', f'stream={e}', '-of', 'csv=p=0', str(p)], text=True).strip()
def dup_pct(p):
    import re as _re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(p), '-vf', 'mpdecimate=hi=64*12:lo=64*5:frac=0.33,showinfo', '-f', 'null', '-'], capture_output=True, text=True)
    kept = len(_re.findall(r'Parsed_showinfo\S* @ \S+\] n:\s*\d+', r.stderr)); tot = int(probe(p, 'nb_frames') or 0)
    return 100.0 * (tot - kept) / tot if tot else 0.0
def assemble():
    c = cfg(); base = (HERE / c['base']).resolve(); assert probe(base, 'r_frame_rate') == '24/1'
    b = c['beats'][0]; out = JOB / 'outputs' / 'graphics.mp4'
    fc = f"[1:v]format=yuva420p,setpts=PTS-STARTPTS+{b['start']}/TB[o];[0:v][o]overlay=eof_action=pass:format=auto,format=yuv420p[v]"
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(base), '-i', str(HERE / 'renders' / 'hook.mov'), '-filter_complex', fc, '-map', '[v]', '-map', '0:a', '-c:v', 'h264_videotoolbox', '-b:v', '14M', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-c:a', 'copy', '-r', '24', '-movflags', '+faststart', str(out)], check=True)
    db, do = dup_pct(base), dup_pct(out); print(f'duplicate frames: base {db:.1f}%  graphics {do:.1f}%')
    if do - db > 5: sys.exit('FAIL: duplicate-frame check'); 
    print('OK', out)
if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else 'build'
    {'validate': lambda: print('\n'.join(validate(cfg()['beats'])) or 'beats valid'), 'build': build, 'render': render, 'assemble': assemble}.get(k, lambda: sys.exit(__doc__))()
