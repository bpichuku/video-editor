---
name: finishing-pass
description: Stage 4. Adds captions (optional, off for long form), a flat music bed, and a few real sound effects to the graphics render, in that order, then runs the self-review loop with the watch skill via sub-agents (technical QA checklist, then a separate composition pass). Use after graphics, when asked for captions, music, SFX, or to review/QA/watch back a render.
---

# Finishing pass

Whole job: captions, a music bed, a few sound effects, then review.

Three sub-steps that can each run alone, but **always run in this order** when run together, because each operates on whatever the previous produced: captions, then music, then SFX. Read `brand.md` and the active style first.

## Captions

- Burn in from the **remapped transcript**, styled from the style file (caption font, weight, position, highlight).
- **Never caption a file that is already captioned.** The script picks its own input rather than accepting whatever it is handed.
- **Captions are genuinely optional.** Long form skips them entirely: YouTube serves its own and burn-ins clutter a 16:9 frame. This channel is long form and mostly voiceless, so default is off. Text shown on screen then comes from graphics cards, not captions.
- Font files from `assets/fonts/` (Nunito Black), never system fonts.

## Music

- Flat bed at about **-18 dB**. **No ducking, no fade-in**, a short fade-out on the tail.
- The track is **user-supplied and licensed**, from `projects/<job>/audio/`. **Never download one.**
- Ducking and fade-in exist only as opt-in flags and should almost never be used. **If the bed is not audible enough, change the level. Do not add a sidechain.**
- Keep the footage's ambient craft sound unless told otherwise (this channel keeps it).

## Sound effects

- **Sparse.** A handful of moments per video, not a hit on every cut.
- **Real sample files** at about **-10 dB**, from the job's `audio/sound-effects/` (copied from the top-level `sfx/sounds-effects/` library at job setup; if the job copy is missing, copy it first, never edit the library). The library is built up over time.
- **Never a synthesised tone.** A generated sine wave is instantly recognisable as not-a-sound-effect.
- **No samples? Skip the step.** Do not fabricate one. Tell the user the library is empty.

## Audio pass rules

- Music and SFX are **pure audio passes. Copy the video stream, never re-encode it** (`-c:v copy`).
- **Write the effects plan and the filter graph to disk** (in `graphics-build/`, not a new folder). When a later graphics tweak re-renders the base, **re-apply the exact same plan** rather than re-deciding every placement.

## Review loop: give it eyes

Claude cannot see video, only the transcript. That is why the rough cut is reliable and graphics come back with small issues. The `watch` skill pulls frames so Claude can look at any moment. The recipe is a goal (finish the video) plus a way to check the work (watch).

Loop: render finishes, sub-agents watch it back like a picky editor, return a **timestamped findings list**, Claude fixes, re-renders, reviews again, until it passes.

- **Use sub-agents, not the main session.** Frame dumps flood the context window. Send the review out, get findings back.
- **Use a frame-extraction skill (`watch`), not a video-understanding model.** Control: Claude decides exactly where to look, e.g. the seam between two specific graphics, instead of receiving a summary of the whole clip.
- Early spot review after the first 10% of the build (see `graphics`), then full review at the end.

### Two distinct passes, in this order

**Pass 1: technical QA (checklist).** Catches binary things: stretched asset, vanished element, wrong colour, brightness dip at a seam, duplicate-frame judder (exact duplicate frames under 3% is clean, around 25% is the overlay-repeat bug), black tails or bars, audio click at joins, graphics shown outside the safe zone (long form: 10% title-safe, right 40% clear in the outro).

**Pass 2: composition (its own named step, concrete items).** Judgment calls with no pass/fail ("why is that at the top", "that's tiny", "does this make sense") are skipped by a checklist reviewer even while looking straight at the frames that show them. So:

1. Re-check **every overlay against what the style file says for that element category**.
2. Account for **every distinct visual moment named in the direction** as *built* or *explicitly flagged as skipped*. Never silently simplified away.

Each finding: timestamp, what is wrong, which pass, proposed fix. The pass ends only when both come back clean.

Everything here reads the style fresh each pass, so corrections absorbed into the style file (see `export`) tighten every future review automatically.
