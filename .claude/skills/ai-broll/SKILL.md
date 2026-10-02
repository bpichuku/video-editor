---
name: ai-broll
description: Stage 3. Turns a beat that has no footage into a rendered silent clip (HyperFrames motion graphics only; no generative AI footage on this channel) and writes a manifest entry. Maps each slot to one of eight scene templates, applies the twelve motion-design rules, renders at the base's probed frame rate with half a second of tail margin. Does not pick windows in existing footage and does not composite. Use when a graphics plan has a b-roll slot, or when asked for motion-graphic B-roll, stat reveals, flowcharts, podiums, kinetic type, before/after.
---

# AI B-roll

Whole job: turn a beat that has no footage into a rendered clip.

What it does **not** do: it does not pick windows in footage already shot (that belongs to `graphics`), and it does not composite anything into the final video. It generates a clip and writes a manifest entry. Keeping generation separate from placement is what makes both debuggable.

Read `brand.md` and the active style first. Use tokens, not hex. Real fonts from `assets/fonts/`. **No Higgsfield and no generative AI footage or images on this channel (decided by the user).** Everything here is rendered locally with HyperFrames, so it costs nothing. Stage 3 is skipped by default and runs only when the user asks for a motion-graphic B-roll slot. If a beat would need an illustration HTML cannot draw, flag it to the user rather than generating one.

## Scene templates

Map every slot to one of eight templates **before** writing a prompt. Picking the right one up front is most of what stops output reading generic.

| The beat is about | Reach for |
|---|---|
| One big number landing | Stat reveal |
| Several categories at once | Data breakdown |
| Parts of a whole | Pie or donut |
| Things ranked | Podium |
| A system or process | Flowchart |
| "Look what showed up" | Phone notification |
| Old versus new | Before and after |
| Words as the payoff | Kinetic type |

## The twelve design rules

These separate motion design from PowerPoint. **Make at least half of them explicit in every single prompt** rather than hoping the render figures them out.

1. Text never just fades in. Clip-mask reveals, or word by word.
2. Nothing animates simultaneously. Stagger everything by at least 0.4 s.
3. The background is never flat. Gradient, vignette, or a fine grid.
4. The accent colour appears on exactly one element per scene.
5. Numbers count up or flip. They never just appear.
6. Exits are designed. Elements leave with purpose.
7. Generous whitespace. More than feels right.
8. One focal point per frame. Never more than two things moving.
9. Scale is dramatic. Primary numbers 160 px minimum.
10. Connectors and dividers draw in, never appear.
11. Small premium details. Thin highlights, low-opacity reflections.
12. Motion blur on fast travel, removed once settled.

### Failure list (the mirror image, reject any of these)

Same layout reused for every beat. "Fade in" instead of a real entrance. No stagger. Flat background. A vague ease like "smooth" instead of a **named** ease (e.g. `power3.out`). Small type. No exits. Too many colours. Everything moving at once.

## Render rules

- **Frame rate: the base video's exact rate, probed with `ffprobe`, never guessed.** If the base is 23.976 pass `24000/1001`, not 24. A rounded guess drifts out of sync once composited.
- **Every generated clip is silent.** The base audio keeps playing underneath. If a render produces an audio stream anyway, strip it (`-an`) before writing the manifest.
- **Duration = beat window + 0.5 s tail margin.** A clip that ends exactly on its boundary is a bug waiting for the next composite.
- For HyperFrames-rendered templates, obey the full HyperFrames timeline contract and silent-render traps in the `graphics` skill (seeked timelines, from-to tweens, no CSS blur, no emoji glyphs, no near-zero tweens).
- Pin `npx hyperframes@0.8.107`.

## Output

Write the clip into the job (`graphics-build/` for source, heavy renders to cache) and append a manifest entry: beat ID, template used, path, probed fps, duration, and confirmation that audio was stripped. Stop there. Placement and compositing belong to `graphics`.
