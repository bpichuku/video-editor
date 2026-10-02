# Brand: Priya / @EarthSkyAndCo

Art and craft channel. Long form 16:9. Mostly voiceless: music plus on-screen text carry the story, so text is the main storytelling tool.

## Colours

| Token | Hex | Role |
|---|---|---|
| bg | #FBF5E9 | Background base (cream paper) |
| rule | #E4D6BF | Thin lines, grid, hairlines |
| accent | #E8664A | The one loud colour (terracotta-coral) |
| accent-soft | #F6C9B8 | Quieter tint of accent, for gradients and decoration |
| ink | #3B2F2A | Dark title text (warm brown) |
| muted | #7E9A6C | Subheads and labels (sage green) |

```json
{
  "bg": "#FBF5E9",
  "rule": "#E4D6BF",
  "accent": "#E8664A",
  "accent-soft": "#F6C9B8",
  "ink": "#3B2F2A",
  "muted": "#7E9A6C"
}
```

## Fonts

- Display font: Fredoka (rounded, playful). File: `assets/fonts/Fredoka-Variable.ttf`. Titles, cards, stats, kinetic type.
- Caption font: Nunito Black (weight 900). File: `assets/fonts/Nunito-Variable.ttf`. Captions, body text, labels.

Both are SIL OFL, free to embed. Renders must load these files directly, never system fonts.

## Caption and text voice

Warm and chatty. Short friendly phrases, lowercase-friendly, like a friend narrating in the margins. Never corporate, never shouty.

## Default hook text

"Let's make something"

Used for the opening card when a video does not specify its own hook.

## Mishear list

As heard, then correct. Single-token pairs are auto-applied by the rough cut. Multi-token heard forms are review-only (they change the word count and would break downstream timestamps), so the rough cut flags them and the fix is applied by hand in the transcript text without touching timings.

| As heard | Correct | Auto-apply |
|---|---|---|
| earthsky | EarthSky | yes |
| pria | Priya | yes |
| preeya | Priya | yes |
| earth sky and co | EarthSkyAndCo | review only |
| earthsky and co | EarthSkyAndCo | review only |
| earth sky & co | EarthSkyAndCo | review only |
| pre ya | Priya | review only |
