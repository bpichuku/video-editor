# Style: short (draft)

STATUS: draft, written without a reference video. Built from the editorial look (brand.md tokens, Fredoka and Nunito) plus the short-form rules in the graphics skill. Treat every section as provisional until a first Short has shipped and its review corrections are absorbed into `style.json` `learned` and this file.

Format: 9:16, 1080x1920, about 30 seconds (60 at most). Colours are tokens from brand.md (`$bg`, `$ink`, `$accent`...). Never hardcode hex. Voiceless like the long-form channel: the picture and the music carry it.

## What this look is

The same cream-paper warmth as the long-form videos, but the footage fills the whole vertical frame. One short hook card, then pure process.

## Structure (about 30 seconds)

| Part | Length | What it is |
|---|---|---|
| Hook | about 4 s | The most satisfying close-up at real speed, with the hook card over it. |
| Build | about 20 s | The whole piece sped up so it grows in one smooth run. |
| Reveal | about 6 s | The finished piece, real time. A real sound effect may land with the final gesture. |

## Framing

- Colour: phone footage is often HDR (HLG). Tone-map it to SDR bt709 before compositing, so the brand colours on the card match the tokens.
- Crop a full-height 9:16 window from the 4K source and keep the subject centred. Keyframe the crop so it follows the drawing when the paper moves.
- Never letterbox a 16:9 frame into the vertical canvas, and never stretch.
- Hard cuts only between parts. No transitions.

## Graphics: exactly one hook card

- Short form raw: one hook card, nothing else. No step cards, no stats.
- Key visuals stay inside y 200 to 1620 and 60 px from each side. The top 200 px and bottom 300 px are background only (platform interface lands there).
- Card: cream `$bg` panel with `$rule` border and an `$accent-soft` edge strip, matching the long-form cards.
- Headline: Fredoka SemiBold, `$ink`, at least 110 px, with one word in `$accent`. Sub-label: Nunito Black, `$muted`, letter-spaced, 36 px, with a `$rule` hairline that draws in under it.
- Entrance by width-mask reveal, 0.4 s stagger between elements. Holds at least 2.5 s of full text before it leaves.
- Place it where it does not cover the subject (the pencil tip and the part being drawn).

## Audio

- Music: user-supplied and cleared. Flat bed, no ducking, no fade-in, 1 s fade-out. If the track opens with silence, start it on its first note so there is sound from frame 0.
- Loudness: about -16 LUFS integrated with the true peak under -1.4 dBFS (see `style.json`). Measure the mix, apply one static gain, limit the peaks. Long-form videos sit near -28 LUFS, which is too quiet for a feed.
- Keep ambient craft sound on real-time segments only. Sped-up segments are music only.
- Sound effects: sparse, real cleared samples only (about -10 dB). Skip the step if there are none.

## Thumbnail cover

A 1080x1920 cover in the long-form thumbnail look: cream paper background with `$accent-soft` corners and grain, the finished piece large in a circle, the hook words above it inside the safe zone. YouTube may show a frame from the video instead of an uploaded cover for Shorts, so the first second of the video should also look good on its own.
