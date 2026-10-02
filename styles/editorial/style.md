# Style: editorial (starter)

STATUS: starter, written without a reference video. Per the playbook, a style is only done when new videos can be made from this file alone. Treat every section marked TODO-REFERENCE as provisional, and rebuild them with the two-pass reference method (see the graphics skill) once Priya picks a reference video. Corrections from reviews get absorbed into `style.json` `learned` and this file.

Formats: long form 16:9 (1920x1080). Colours are tokens from brand.md (`$bg`, `$ink`, `$accent`...). Never hardcode hex.

## What this look is

A cream paper desk. Hand-made warmth, rounded type, one terracotta-coral accent per scene, sage for labels. The footage is silent craft process, so on-screen text does the storytelling.

## Scene vocabulary

| Scene | What it is |
|---|---|
| Plain | Footage only, no graphic. Default. Lets the craft breathe. |
| Hook card | Opening text over the first footage, `$ink` Fredoka, one accent word. |
| Step card | Short chatty label for a process step, lower-left, "step 2: glue the petals". |
| Stat | One big number or measurement ("3 hours", "12 petals"), count-up. |
| Takeover | Full-frame text or diagram on `$bg` paper texture, replaces the footage. |
| Zoom | Footage push-in on a detail (FFmpeg, not browser). |
| B-roll slot | AI or motion graphic clip for a beat with no footage. |

## Transitions at each boundary

- Footage to footage: hard cut, on the beat of the music.
- Footage to card: card enters with a clip-mask reveal (no plain fade), 0.4s stagger between elements.
- Card to card: hard cut of content inside the same card frame (never a full-screen bounce).
- Footage to takeover: wipe from the left in `$accent-soft`, 0.35s.
- Takeover back to footage: reverse wipe, 0.35s.

TODO-REFERENCE: verify these against a reference at high frame rate.

## Title card anatomy

- Display font Fredoka SemiBold, 120px minimum for the headline, `$ink`.
- One word per title in `$accent`.
- Sub-label in Nunito Black 40px, `$muted`, letter-spaced, sits 24px under the headline.
- Thin `$rule` hairline draws in under the block (draws, never appears).
- Everything inside the 10% title-safe margin.

## Picture-in-picture

Not applicable (voiceless, no talking head). If a face-cam is ever added, geometry goes here: TODO-REFERENCE.

## Camera behaviour inside a scene

Slow push of 4 to 6 percent over the scene on detail shots. No shake, no whip pans. Zoom ramps start from a reset frame counter (see graphics skill).

## Texture

`$bg` base with 6% paper grain overlay and a faint `$accent-soft` vignette in the corners. Backgrounds are never flat.

## Fonts and jobs

- Fredoka: titles, stats, kinetic type.
- Nunito Black: step labels, sub-labels, optional captions.

## Pacing (provisional)

- A graphic on roughly one beat in four. Most beats stay plain.
- Cards hold at least 2.5 seconds so the text reads, then hold until the next part starts.
- Beats of 20 seconds or more carry continuous motion for the whole duration.

TODO-REFERENCE: replace with measured pacing from the reference.

## Captions

Off by default (long form). If turned on: Nunito Black 900, 4 words max per line, lower-third inside title-safe, `$ink` on a `$bg` pill, one `$accent` highlight word.

## Audio

Music is user-supplied and licensed. Flat bed at -18 dB, no ducking, no fade-in, 1.5s fade-out. Keep ambient craft sounds from the footage. SFX sparse, real samples from `assets/sfx/` at -10 dB.
